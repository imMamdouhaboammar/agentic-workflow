#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════
  prompt_extractor.py — Deterministic Prompt Extractor
  
  Purpose: Completely prevent stochastic LLM behavior and extract,
           save, and verify prompts 100% mechanically using Python.
  
  Usage:
    python3 prompt_extractor.py extract   → Extract + Save + Verify
    python3 prompt_extractor.py verify    → Verify existing files only
    python3 prompt_extractor.py checksum  → Output MD5 checksums
═══════════════════════════════════════════════════════════════════
"""

import sys
import os
import re
import json
import hashlib
from pathlib import Path
from typing import List, Dict, Tuple


# ─── Configuration ──────────────────────────────────────────────
ORIGINAL_FILE = None  # Auto-detected at runtime
PROMPTS_DIR = None    # Auto-configured at runtime
MANIFEST_FILE = None


def find_original_file() -> str:
    """Auto-detect source markdown file"""
    candidates = [
        "/mnt/user-data/uploads/source_document.md",
        "./source.md",
        "./source_document.md",
    ]
    for c in candidates:
        if os.path.exists(c):
            return c
    # Search for .md files in current directory
    for f in Path(".").glob("*.md"):
        if f.name not in ("ANALYSIS.md", "README.md", "CLAUDE.md"):
            return str(f)
    raise FileNotFoundError("Could not find source markdown file.")


# ─── Core: Deterministic Code Block Extractor ────────────────────
def extract_code_blocks(filepath: str) -> List[Dict]:
    """
    Mechanically extracts code blocks from a markdown file.
    
    Rules (deterministic, no exceptions):
    1. 4-space indent + line starting with ```json or ```jsx = block start
    2. 4-space indent + line containing only ``` = block end
    3. All lines between start and end = block content (with strip() applied)
    4. Block indices start at 1, sequentially numbered in order of appearance
    """
    
    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()
    
    # Pattern definitions (compiled regexes — deterministic)
    OPEN_PATTERN = re.compile(r"^    ```(json|jsx)\s*$")
    CLOSE_PATTERN = re.compile(r"^    ```\s*$")
    
    blocks: List[Dict] = []
    in_block = False
    block_content_lines: List[str] = []
    block_start_line = 0
    block_lang = ""
    
    for line_num_0based, line in enumerate(lines):
        line_num = line_num_0based + 1  # 1-based
        
        if not in_block:
            m = OPEN_PATTERN.match(line)
            if m:
                in_block = True
                block_lang = m.group(1)
                block_start_line = line_num
                block_content_lines = []
        else:
            # Termination condition: line with only ```, and not a start pattern
            if CLOSE_PATTERN.match(line) and not OPEN_PATTERN.match(line):
                raw_content = "".join(block_content_lines)
                stripped = raw_content.strip()
                
                md5 = hashlib.md5(stripped.encode("utf-8")).hexdigest()
                sha256 = hashlib.sha256(stripped.encode("utf-8")).hexdigest()
                
                blocks.append({
                    "index": len(blocks) + 1,
                    "start_line": block_start_line,
                    "end_line": line_num,
                    "language": block_lang,
                    "content": stripped,
                    "char_count": len(stripped),
                    "byte_count": len(stripped.encode("utf-8")),
                    "md5": md5,
                    "sha256": sha256,
                    "is_clear": stripped == "/clear",
                })
                in_block = False
            else:
                block_content_lines.append(line)
    
    # Safety check: inspect unclosed blocks
    if in_block:
        raise RuntimeError(
            f"Fatal error: Code block starting at line {block_start_line} was not closed."
        )
    
    return blocks


# ─── Save Prompt Files ──────────────────────────────────────────
def save_prompt_files(blocks: List[Dict], output_dir: str) -> None:
    """Save each block as an individual text file"""
    
    os.makedirs(output_dir, exist_ok=True)
    
    for block in blocks:
        filename = f"{block['index']:03d}.txt"
        filepath = os.path.join(output_dir, filename)
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(block["content"])
    
    print(f"  ✅ Saved {len(blocks)} prompt files → {output_dir}/")


# ─── Generate Manifest ──────────────────────────────────────────
def save_manifest(blocks: List[Dict], filepath: str) -> None:
    """Save metadata for all blocks as JSON"""
    
    manifest = []
    for b in blocks:
        manifest.append({
            "file": f"{b['index']:03d}.txt",
            "index": b["index"],
            "start_line": b["start_line"],
            "end_line": b["end_line"],
            "language": b["language"],
            "is_clear": b["is_clear"],
            "char_count": b["char_count"],
            "byte_count": b["byte_count"],
            "md5": b["md5"],
            "sha256": b["sha256"],
        })
    
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
    
    print(f"  ✅ Manifest saved → {filepath}")


# ─── Verification: Compare Saved Files to Source ─────────────────
def verify_files(blocks: List[Dict], prompts_dir: str) -> Tuple[int, int, List[str]]:
    """
    Compares saved files byte-by-byte with source blocks.
    
    Returns:
        (matches_count, mismatches_count, error_messages_list)
    """
    
    matches = 0
    mismatches = 0
    errors: List[str] = []
    
    for block in blocks:
        filename = f"{block['index']:03d}.txt"
        filepath = os.path.join(prompts_dir, filename)
        
        # Check file existence
        if not os.path.exists(filepath):
            errors.append(f"#{block['index']:03d}: File not found ({filepath})")
            mismatches += 1
            continue
        
        # Read file contents
        with open(filepath, "r", encoding="utf-8") as f:
            saved_content = f.read()
        
        # Byte-by-byte comparison
        original = block["content"]
        
        if original == saved_content:
            # Double-check MD5
            saved_md5 = hashlib.md5(saved_content.encode("utf-8")).hexdigest()
            if saved_md5 == block["md5"]:
                matches += 1
            else:
                errors.append(
                    f"#{block['index']:03d}: String match but MD5 mismatch! "
                    f"(Source: {block['md5']}, Saved: {saved_md5})"
                )
                mismatches += 1
        else:
            # Detailed discrepancy analysis
            orig_bytes = len(original.encode("utf-8"))
            saved_bytes = len(saved_content.encode("utf-8"))
            saved_md5 = hashlib.md5(saved_content.encode("utf-8")).hexdigest()
            
            # Find first difference position
            first_diff = -1
            for j in range(min(len(original), len(saved_content))):
                if original[j] != saved_content[j]:
                    first_diff = j
                    break
            if first_diff == -1:
                first_diff = min(len(original), len(saved_content))
            
            errors.append(
                f"#{block['index']:03d}: Content mismatch!\n"
                f"       Source: {orig_bytes} bytes, MD5: {block['md5']}\n"
                f"       Saved:  {saved_bytes} bytes, MD5: {saved_md5}\n"
                f"       First difference at: Char #{first_diff}\n"
                f"       Source[{first_diff}:+20]: {repr(original[first_diff:first_diff+20])}\n"
                f"       Saved[{first_diff}:+20]:  {repr(saved_content[first_diff:first_diff+20])}"
            )
            mismatches += 1
    
    # Check for extra/missing files
    expected = set(f"{b['index']:03d}.txt" for b in blocks)
    actual = set(f for f in os.listdir(prompts_dir) if f.endswith(".txt"))
    extra = actual - expected
    missing = expected - actual
    
    if extra:
        errors.append(f"Extra files detected: {sorted(extra)}")
    if missing:
        errors.append(f"Missing files detected: {sorted(missing)}")
    
    return matches, mismatches, errors


# ─── Print Comprehensive Verification Report ────────────────────
def print_verification_report(
    blocks: List[Dict], 
    matches: int, 
    mismatches: int, 
    errors: List[str]
) -> bool:
    """Prints verification results and returns success status"""
    
    total = len(blocks)
    clear_count = sum(1 for b in blocks if b["is_clear"])
    exec_count = total - clear_count
    
    print()
    print("=" * 70)
    print("  Prompt Extraction Verification Report")
    print("=" * 70)
    print()
    print(f"  Total code blocks:    {total}")
    print(f"    Execution prompts:  {exec_count}")
    print(f"    /clear commands:    {clear_count}")
    print()
    print(f"  /clear locations:     {[b['index'] for b in blocks if b['is_clear']]}")
    print()
    print(f"  Verification results:")
    print(f"    ✅ Perfect matches: {matches}/{total}")
    print(f"    ❌ Mismatches:      {mismatches}/{total}")
    print()
    
    if errors:
        print("  Error Details:")
        for e in errors:
            for line in e.split("\n"):
                print(f"    {line}")
            print()
    
    if mismatches == 0 and matches == total:
        print("  ╔══════════════════════════════════════════════════╗")
        print(f"  ║  ✅ Verification Passed: {total} code blocks       ║")
        print("  ║     100% byte-for-byte identical                 ║")
        print("  ║     MD5 checksum double-verification passed      ║")
        print("  ╚══════════════════════════════════════════════════╝")
        print()
        return True
    else:
        print("  ╔══════════════════════════════════════════════════╗")
        print("  ║  ❌ Verification Failed: Discrepancies found     ║")
        print("  ║     Re-extraction with extract command required  ║")
        print("  ╚══════════════════════════════════════════════════╝")
        print()
        return False


# ─── Print Checksums ─────────────────────────────────────────────
def print_checksums(blocks: List[Dict]) -> None:
    """Prints checksums for all blocks (for external verification)"""
    
    print()
    print("=" * 90)
    print(f"  {'#':>3}  {'MD5':>32}  {'Bytes':>6}  {'Lines':>10}  {'Type':<8}")
    print("=" * 90)
    
    for b in blocks:
        btype = "/clear" if b["is_clear"] else b["language"]
        lines = f"L{b['start_line']}-L{b['end_line']}"
        print(f"  {b['index']:3d}  {b['md5']}  {b['byte_count']:6d}  {lines:>10}  {btype:<8}")
    
    # Composite hash (order-dependent)
    all_content = "\n===SEPARATOR===\n".join(b["content"] for b in blocks)
    total_md5 = hashlib.md5(all_content.encode("utf-8")).hexdigest()
    total_sha256 = hashlib.sha256(all_content.encode("utf-8")).hexdigest()
    
    print()
    print(f"  Composite MD5:    {total_md5}")
    print(f"  Composite SHA256: {total_sha256}")
    print()


# ─── Main ────────────────────────────────────────────────────────
def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python3 prompt_extractor.py extract [source.md] [output_dir]")
        print("  python3 prompt_extractor.py verify  [source.md] [prompts_dir]")
        print("  python3 prompt_extractor.py checksum [source.md]")
        sys.exit(1)
    
    command = sys.argv[1]
    
    # Source file path
    if len(sys.argv) >= 3:
        source_file = sys.argv[2]
    else:
        source_file = find_original_file()
    
    if not os.path.exists(source_file):
        print(f"❌ Source file not found: {source_file}")
        sys.exit(1)
    
    print(f"  Source file: {source_file}")
    
    # Extraction
    blocks = extract_code_blocks(source_file)
    print(f"  Extracted code blocks: {len(blocks)}")
    
    if command == "extract":
        output_dir = sys.argv[3] if len(sys.argv) >= 4 else "./prompts"
        manifest_file = os.path.join(os.path.dirname(output_dir), "manifest.json")
        
        # Save
        save_prompt_files(blocks, output_dir)
        save_manifest(blocks, manifest_file)
        
        # Verify immediately after saving
        matches, mismatches, errors = verify_files(blocks, output_dir)
        success = print_verification_report(blocks, matches, mismatches, errors)
        print_checksums(blocks)
        
        sys.exit(0 if success else 1)
    
    elif command == "verify":
        prompts_dir = sys.argv[3] if len(sys.argv) >= 4 else "./prompts"
        
        matches, mismatches, errors = verify_files(blocks, prompts_dir)
        success = print_verification_report(blocks, matches, mismatches, errors)
        
        sys.exit(0 if success else 1)
    
    elif command == "checksum":
        print_checksums(blocks)
        sys.exit(0)
    
    else:
        print(f"❌ Unknown command: {command}")
        print("   Available commands: extract, verify, checksum")
        sys.exit(1)


if __name__ == "__main__":
    main()
