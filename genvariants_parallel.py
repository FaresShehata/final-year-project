#!/usr/bin/env python3

import json
import random
import os
from typing import List
from argparse import ArgumentParser
from concurrent.futures import ThreadPoolExecutor, as_completed
import sys

from llm_provider import create_provider, HuggingFaceTGIProvider, LLMProvider


def continue_completion(text: str) -> tuple[str, str]:
    text_lines = text.split("\n")
    # Pick a random line number to cut at
    cut_line = len(text_lines)
    prompt_text = "\n".join(text_lines[:cut_line])
    real_completion = ""
    return prompt_text, real_completion


def random_completion(text: str, start_line: int = 1) -> tuple[str, str]:
    """Generate a completion of the text starting from a random line.
    Always include at least 1 line to avoid an empty prompt."""
    text_lines = text.split("\n")
    # Pick a random line number to cut at
    cut_line = (
        len(text_lines) - 2
        if start_line + 1 >= len(text_lines) - 1
        else random.randint(start_line + 1, len(text_lines) - 1)
    )
    prompt_text = "\n".join(text_lines[:cut_line])
    real_completion = "\n".join(text_lines[cut_line:])
    return prompt_text, real_completion


def random_fim(text: str, start_line: int = 1) -> tuple[str, str, str]:
    """Fill in the middle of the text with a random completion."""
    text_lines = text.split("\n")
    # Random start and end lines. Make sure we always have at least
    # one line in each section.
    fim_start_line = (
        len(text_lines) - 3
        if start_line + 1 >= len(text_lines) - 2
        else random.randint(start_line + 1, len(text_lines) - 2)
    )
    fim_end_line = random.randint(fim_start_line + 1, len(text_lines) - 1)
    prefix_text = "\n".join(text_lines[:fim_start_line]) + "\n"
    suffix_text = "\n".join(text_lines[fim_end_line:])
    real_middle = "\n".join(text_lines[fim_start_line:fim_end_line])
    return prefix_text, suffix_text, real_middle


def random_crossover(text1: str, text2: str, start_line: int = 1) -> tuple[str, str]:
    """Generate a splice of two texts."""

    text_lines1 = text1.split("\n")
    text_lines2 = text2.split("\n")

    common_prefix = 0
    for i in range(min(len(text_lines1), len(text_lines2))):
        if text_lines1[i] != text_lines2[i]:
            common_prefix = i - 1
            break

    cut_line1 = (
        len(text_lines1) - 2
        if start_line + 1 >= len(text_lines1) - 1
        else random.randint(start_line + 1, len(text_lines1) - 1)
    )

    may_overlap = min(cut_line1 - 1, common_prefix)

    cut_line2_start = max(may_overlap, start_line)

    cut_line2 = (
        len(text_lines2) - 2
        if cut_line2_start + 1 >= len(text_lines2) - 1
        else random.randint(cut_line2_start + 1, len(text_lines2) - 1)
    )
    prefix = "\n".join(text_lines1[:cut_line1])
    suffix = "\n".join(text_lines2[cut_line2:])
    return prefix, suffix


# SRCS = [
#     '/home/moyix/git/gifdec/gifdec.c',
# ]
# def random_snippet(text: str, start_line: int = 1) -> [str,str]:
#     """Include commented out code from the parser code."""
#     parser_chunks = open(random.choice(SRCS)).read().split('\n\n')

#     "# NOTE: the corresponding parser code in C is:\n#\n"


def new_base(filename: str) -> tuple[str, str]:
    # filename and extension
    base = os.path.basename(filename)
    base, ext = os.path.splitext(base)
    # Get the first occurrence (if any) of ".base_"
    first = base.find(".base_")
    if first == -1:
        return base, ext
    else:
        base = base[:first]
        return base, ext


def generate_variant(i, generators, model, filename, args):
    provider: LLMProvider = args.provider
    # Pick a random generator
    generator = random.choice(generators)
    if generator == "infilled":
        prefix, suffix, orig = random_fim(open(filename).read(), args.start_line)
        stop = []
    elif generator == "lmsplice":
        other_files = [f for f in args.files if f != filename]
        if other_files:
            filename2 = random.choice(other_files)
        else:
            filename2 = filename
        prefix, suffix = random_crossover(open(filename).read(), open(filename2).read(), args.start_line)
        orig = ""
        stop = []
    elif generator == "continue":
        assert False, "Continue not supported"
        prefix, orig = continue_completion(open(filename).read())
        suffix = ""
        stop = ["\nif", "\nclass", "\nfor", "\nwhile"]
    else:
        assert generator == "complete"
        prefix, orig = random_completion(open(filename).read(), args.start_line)
        suffix = ""
        stop = ["\nif", "\nclass", "\nfor", "\nwhile"]

    # Prepare metadata up front in case we fail to generate
    # filename and extension
    base, ext = new_base(filename)
    if generator == "lmsplice":
        base2, _ = new_base(filename2)
    else:
        base2 = base
    # Count lines
    plines = prefix.count("\n")
    slines = suffix.count("\n")
    olines = orig.count("\n")
    # Output filenames
    out_file = f"var_{i:04}.{generator}{ext}"
    out_path = os.path.join(args.output_dir, out_file)
    meta_file = os.path.join(args.log_dir, out_file + ".json")

    prompt = provider.build_prompt(generator, prefix, suffix)

    res = provider.generate_completion(
        prompt,
        stop=stop,
        **vars(args.gen),
    )
    if "generated_text" not in res:
        meta = {
            "model": model,
            "prompt": prompt,
            "generator": generator,
            "prompt_lines": plines,
            "orig_lines": olines,
            "gen_lines": 0,
            "suffix_lines": slines,
            "finish_reason": "err",
            "base": [base] + ([base2] if generator == "lmsplice" else []),
            "response": res,
        }

        # Write (error) metadata to logdir
        with open(meta_file, "w") as f:
            f.write(json.dumps(meta))

        return None

    # Fix up the generated text
    text = res["generated_text"]
    if isinstance(provider, HuggingFaceTGIProvider) and "codellama" in model:
        text = text.replace(" <EOT>", "")
        for stop_seq in stop:
            if text.endswith(stop_seq):
                text = text[: -len(stop_seq)]
    gen_lines = text.count("\n")

    # one of [length, eos_token, stop_sequence]
    finish_reason = res["details"]["finish_reason"]
    finish_reason = {
        "length": "len",
        "eos_token": "eos",
        "stop_sequence": "stp",
    }[finish_reason]
    meta = {
        "model": model,
        "prompt": prompt,
        "generator": generator,
        "prompt_lines": plines,
        "orig_lines": olines,
        "gen_lines": gen_lines,
        "suffix_lines": slines,
        "finish_reason": finish_reason,
        "base": [base] + ([base2] if generator == "lmsplice" else []),
        "response": res,
    }
    # Write output to file
    with open(out_path, "w") as f:
        f.write(prefix)
        f.write(text)
        f.write(suffix)

    # Write metadata to logdir
    with open(meta_file, "w") as f:
        f.write(json.dumps(meta))

    return out_path


def make_parser():
    parser = ArgumentParser(description="Use a code model to generate variants of a file.")
    parser.add_argument("files", type=str, nargs="+")
    parser.add_argument(
        "-M", "--model_name", type=str, default="codellama/CodeLlama-13b-hf", help="Model to use for generation"
    )
    parser.add_argument(
        "--backend",
        type=str,
        default=os.environ.get("ELMFUZZ_LLM_BACKEND", "huggingface"),
        choices=["huggingface", "copilot"],
        help="LLM backend to use for generation",
    )
    parser.add_argument("--no-completion", action="store_true", help="Disable the completion mutator")
    parser.add_argument("--no-fim", action="store_true", help="Disable the FIM (infilling) mutator")
    parser.add_argument("--no-splice", action="store_true", help="Disable the splice mutator")
    parser.add_argument(
        "-n", "--num_variants", type=int, default=1, help="Number of variants to generate for each seed"
    )
    parser.add_argument("-O", "--output_dir", type=str, default=".", help="Directory to write variants to")
    parser.add_argument("-L", "--log_dir", type=str, default="logs", help="Directory to write generation metadata to")
    parser.add_argument(
        "-s",
        "--start_line",
        type=int,
        default=0,
        help="When making random cuts, always start at this line. "
        + "Allows specifying an immutable region not subject to mutation.",
    )
    parser.add_argument("-j", "--jobs", type=int, default=16, help="Number of inference jobs to run in parallel")
    # Generation params
    parser.add_argument("-t", "--gen.temperature", type=float, default=0.2, help="Generation temperature")
    parser.add_argument(
        "-m", "--gen.max-new-tokens", type=int, default=2048, help="Maximum number of tokens to generate"
    )
    parser.add_argument("-r", "--gen.repetition-penalty", type=float, default=1.1, help="Repetition penalty")
    return parser


def init_parser(elm):
    # Add a bit of help text to the generation options
    elm.subgroup_help["gen"] = "Generation parameters"


def main():
    from elmconfig import ELMFuzzConfig

    config = ELMFuzzConfig(parents={"genvariants_parallel": make_parser()})
    init_parser(config)
    args = config.parse_args()

    if args.no_completion and args.no_fim and args.no_splice:
        config.parser.error(f"Nothing to do")

    os.makedirs(args.output_dir, exist_ok=True)
    os.makedirs(args.log_dir, exist_ok=True)

    access_info = on_nsf_access()
    endpoint = None
    if args.backend == "huggingface":
        if access_info is not None:
            endpoint = access_info["endpoint"]
        else:
            endpoint = args.model.endpoints.get(args.model_name)
            if endpoint is None:
                # Model-override path (e.g. --use-small-model): the configured
                # endpoint map doesn't include the override model. Fall back to
                # the first configured endpoint — that's the TGI server we
                # actually started.
                first = next(iter(args.model.endpoints.values()), None)
                if first is not None:
                    print(
                        f"INFO: no endpoint for model {args.model_name!r}; "
                        f"falling back to first configured endpoint {first}",
                        file=sys.stderr,
                    )
                    endpoint = first
                else:
                    print(f"WARNING: no endpoint for model {args.model_name}", file=sys.stderr)

    args.provider = create_provider(
        args.backend,
        model_id=args.model_name,
        endpoint=endpoint,
    )
    model = args.provider.model_id

    forbidden = os.environ.get("ELFUZZ_FORBIDDEN_MUTATORS", "").split(",")
    forbidden = [f.strip() for f in forbidden if f.strip()]

    generators = []
    if not args.no_completion or "complete" not in forbidden:
        generators += ["complete"]
    if not args.no_fim or "infilled" not in forbidden:
        generators += ["infilled"]
    if not args.no_splice or "lmsplice" not in forbidden:
        generators += ["lmsplice"]
    # generators += ['continue']

    # Print the number of variants we'll generate so that the next
    # stage (genoutputs) knows how many to expect.
    print(len(args.files) * args.num_variants, flush=True)

    worklist = []
    i = 0
    for _ in range(args.num_variants):
        for filename in args.files:
            worklist.append((i, filename))
            i += 1
    # pbar = tqdm(total=len(worklist), desc='Generating', unit='variant')
    with ThreadPoolExecutor(max_workers=args.jobs) as executor:
        futures = []
        for i, filename in worklist:
            future = executor.submit(generate_variant, i, generators, model, filename, args)
            # future.add_done_callback(lambda _: pbar.update())
            futures.append(future)
        # A single failed variant must not abort the whole generation (and with
        # it the multi-hour pipeline). The provider already retries/restarts on
        # transient backend failures; here we tolerate the few that still slip
        # through, and only bail if the backend looks truly unrecoverable
        # (a large and majority share of variants failing).
        completed = 0
        failures = 0
        for future in as_completed(futures):
            completed += 1
            try:
                res = future.result()
            except Exception as e:
                failures += 1
                print(
                    f"WARNING: variant generation failed ({failures} so far): "
                    f"{type(e).__name__}: {e}",
                    file=sys.stderr,
                    flush=True,
                )
                if failures >= 20 and failures > completed * 0.5:
                    print(
                        "ERROR: majority of variants failing; backend appears "
                        "unrecoverable, aborting generation",
                        file=sys.stderr,
                        flush=True,
                    )
                    raise
                continue
            if res is not None:
                print(res, flush=True)
    # pbar.close()


def on_nsf_access() -> dict[str, str] | None:
    if not "ACCESS_INFO" in os.environ:
        return None
    endpoint = os.environ["ACCESS_INFO"]
    return {"endpoint": endpoint}


if __name__ == "__main__":
    main()
