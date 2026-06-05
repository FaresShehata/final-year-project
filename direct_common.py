"""Shared helpers for `elfuzz direct` mode.

Used by `direct_initial.py` and `direct_mutate.py`. Keeps prompt construction
and post-processing in one place.
"""

from __future__ import annotations

import random
from typing import Any

from llm_provider import LLMProvider


COPILOT_STOP = ["\n```", "\nExplanation:", "\n\nNote:"]


# ---------------------------------------------------------------------------
# Copilot natural-language prompts (format-aware)
# ---------------------------------------------------------------------------


def copilot_initial_prompt(
    format_name: str, format_description: str, examples: list[str] | None = None
) -> str:
    base = (
        f"Generate a single example of {format_description} ({format_name}). "
        "Output only the resulting content. Do NOT include explanations, "
        "markdown fences, preamble, or postamble. Output the content and nothing else."
    )
    if examples:
        ex_block = "\n\n".join(f"Example:\n{e}" for e in examples)
        return f"{base}\n\n{ex_block}\n\nNow output a new, different example:"
    return base


def copilot_complete_prompt(format_name: str, format_description: str, prefix: str) -> str:
    return (
        f"Continue this {format_description} ({format_name}). "
        "Output only the continuation, no markdown, no explanation, "
        f"no preamble, no postamble.\n\n{prefix}"
    )


def copilot_infill_prompt(
    format_name: str, format_description: str, prefix: str, suffix: str
) -> str:
    return (
        f"Fill in the missing portion of this {format_description} ({format_name}). "
        "Output only the missing portion, no markdown, no explanation.\n\n"
        f"PREFIX:\n{prefix}\n\nSUFFIX:\n{suffix}\n\nMISSING:"
    )


def copilot_splice_prompt(
    format_name: str, format_description: str, prefix: str, suffix: str
) -> str:
    return (
        f"Combine these two {format_name} fragments into a single valid "
        f"{format_description}. Output only the result, no markdown, no explanation.\n\n"
        f"FRAGMENT A:\n{prefix}\n\nFRAGMENT B:\n{suffix}"
    )


# ---------------------------------------------------------------------------
# Backend dispatcher
# ---------------------------------------------------------------------------


def fewshot_delim(provider: LLMProvider) -> str:
    """Separator between few-shot examples (and the stop sequence for the
    generated one). Qwen2.5-Coder is pretrained with ``<|file_sep|>`` between
    files, so we reuse it; other models get a generic sentinel."""
    mid = getattr(provider, "model_id", "") or ""
    if "Qwen2.5-Coder" in mid:
        return "<|file_sep|>"
    return "\n<<<ELFUZZ_NEXT_INPUT>>>\n"


def build_direct_prompt(
    provider: LLMProvider,
    backend: str,
    op: str,
    prefix: str,
    suffix: str,
    fmt_name: str,
    fmt_desc: str,
    ext: str = "",
    examples: list[str] | None = None,
) -> str:
    """Build a prompt string for the given backend and operator.

    Operators: "initial", "complete", "infilled", "lmsplice". ``examples`` (real
    in-format inputs) few-shot-prime the "initial" op so the model knows what
    format to produce.
    """
    if backend == "copilot":
        if op == "initial":
            return copilot_initial_prompt(fmt_name, fmt_desc, examples)
        if op == "complete":
            return copilot_complete_prompt(fmt_name, fmt_desc, prefix)
        if op == "infilled":
            return copilot_infill_prompt(fmt_name, fmt_desc, prefix, suffix)
        if op == "lmsplice":
            return copilot_splice_prompt(fmt_name, fmt_desc, prefix, suffix)
        raise ValueError(f"unknown direct operator: {op!r}")

    # HuggingFace TGI: reuse the FIM-tokenised paths from synth.
    if op == "initial":
        if examples:
            mid = getattr(provider, "model_id", "") or ""
            if "Qwen2.5-Coder" in mid:
                # Qwen2.5-Coder repo-completion format. CRUCIAL: give every
                # few-shot example a `{ext}` filename so the model continues
                # with one MORE file of the SAME type. A bare <|file_sep|> with
                # no filename flips it into "generate arbitrary repo code" mode
                # -- it emits .cs/.php/.cpp files, not the target format. The
                # trailing prime starts the new file.
                name = (fmt_name or "input").lower().replace(" ", "_")
                parts = ["<|repo_name|>examples"]
                for i, ex in enumerate(examples):
                    parts.append(f"<|file_sep|>{name}_{i}{ext}\n{ex}")
                parts.append(f"<|file_sep|>{name}_{len(examples)}{ext}\n{prefix}")
                return "".join(parts)
            # Generic base model: plain-delimiter few-shot continuation.
            delim = fewshot_delim(provider)
            return delim.join(examples) + delim + prefix
        # No corpus: a lightweight format signal (from metadata) so a base code
        # model doesn't free-associate into other languages.
        return f"{fmt_desc} ({fmt_name}):\n{prefix}"
    if op == "complete":
        return prefix
    if op == "infilled":
        return provider.build_prompt("infilled", prefix, suffix)
    if op == "lmsplice":
        return provider.build_prompt("lmsplice", prefix, suffix)
    raise ValueError(f"unknown direct operator: {op!r}")


def stop_for(backend: str, op: str) -> list[str] | None:
    if backend == "copilot":
        return list(COPILOT_STOP)
    return None


def initial_stop(
    provider: LLMProvider, backend: str, examples: list[str] | None
) -> list[str] | None:
    """Stop sequence for initial-input generation: for HF few-shot, stop at the
    example delimiter so the model emits exactly one fresh input."""
    if backend == "copilot":
        return list(COPILOT_STOP)
    if examples:
        return [fewshot_delim(provider)]
    return None


def postprocess_copilot(text: str) -> str:
    """Strip markdown fences / leading & trailing whitespace from Copilot output."""
    s = text.strip()
    if s.startswith("```"):
        # drop the fence line (with or without language tag)
        if "\n" in s:
            s = s.split("\n", 1)[1]
        else:
            s = s[3:]
        if s.endswith("```"):
            s = s[: -3]
    return s.strip()


# ---------------------------------------------------------------------------
# Line-boundary cuts for mutation operators (byte-text equivalents of
# random_completion / random_fim / random_crossover from genvariants_parallel.py)
# ---------------------------------------------------------------------------


# Hard cap on parent text fed to the LLM. Without this, prefixes/suffixes
# grow unboundedly across generations: each gen N's outputs become parents
# for gen N+1, so prompts (and per-call latency) compound.
_PARENT_TEXT_CAP = 4096


def _cap(text: str) -> str:
    if len(text) <= _PARENT_TEXT_CAP:
        return text
    # Cut at the last newline within the cap so we don't slice mid-line.
    head = text[:_PARENT_TEXT_CAP]
    nl = head.rfind("\n")
    return head[: nl + 1] if nl > 0 else head


def random_complete_cut(text: str) -> str:
    """Return a prefix of *text* cut at a random line boundary.

    At least one line is preserved so the prompt is non-empty (when text has
    multiple lines).
    """
    text = _cap(text)
    lines = text.split("\n")
    if len(lines) <= 1:
        # Single-line input: cut mid-line at a random byte.
        if len(text) <= 1:
            return text
        cut = random.randint(1, len(text) - 1)
        return text[:cut]
    cut_line = random.randint(1, max(1, len(lines) - 1))
    return "\n".join(lines[:cut_line])


def random_fim_cut(text: str) -> tuple[str, str]:
    """Return (prefix, suffix) cuts of *text* at two random line boundaries."""
    text = _cap(text)
    lines = text.split("\n")
    if len(lines) <= 2:
        # Fall back to byte-level cut.
        if len(text) <= 2:
            return text, ""
        i = random.randint(1, len(text) - 2)
        j = random.randint(i + 1, len(text) - 1)
        return text[:i], text[j:]
    start = random.randint(1, len(lines) - 2)
    end = random.randint(start + 1, len(lines) - 1)
    return "\n".join(lines[:start]) + "\n", "\n".join(lines[end:])


def random_suffix_cut(text: str) -> str:
    """Return a suffix of *text* cut at a random line boundary."""
    text = _cap(text)
    lines = text.split("\n")
    if len(lines) <= 1:
        if len(text) <= 1:
            return text
        cut = random.randint(1, len(text) - 1)
        return text[cut:]
    cut_line = random.randint(1, max(1, len(lines) - 1))
    return "\n".join(lines[cut_line:])


def random_splice_cuts(text_a: str, text_b: str) -> tuple[str, str]:
    """Return (prefix from a, suffix from b) at random line boundaries."""
    return random_complete_cut(text_a), random_suffix_cut(text_b)
