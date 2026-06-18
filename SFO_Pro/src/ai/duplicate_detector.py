"""Duplicate file detection — hash-based and name similarity."""
from typing import List, Dict, Tuple
from collections import defaultdict
import difflib


def find_hash_duplicates(files: List[Dict]) -> List[List[Dict]]:
    """Group files with identical MD5 hashes (exact duplicates)."""
    hash_groups: Dict[str, List[Dict]] = defaultdict(list)
    for f in files:
        h = f.get("hash_md5")
        if h:
            hash_groups[h].append(f)
    return [grp for grp in hash_groups.values() if len(grp) > 1]


def find_name_duplicates(files: List[Dict], threshold: float = 0.85) -> List[Tuple[Dict, Dict]]:
    """Find pairs of files with very similar names (fuzzy match)."""
    pairs = []
    names = [(f["filename"], f) for f in files]
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            ratio = difflib.SequenceMatcher(
                None, names[i][0].lower(), names[j][0].lower()
            ).ratio()
            if ratio >= threshold:
                pairs.append((names[i][1], names[j][1], ratio))
    return pairs


def calculate_duplicate_savings(duplicate_groups: List[List[Dict]]) -> int:
    """Calculate bytes recoverable by deleting duplicates."""
    total = 0
    for grp in duplicate_groups:
        if len(grp) > 1:
            sizes = sorted([f.get("size_bytes", 0) for f in grp], reverse=True)
            # Keep one (largest), delete rest
            total += sum(sizes[1:])
    return total
