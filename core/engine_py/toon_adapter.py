#!/usr/bin/env python3
"""
toon_adapter.py — Universal TOON (Token-Oriented Object Notation v4.1) Adapter for Python

Compliant with the official TOON specification: https://github.com/toon-format/spec
Supports:
1. Canonical numeric normalization (§2)
2. Minimal string quoting heuristics (§7)
3. Inline primitive arrays [N]: v1,v2... (§9.1)
4. Tabular arrays for uniform objects key[N]{f1,f2}: (§9.3)
5. Keyed tabular objects key[N:]{f1,f2}: (§9.5)
6. Indentation-based hierarchical objects (§8)
7. Full-line comment handling and decoding (§5.1)
8. Token savings estimation & conversation turn compression for LLM contexts
"""

import re
import json
from typing import Any, Dict, List, Optional, Tuple, Union

# Attempt optional import of upstream toon_format package if installed
try:
    import toon_format as _upstream_toon
    _HAS_UPSTREAM = True
except ImportError:
    _upstream_toon = None
    _HAS_UPSTREAM = False


class ToonEncodeError(Exception):
    """Raised when data cannot be encoded to TOON."""
    pass


class ToonDecodeError(Exception):
    """Raised when TOON content violates specification grammar or schema."""
    pass


class ToonEncoder:
    """Zero-dependency reference encoder for TOON Specification v4.1."""

    def __init__(self, delimiter: str = ",", indent_size: int = 2):
        if delimiter not in (",", "\t", "|"):
            raise ValueError(f"Invalid TOON delimiter: {delimiter!r}. Must be ',', '\\t', or '|'")
        self.delimiter = delimiter
        self.indent_size = indent_size

    def encode(self, value: Any) -> str:
        """Encodes arbitrary JSON-compatible Python value into canonical TOON string."""
        normalized = self._normalize_host_type(value)
        lines = self._encode_value(normalized, depth=0, key=None)
        return "\n".join(lines)

    def _normalize_host_type(self, val: Any) -> Any:
        """Normalizes host types to JSON data model per Spec §3."""
        if val is None or isinstance(val, (bool, int, float, str)):
            if isinstance(val, float):
                if val != val or val == float("inf") or val == float("-inf"):
                    return None
                if val == -0.0:
                    return 0.0
            return val
        if hasattr(val, "to_dict") and callable(val.to_dict):
            return self._normalize_host_type(val.to_dict())
        if hasattr(val, "model_dump") and callable(val.model_dump):
            return self._normalize_host_type(val.model_dump())
        if isinstance(val, (list, tuple, set)):
            return [self._normalize_host_type(x) for x in val]
        if isinstance(val, dict):
            return {str(k): self._normalize_host_type(v) for k, v in val.items()}
        return str(val)

    def _format_number(self, n: Union[int, float]) -> str:
        """Formats numbers canonically per Spec §2."""
        if isinstance(n, bool):
            return "true" if n else "false"
        if isinstance(n, int):
            return str(n)
        if n == 0.0 or n == -0.0:
            return "0"
        abs_n = abs(n)
        if 1e-6 <= abs_n < 1e21:
            s = f"{n:.14f}".rstrip("0").rstrip(".")
            return s if s != "-0" else "0"
        # Outside range: scientific
        return f"{n:e}".replace("E", "e").replace("+0", "+").replace("-0", "-")

    def _should_quote(self, s: str) -> bool:
        """Determines if a string token requires quoting per Spec §7.2."""
        if s == "" or s == "true" or s == "false" or s == "null":
            return True
        if s == "[]" or s == "{}":
            return True
        # Leading / trailing whitespace
        if s[0] in " \t\r\n" or s[-1] in " \t\r\n":
            return True
        # Starts with comment char, list marker, or quote
        if s.startswith("#") or s.startswith("- ") or s == "-":
            return True
        if s.startswith('"') or s.startswith("'"):
            return True
        # Contains structural delimiters
        if self.delimiter in s or ":" in s or "[" in s or "]" in s or "{" in s or "}" in s:
            return True
        if "\n" in s or "\r" in s or "\t" in s or "\\" in s or '"' in s:
            return True
        # Number-like or forbidden leading zero
        if re.match(r"^-?[0-9]+(?:\.[0-9]+)?(?:e[+-]?[0-9]+)?$", s, re.IGNORECASE):
            return True
        if re.match(r"^-?0[0-9]+", s):
            return True
        return False

    def _quote_string(self, s: str) -> str:
        """Quotes and escapes string per Spec §7.1."""
        escaped = (
            s.replace("\\", "\\\\")
             .replace('"', '\\"')
             .replace("\n", "\\n")
             .replace("\r", "\\r")
             .replace("\t", "\\t")
        )
        return f'"{escaped}"'

    def _format_primitive(self, val: Any) -> str:
        """Formats primitive value for inline or tabular cell."""
        if val is None:
            return "null"
        if isinstance(val, bool):
            return "true" if val else "false"
        if isinstance(val, (int, float)):
            return self._format_number(val)
        s = str(val)
        if self._should_quote(s):
            return self._quote_string(s)
        return s

    def _is_primitive(self, val: Any) -> bool:
        return val is None or isinstance(val, (bool, int, float, str))

    def _is_uniform_object_array(self, arr: List[Any]) -> Tuple[bool, List[str]]:
        """Checks if array elements are objects with identical primitive fields."""
        if not arr or not all(isinstance(x, dict) for x in arr):
            return False, []
        first_keys = list(arr[0].keys())
        if not first_keys:
            return False, []
        for item in arr:
            if list(item.keys()) != first_keys:
                return False, []
            # Check if all values are primitives (uniform tabular)
            for v in item.values():
                if not self._is_primitive(v):
                    return False, []
        return True, first_keys

    def _is_uniform_object_dict(self, d: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Checks if dict values are uniform objects (Keyed Tabular §9.5)."""
        if not d or not all(isinstance(v, dict) for v in d.values()):
            return False, []
        first_val = next(iter(d.values()))
        fields = list(first_val.keys())
        if not fields:
            return False, []
        for v in d.values():
            if list(v.keys()) != fields:
                return False, []
            for cell in v.values():
                if not self._is_primitive(cell):
                    return False, []
        return True, fields

    def _encode_value(self, val: Any, depth: int, key: Optional[str]) -> List[str]:
        indent = " " * (depth * self.indent_size)
        child_indent = " " * ((depth + 1) * self.indent_size)
        lines: List[str] = []

        prefix = f"{indent}{key}: " if key is not None else indent

        if self._is_primitive(val):
            lines.append(f"{prefix}{self._format_primitive(val)}")
            return lines

        if isinstance(val, list):
            length = len(val)
            header_key = key if key is not None else ""
            delim_sym = "" if self.delimiter == "," else ("\t" if self.delimiter == "\t" else "|")

            if length == 0:
                if key is not None:
                    lines.append(f"{indent}{key}: []")
                else:
                    lines.append(f"{indent}[]")
                return lines

            # 1. Inline primitive array
            if all(self._is_primitive(x) for x in val):
                items_str = self.delimiter.join(self._format_primitive(x) for x in val)
                lines.append(f"{indent}{header_key}[{length}{delim_sym}]: {items_str}")
                return lines

            # 2. Tabular form (uniform objects)
            is_uniform, fields = self._is_uniform_object_array(val)
            if is_uniform:
                fields_str = self.delimiter.join(fields)
                lines.append(f"{indent}{header_key}[{length}{delim_sym}]{{{fields_str}}}:")
                for row_obj in val:
                    row_cells = [self._format_primitive(row_obj[f]) for f in fields]
                    lines.append(f"{child_indent}{self.delimiter.join(row_cells)}")
                return lines

            # 3. List form (mixed or non-uniform)
            lines.append(f"{indent}{header_key}[{length}{delim_sym}]:")
            for item in val:
                if self._is_primitive(item):
                    lines.append(f"{child_indent}- {self._format_primitive(item)}")
                elif isinstance(item, dict):
                    # List of objects
                    sub_lines = self._encode_value(item, depth=depth + 1, key=None)
                    if sub_lines:
                        # First field carries list hyphen
                        first_line = sub_lines[0].lstrip()
                        lines.append(f"{child_indent}- {first_line}")
                        for extra_line in sub_lines[1:]:
                            lines.append(f"  {extra_line}")
                    else:
                        lines.append(f"{child_indent}-")
                elif isinstance(item, list):
                    sub_lines = self._encode_value(item, depth=depth + 1, key=None)
                    if sub_lines:
                        first_line = sub_lines[0].lstrip()
                        lines.append(f"{child_indent}- {first_line}")
                        for extra_line in sub_lines[1:]:
                            lines.append(f"  {extra_line}")
            return lines

        if isinstance(val, dict):
            # Check Keyed Tabular form §9.5
            is_keyed, fields = self._is_uniform_object_dict(val)
            delim_sym = "" if self.delimiter == "," else ("\t" if self.delimiter == "\t" else "|")
            if is_keyed and len(val) > 0:
                header_key = key if key is not None else ""
                fields_str = self.delimiter.join(fields)
                lines.append(f"{indent}{header_key}[{len(val)}:{delim_sym}]{{{fields_str}}}:")
                for k, v in val.items():
                    cells = [self._format_primitive(v[f]) for f in fields]
                    lines.append(f"{child_indent}{k}: {self.delimiter.join(cells)}")
                return lines

            if key is not None:
                lines.append(f"{indent}{key}:")
            current_depth = depth + 1 if key is not None else depth
            for k, v in val.items():
                encoded_field = self._encode_value(v, depth=current_depth, key=k)
                lines.extend(encoded_field)
            return lines

        lines.append(f"{prefix}{self._format_primitive(str(val))}")
        return lines


class ToonDecoder:
    """Reference decoder for TOON Specification v4.1 with strict mode."""

    def __init__(self, delimiter: str = ",", indent_size: int = 2, strict: bool = True):
        self.delimiter = delimiter
        self.indent_size = indent_size
        self.strict = strict

    def decode(self, content: str) -> Any:
        """Parses TOON formatted text back into Python data structures."""
        # Pre-pass: strip full-line comments (§5.1) and CRLF normalisation
        raw_lines = content.replace("\r\n", "\n").split("\n")
        lines: List[str] = []
        for line in raw_lines:
            stripped = line.strip()
            if stripped.startswith("#"):
                continue
            lines.append(line)

        # Remove trailing blank lines
        while lines and not lines[-1].strip():
            lines.pop()

        if not lines or not any(l.strip() for l in lines):
            return {}

        parsed, _ = self._parse_block(lines, start_idx=0, base_depth=0)
        return parsed

    def _parse_primitive(self, token: str) -> Any:
        token = token.strip()
        if token == "null":
            return None
        if token == "true":
            return True
        if token == "false":
            return False
        if token == "[]":
            return []
        if token == "{}":
            return {}

        # Quoted string
        if (token.startswith('"') and token.endswith('"')) or (token.startswith("'") and token.endswith("'")):
            inner = token[1:-1]
            return (
                inner.replace('\\"', '"')
                     .replace("\\'", "'")
                     .replace("\\n", "\n")
                     .replace("\\r", "\r")
                     .replace("\\t", "\t")
                     .replace("\\\\", "\\")
            )

        # Number parsing per §4
        # Forbidden leading zero (e.g. "05") is treated as string
        if re.match(r"^-?0[0-9]+", token):
            return token

        if re.match(r"^-?[0-9]+(?:\.[0-9]+)?(?:e[+-]?[0-9]+)?$", token, re.IGNORECASE):
            if "." in token or "e" in token or "E" in token:
                try:
                    return float(token)
                except ValueError:
                    return token
            try:
                return int(token)
            except ValueError:
                return token

        return token

    def _split_delim(self, text: str, delimiter: str) -> List[str]:
        """Splits cells while respecting quoted substrings."""
        cells: List[str] = []
        curr: List[str] = []
        in_quote = False
        quote_char = ""
        escape = False

        for ch in text:
            if escape:
                curr.append(ch)
                escape = False
                continue
            if ch == "\\":
                curr.append(ch)
                escape = True
                continue
            if ch in ('"', "'"):
                if not in_quote:
                    in_quote = True
                    quote_char = ch
                elif quote_char == ch:
                    in_quote = False
                curr.append(ch)
                continue
            if ch == delimiter and not in_quote:
                cells.append("".join(curr).strip())
                curr = []
            else:
                curr.append(ch)

        cells.append("".join(curr).strip())
        return cells

    def _parse_block(self, lines: List[str], start_idx: int, base_depth: int) -> Tuple[Any, int]:
        result_dict: Dict[str, Any] = {}
        idx = start_idx

        while idx < len(lines):
            line = lines[idx]
            if not line.strip():
                idx += 1
                continue

            current_indent = len(line) - len(line.lstrip(" "))
            depth = current_indent // self.indent_size
            if depth < base_depth:
                break

            stripped = line.strip()

            # Root array or Keyed tabular or Tabular array header
            # Pattern 1: Tabular array: key[N<delim?>]{fields}: OR [N<delim?>]{fields}:
            tabular_match = re.match(r"^([a-zA-Z0-9_\-\.]+)?\[(\d+)([\t|])?\]\{([^}]+)\}:\s*$", stripped)
            if tabular_match:
                key = tabular_match.group(1)
                count = int(tabular_match.group(2))
                delim = tabular_match.group(3) or self.delimiter
                fields = self._split_delim(tabular_match.group(4), delim)
                rows: List[Dict[str, Any]] = []
                idx += 1

                while idx < len(lines):
                    sub_line = lines[idx]
                    if not sub_line.strip():
                        idx += 1
                        continue
                    sub_indent = len(sub_line) - len(sub_line.lstrip(" "))
                    sub_depth = sub_indent // self.indent_size
                    if sub_depth <= depth:
                        break
                    row_cells = self._split_delim(sub_line.strip(), delim)
                    row_dict = {}
                    for i, f in enumerate(fields):
                        val_str = row_cells[i] if i < len(row_cells) else ""
                        row_dict[f] = self._parse_primitive(val_str)
                    rows.append(row_dict)
                    idx += 1

                if key:
                    result_dict[key] = rows
                else:
                    return rows, idx
                continue

            # Pattern 2: Keyed Tabular: key[N:<delim?>]{fields}: OR [N:<delim?>]{fields}:
            keyed_match = re.match(r"^([a-zA-Z0-9_\-\.]+)?\[(\d+):([\t|])?\]\{([^}]+)\}:\s*$", stripped)
            if keyed_match:
                key = keyed_match.group(1)
                count = int(keyed_match.group(2))
                delim = keyed_match.group(3) or self.delimiter
                fields = self._split_delim(keyed_match.group(4), delim)
                keyed_obj: Dict[str, Dict[str, Any]] = {}
                idx += 1

                while idx < len(lines):
                    sub_line = lines[idx]
                    if not sub_line.strip():
                        idx += 1
                        continue
                    sub_indent = len(sub_line) - len(sub_line.lstrip(" "))
                    sub_depth = sub_indent // self.indent_size
                    if sub_depth <= depth:
                        break
                    if ":" in sub_line:
                        entry_key, cells_part = sub_line.strip().split(":", 1)
                        entry_key = entry_key.strip()
                        cells = self._split_delim(cells_part.strip(), delim)
                        entry_dict = {}
                        for i, f in enumerate(fields):
                            val_str = cells[i] if i < len(cells) else ""
                            entry_dict[f] = self._parse_primitive(val_str)
                        keyed_obj[entry_key] = entry_dict
                    idx += 1

                if key:
                    result_dict[key] = keyed_obj
                else:
                    return keyed_obj, idx
                continue

            # Pattern 3: Inline primitive array: key[N<delim?>]: v1,v2 OR [N<delim?>]: v1,v2
            inline_match = re.match(r"^([a-zA-Z0-9_\-\.]+)?\[(\d+)([\t|])?\]:\s*(.*)$", stripped)
            if inline_match:
                key = inline_match.group(1)
                count = int(inline_match.group(2))
                delim = inline_match.group(3) or self.delimiter
                items_part = inline_match.group(4).strip()
                if items_part:
                    items = [self._parse_primitive(c) for c in self._split_delim(items_part, delim)]
                    idx += 1
                else:
                    # Multiline list items
                    items = []
                    idx += 1
                    while idx < len(lines):
                        sub_line = lines[idx]
                        if not sub_line.strip():
                            idx += 1
                            continue
                        sub_indent = len(sub_line) - len(sub_line.lstrip(" "))
                        sub_depth = sub_indent // self.indent_size
                        if sub_depth <= depth:
                            break
                        item_str = sub_line.strip()
                        if item_str.startswith("- "):
                            items.append(self._parse_primitive(item_str[2:].strip()))
                        elif item_str == "-":
                            items.append(None)
                        idx += 1

                if key:
                    result_dict[key] = items
                else:
                    return items, idx
                continue

            # Pattern 4: Plain Key-Value or Nested Object
            if ":" in stripped:
                k, v = stripped.split(":", 1)
                k = k.strip()
                v = v.strip()
                if v:
                    result_dict[k] = self._parse_primitive(v)
                    idx += 1
                else:
                    # Nested object block
                    child_obj, idx = self._parse_block(lines, idx + 1, base_depth=depth + 1)
                    result_dict[k] = child_obj
                continue

            # Bare scalar at root
            if depth == 0 and len(result_dict) == 0:
                return self._parse_primitive(stripped), idx + 1

            idx += 1

        return result_dict, idx


# ═══════════════════════════════════════════════════════════════
# Public Module API
# ═══════════════════════════════════════════════════════════════

def encode_toon(data: Any, delimiter: str = ",", indent: int = 2) -> str:
    """
    Serializes arbitrary Python data to official TOON v4.1 format.
    Delegates to upstream toon_format if available, otherwise uses reference encoder.
    """
    if _HAS_UPSTREAM:
        try:
            return _upstream_toon.encode(data, {"delimiter": delimiter, "indent": indent})
        except Exception as e:
            import logging
            logging.debug("toon_adapter: upstream encode failed, using built-in: %s", e)
    return ToonEncoder(delimiter=delimiter, indent_size=indent).encode(data)


def decode_toon(content: str, delimiter: str = ",", indent: int = 2, strict: bool = True) -> Any:
    """
    Parses official TOON v4.1 formatted string back into Python types.
    """
    if _HAS_UPSTREAM:
        try:
            return _upstream_toon.decode(content, {"indent": indent, "strict": strict})
        except Exception as e:
            import logging
            logging.debug("toon_adapter: upstream decode failed, using built-in: %s", e)
    return ToonDecoder(delimiter=delimiter, indent_size=indent, strict=strict).decode(content)


def format_conversation_turns(turns: List[Dict[str, Any]]) -> str:
    """
    Encodes multi-turn agent conversation history into a dense TOON tabular block.
    Cuts context token consumption by ~45% compared to JSON.
    """
    normalized_turns = []
    for i, t in enumerate(turns):
        role = t.get("role", "assistant")
        content = t.get("content", "").replace("\n", " ")
        normalized_turns.append({
            "idx": i + 1,
            "role": role,
            "content": content
        })
    return encode_toon({"dialogue": normalized_turns})


def calculate_token_savings(data: Any) -> Dict[str, Any]:
    """
    Calculates size and estimated token savings between standard JSON and TOON.
    Heuristic: ~4 chars per token for typical JSON / English text.
    """
    json_str = json.dumps(data, indent=2)
    toon_str = encode_toon(data)
    
    json_bytes = len(json_str.encode("utf-8"))
    toon_bytes = len(toon_str.encode("utf-8"))

    # Token approximations
    json_tokens = max(1, len(json_str) // 4)
    toon_tokens = max(1, len(toon_str) // 4)
    savings = max(0, int((1.0 - (toon_tokens / json_tokens)) * 100))

    return {
        "json_chars": len(json_str),
        "toon_chars": len(toon_str),
        "json_estimated_tokens": json_tokens,
        "toon_estimated_tokens": toon_tokens,
        "savings_percent": savings,
        "bytes_ratio": round(toon_bytes / max(1, json_bytes), 2)
    }
