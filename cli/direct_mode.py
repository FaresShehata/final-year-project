"""LLM-direct input synthesis ("elfuzz direct" command).

This is a sibling to `synthesize_fuzzer` in pre_experiments.py, but instead of
evolving Python fuzzer programs the LLM produces inputs directly. The unit of
selection is a *collection* of inputs (a directory); coverage is the union over
all inputs in the collection; selection uses the same Pareto-by-superset rule
as `select_seeds.py`.
"""

import os
import select
import shutil
import subprocess
import sys
import tempfile
import threading
from datetime import datetime

import click

from common import PROJECT_ROOT, USER, UID


DIRECT_FORMAT_METADATA = {
    "jsoncpp": {
        "format_name": "JSON",
        "format_description": "valid JSON document",
        "input_extension": ".json",
        "hf_initial_prefix": "",
    },
    "libxml2": {
        "format_name": "XML",
        "format_description": "valid XML document",
        "input_extension": ".xml",
        "hf_initial_prefix": "<?xml version=\"1.0\"?>\n",
    },
    "re2": {
        "format_name": "regex",
        "format_description": "valid POSIX regular expression",
        "input_extension": ".re",
        "hf_initial_prefix": "",
    },
    "librsvg": {
        "format_name": "SVG",
        "format_description": "valid SVG document",
        "input_extension": ".svg",
        "hf_initial_prefix": "<?xml version=\"1.0\"?>\n",
    },
    "cvc5": {
        "format_name": "SMT-LIB v2",
        "format_description": "valid SMT-LIB v2 script",
        "input_extension": ".smt2",
        "hf_initial_prefix": "",
    },
    "sqlite3": {
        "format_name": "SQL",
        "format_description": "valid SQLite SQL script",
        "input_extension": ".sql",
        "hf_initial_prefix": "",
    },
    "cpython3": {
        "format_name": "Python",
        "format_description": "valid Python 3 source file",
        "input_extension": ".py",
        "hf_initial_prefix": "",
    },
}

DEFAULT_INPUTS_PER_COLLECTION = 50
DEFAULT_NUM_INITIAL_COLLECTIONS = 20
DEFAULT_NUM_VARIANTS = 20

OUTPUT_FUZZER_NAME = "elfuzz_direct"


def synthesize_direct(
    benchmark,
    *,
    tgi_waiting=1200,
    evolution_iterations=50,
    use_small_model=False,
    llm_backend="huggingface",
):
    if benchmark not in DIRECT_FORMAT_METADATA:
        raise ValueError(f"benchmark {benchmark!r} not supported by direct mode")
    fmt = DIRECT_FORMAT_METADATA[benchmark]

    env = os.environ.copy() | {
        "ELFUZZ_DIRECT_FORMAT_NAME": fmt["format_name"],
        "ELFUZZ_DIRECT_FORMAT_DESCRIPTION": fmt["format_description"],
        "ELFUZZ_DIRECT_INPUT_EXTENSION": fmt["input_extension"],
        "ELFUZZ_DIRECT_HF_INITIAL_PREFIX": fmt["hf_initial_prefix"],
        "ELFUZZ_DIRECT_INPUTS_PER_COLLECTION": str(DEFAULT_INPUTS_PER_COLLECTION),
        "ELFUZZ_DIRECT_NUM_INITIAL_COLLECTIONS": str(DEFAULT_NUM_INITIAL_COLLECTIONS),
        "ELFUZZ_DIRECT_NUM_VARIANTS": str(DEFAULT_NUM_VARIANTS),
        # Reuse the same selection knob as synth's lattice mode:
        "SELECTION_STRATEGY": "lattice",
        "ELFUZZ_FORBIDDEN_MUTATORS": "",
    }

    tgi_p = None
    if llm_backend == "huggingface":
        cmd_tgi = [
            "sudo",
            os.path.join(
                PROJECT_ROOT,
                "start_tgi_servers.sh" if not use_small_model else "start_tgi_servers_debug.sh",
            ),
        ]
        click.echo(
            "Starting the text-generation-inference server. This may take a while as it has to download the model..."
        )
        tgi_p = subprocess.Popen(
            " ".join(cmd_tgi),
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
            cwd=PROJECT_ROOT,
            user=USER,
            text=True,
        )
        start = datetime.now()
        print(f"TGI server started at {start}.", flush=True)
        poll_obj = select.poll()
        assert tgi_p.stdout is not None
        poll_obj.register(tgi_p.stdout, select.POLLIN)
        while True:
            if tgi_p.poll() is not None:
                print("TGI server failed to start.", flush=True)
                print("stderr:", flush=True)
                print(tgi_p.stderr.read(), flush=True)  # type: ignore
                print("stdout:", flush=True)
                print(tgi_p.stdout.read(), flush=True)  # type: ignore
                raise RuntimeError("TGI server failed to start.")
            if (datetime.now() - start).total_seconds() > tgi_waiting:
                break
            if poll_obj.poll(20):
                line = tgi_p.stdout.readline().strip()
                if line:
                    print(line, flush=True)
        click.echo("Text-generation-inference server started.")

        # CRITICAL: keep draining stdout/stderr for the remainder of the run.
        # TGI logs a few lines per request; if we stop reading, the OS pipe
        # buffer (~64KB) fills, TGI blocks on its next write(), and the whole
        # server stalls — every in-flight request hangs.
        # We discard the bytes silently (TGI is too chatty to forward).
        def _drain(stream):
            try:
                while stream.read(4096):
                    pass
            except Exception:
                pass

        threading.Thread(target=_drain, args=(tgi_p.stdout,), daemon=True).start()
        threading.Thread(target=_drain, args=(tgi_p.stderr,), daemon=True).start()

    try:
        rundir = os.path.join("preset", benchmark)

        run_cmd = [
            "sudo",
            "env",
            f"ELMFUZZ_LLM_BACKEND={llm_backend}",
            "REPROUDCE_MODE=true",
            f"NUM_GENERATIONS={evolution_iterations}",
            f"ELFUZZ_DIRECT_FORMAT_NAME={fmt['format_name']}",
            f"ELFUZZ_DIRECT_FORMAT_DESCRIPTION={fmt['format_description']}",
            f"ELFUZZ_DIRECT_INPUT_EXTENSION={fmt['input_extension']}",
            f"ELFUZZ_DIRECT_HF_INITIAL_PREFIX={fmt['hf_initial_prefix']}",
            f"ELFUZZ_DIRECT_INPUTS_PER_COLLECTION={DEFAULT_INPUTS_PER_COLLECTION}",
            f"ELFUZZ_DIRECT_NUM_INITIAL_COLLECTIONS={DEFAULT_NUM_INITIAL_COLLECTIONS}",
            f"ELFUZZ_DIRECT_NUM_VARIANTS={DEFAULT_NUM_VARIANTS}",
        ]
        if use_small_model and llm_backend == "huggingface":
            run_cmd.append("ELFUZZ_DIRECT_HF_MODEL_OVERRIDE=Qwen/Qwen2.5-Coder-1.5B")
        run_cmd += [
            os.path.join(PROJECT_ROOT, "all_gen_direct.sh"),
            rundir,
        ]
        # Run without shell=True so spaces in env-var values (e.g. "valid JSON
        # document") are preserved as a single argument, instead of being split
        # by the shell and confusing `env`.
        print(f"Running command: {run_cmd!r}", flush=True)
        subprocess.run(
            run_cmd,
            check=True,
            user=USER,
            cwd=PROJECT_ROOT,
            stdout=sys.stdout,
            stderr=sys.stderr,
        )

        _package_outputs(benchmark, rundir, evolution_iterations, fmt)
        click.echo(f"Direct-mode synthesis for {benchmark} completed.")
    finally:
        if tgi_p is not None:
            subprocess.run(
                ["sudo", "docker", "stop", "tgi-server"],
                check=False,
                cwd=PROJECT_ROOT,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )


def _package_outputs(benchmark, rundir, evolution_iterations, fmt):
    """Bundle the final-gen elite collections into the seed-tarball path used by
    `elfuzz produce` so that downstream rq commands can consume them.
    """
    last_gen = f"gen{evolution_iterations}"
    final_dir = os.path.join(PROJECT_ROOT, rundir, last_gen, "seeds")
    if not os.path.isdir(final_dir):
        click.echo(f"WARNING: expected final seeds dir {final_dir} not found", err=True)
        return

    datesuffix = datetime.now().strftime("%y%m%d")
    inside_name = f"{benchmark}_{OUTPUT_FUZZER_NAME}"

    # 1. Flat seed tarball at extradata/seeds/raw/{benchmark}/elfuzz_direct/{date}.tar.zst
    raw_dir = os.path.join(PROJECT_ROOT, "extradata", "seeds", "raw", benchmark, OUTPUT_FUZZER_NAME)
    os.makedirs(raw_dir, exist_ok=True)

    with tempfile.TemporaryDirectory() as tmpdir_raw:
        flat_dir = os.path.join(tmpdir_raw, inside_name, "seeds")
        os.makedirs(flat_dir, exist_ok=True)
        for collection_name in os.listdir(final_dir):
            coll_path = os.path.join(final_dir, collection_name)
            if not os.path.isdir(coll_path):
                continue
            for input_file in os.listdir(coll_path):
                src = os.path.join(coll_path, input_file)
                if not os.path.isfile(src):
                    continue
                dst = os.path.join(flat_dir, f"{collection_name}__{input_file}")
                shutil.copy(src, dst)
        seed_tar = os.path.join(raw_dir, f"{datesuffix}.tar.zst")
        subprocess.run(
            ["tar", "--zstd", "-cf", seed_tar, "-C", tmpdir_raw, inside_name],
            check=True,
        )
        click.echo(f"Wrote seed tarball: {seed_tar}")

    # 2. Full evolution record (mirrors synth at pre_experiments.py:296-303)
    evolution_record_dir = os.path.join(
        PROJECT_ROOT, "extradata", "evolution_record", OUTPUT_FUZZER_NAME
    )
    os.makedirs(evolution_record_dir, exist_ok=True)
    for old in os.listdir(evolution_record_dir):
        try:
            os.remove(os.path.join(evolution_record_dir, old))
        except OSError:
            pass
    evo_tar = os.path.join(evolution_record_dir, "evolution.tar.xz")
    subprocess.run(
        ["tar", "-cJf", evo_tar, rundir],
        check=True,
        cwd=PROJECT_ROOT,
    )
    click.echo(f"Wrote evolution record: {evo_tar}")
