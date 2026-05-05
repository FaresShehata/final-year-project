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


def copilot_initial_prompt(format_name: str, format_description: str) -> str:
    return (
        f"Generate a single example of {format_description} ({format_name}). "
        "Output only the resulting content. Do NOT include explanations, "
        "markdown fences, preamble, or postamble. Output the content and nothing else."
    )


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


def build_direct_prompt(
    provider: LLMProvider,
    backend: str,
    op: str,
    prefix: str,
    suffix: str,
    fmt_name: str,
    fmt_desc: str,
) -> str:
    """Build a prompt string for the given backend and operator.

    Operators: "initial", "complete", "infilled", "lmsplice".
    """
    if backend == "copilot":
        if op == "initial":
            return copilot_initial_prompt(fmt_name, fmt_desc)
        if op == "complete":
            return copilot_complete_prompt(fmt_name, fmt_desc, prefix)
        if op == "infilled":
            return copilot_infill_prompt(fmt_name, fmt_desc, prefix, suffix)
        if op == "lmsplice":
            return copilot_splice_prompt(fmt_name, fmt_desc, prefix, suffix)
        raise ValueError(f"unknown direct operator: {op!r}")

    # HuggingFace TGI: reuse the FIM-tokenised paths from synth.
    if op == "initial":
        return prefix
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
