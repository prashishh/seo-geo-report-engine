"""Dependency-free YAML reader for the subset used by this framework.

Supports: block maps, block sequences, lists-of-maps, inline flow sequences
[a, b, c] and flow maps {k: v}, comments, quoted strings, and scalar coercion
(int / float / bool / null). PyYAML is used automatically when installed; this is
the zero-install fallback so `client.yml` stays human-friendly without `pip`.

Keep framework.yml / client.yml within this subset (no anchors, no multiline
block scalars). The CLI self-tests this on `./bin/mkt selftest`.
"""
from __future__ import annotations

import json


def safe_load(text):
    stripped = text.lstrip()
    if stripped.startswith(("{", "[")):
        try:
            return json.loads(text)
        except Exception:
            pass
    try:
        import yaml  # prefer the real thing when present
        return yaml.safe_load(text)
    except Exception:
        pass
    items = []
    for raw in text.split("\n"):
        s = _strip_comment(raw)
        if not s.strip():
            continue
        indent = len(s) - len(s.lstrip(" "))
        items.append([indent, s.strip()])
    if not items:
        return None
    val, _ = _parse(items, 0, items[0][0])
    return val


def _parse(items, i, indent):
    if items[i][1].startswith("- "):
        return _parse_seq(items, i, indent)
    return _parse_map(items, i, indent)


def _parse_map(items, i, indent):
    d = {}
    while i < len(items):
        ind, text = items[i]
        if ind < indent or text.startswith("- "):
            break
        if ind > indent:  # stray deeper line; skip defensively
            i += 1
            continue
        key, _, rest = text.partition(":")
        key, rest = key.strip(), rest.strip()
        if rest == "":
            j = i + 1
            if j < len(items) and items[j][0] > indent:
                child, i = _parse(items, j, items[j][0])
                d[key] = child
            else:
                d[key] = None
                i = j
        else:
            d[key] = _scalar(rest)
            i += 1
    return d, i


def _parse_seq(items, i, indent):
    arr = []
    while i < len(items):
        ind, text = items[i]
        if ind != indent or not text.startswith("- "):
            break
        inner = text[2:].strip()
        cind = indent + 2
        items[i] = [cind, inner]
        if inner.startswith("- "):
            val, i = _parse_seq(items, i, cind)
            arr.append(val)
        elif _is_map_line(inner):
            val, i = _parse_map(items, i, cind)
            arr.append(val)
        else:
            arr.append(_scalar(inner))
            i += 1
    return arr, i


def _is_map_line(s):
    head = s.split(":", 1)[0]
    return ":" in s and head and " " not in head.strip() and not s.startswith(("[", "{", '"', "'"))


def _strip_comment(raw):
    out, q = [], None
    for ch in raw:
        if q:
            out.append(ch)
            if ch == q:
                q = None
        elif ch in "\"'":
            q = ch
            out.append(ch)
        elif ch == "#":
            break
        else:
            out.append(ch)
    return "".join(out).rstrip()


def _split_flow(s):
    parts, depth, q, cur = [], 0, None, []
    for ch in s:
        if q:
            cur.append(ch)
            if ch == q:
                q = None
        elif ch in "\"'":
            q = ch
            cur.append(ch)
        elif ch in "[{":
            depth += 1
            cur.append(ch)
        elif ch in "]}":
            depth -= 1
            cur.append(ch)
        elif ch == "," and depth == 0:
            parts.append("".join(cur).strip())
            cur = []
        else:
            cur.append(ch)
    if "".join(cur).strip():
        parts.append("".join(cur).strip())
    return parts


def _scalar(s):
    s = s.strip()
    if s == "" or s in ("~", "null", "Null", "NULL"):
        return None
    if len(s) >= 2 and s[0] == '"' and s[-1] == '"':
        return s[1:-1].replace('\\"', '"').replace("\\n", "\n")
    if len(s) >= 2 and s[0] == "'" and s[-1] == "'":
        return s[1:-1].replace("''", "'")
    if s.startswith("[") and s.endswith("]"):
        inner = s[1:-1].strip()
        return [_scalar(x) for x in _split_flow(inner)] if inner else []
    if s.startswith("{") and s.endswith("}"):
        inner = s[1:-1].strip()
        d = {}
        if inner:
            for part in _split_flow(inner):
                k, _, v = part.partition(":")
                d[k.strip()] = _scalar(v.strip())
        return d
    low = s.lower()
    if low in ("true", "yes", "on"):
        return True
    if low in ("false", "no", "off"):
        return False
    try:
        return int(s)
    except ValueError:
        pass
    try:
        return float(s)
    except ValueError:
        pass
    return s
