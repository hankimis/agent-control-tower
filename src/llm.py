"""Unified, cached chat wrappers for OpenAI + Anthropic.

Routes by model name (gpt-* -> OpenAI, claude-* -> Anthropic). Disk-cached on the
full request (plus a non-transmitted `salt`) so a re-run reproduces the same
generations and is cheap to re-render, even at temperature > 0.
"""
from __future__ import annotations

import hashlib
import json
import os
import time
from pathlib import Path

_CACHE = Path(__file__).resolve().parent.parent / "results" / "_cache"
_CACHE.mkdir(parents=True, exist_ok=True)

_oai = None
_ant = None


def _openai():
    global _oai
    if _oai is None:
        from openai import OpenAI
        key = os.environ.get("OPENAI_API_KEY")
        if not key:
            raise RuntimeError("OPENAI_API_KEY not set")
        _oai = OpenAI(api_key=key)
    return _oai


def _anthropic():
    global _ant
    if _ant is None:
        import anthropic
        key = os.environ.get("ANTHROPIC_API_KEY")
        if not key:
            raise RuntimeError("ANTHROPIC_API_KEY not set")
        _ant = anthropic.Anthropic(api_key=key)
    return _ant


def _path(payload: dict) -> Path:
    h = hashlib.sha256(json.dumps(payload, sort_keys=True, ensure_ascii=False).encode()).hexdigest()[:24]
    return _CACHE / f"chat_{h}.json"


def chat(model: str, system: str, user: str, temperature: float = 1.0, max_tokens: int = 600, salt: str = "") -> str:
    """One-shot system+user chat. `salt` enters the cache key only (not the API call)."""
    payload = {"model": model, "system": system, "user": user, "temperature": temperature,
               "max_tokens": max_tokens, "salt": salt}
    cp = _path(payload)
    if cp.exists():
        return json.loads(cp.read_text())["text"]
    for attempt in range(9):
        try:
            if model.startswith("gpt") or model.startswith("o1") or model.startswith("o3"):
                msgs = ([{"role": "system", "content": system}] if system else []) + [{"role": "user", "content": user}]
                r = _openai().chat.completions.create(model=model, messages=msgs,
                                                       temperature=temperature, max_tokens=max_tokens)
                text = r.choices[0].message.content.strip()
            elif model.startswith("claude"):
                kw = {"model": model, "max_tokens": max_tokens, "temperature": temperature,
                      "messages": [{"role": "user", "content": user}]}
                if system:
                    kw["system"] = system
                r = _anthropic().messages.create(**kw)
                text = r.content[0].text.strip()
            else:
                raise ValueError(f"unknown model {model}")
            cp.write_text(json.dumps({"text": text, "payload": payload}, ensure_ascii=False))
            return text
        except Exception as e:  # noqa: BLE001 - transient API errors
            wait = min(45, 2 ** attempt)
            print(f"  [retry {attempt+1} {model}: {type(e).__name__}; sleep {wait}s]")
            time.sleep(wait)
    raise RuntimeError(f"chat failed after retries: {model}")
