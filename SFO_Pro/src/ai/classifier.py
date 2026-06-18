"""AI File Classifier — keyword + NLP heuristic model (no external API required)."""
import re
from pathlib import Path
from typing import Dict, List, Tuple

# ── Keyword rules ──────────────────────────────────────────────────────────────
CATEGORY_KEYWORDS: Dict[str, List[str]] = {
    "Education": [
        "assignment", "homework", "lecture", "notes", "study", "exam",
        "quiz", "syllabus", "course", "university", "college", "school",
        "semester", "thesis", "dissertation", "tutorial", "lab", "research",
        "textbook", "essay", "academic",
    ],
    "Business": [
        "report", "invoice", "contract", "proposal", "budget", "finance",
        "meeting", "agenda", "presentation", "client", "company", "project",
        "strategy", "annual", "quarterly", "revenue", "profit", "expense",
        "statement", "tax", "payroll", "hr", "employee",
    ],
    "Personal": [
        "photo", "vacation", "holiday", "birthday", "family", "wedding",
        "travel", "trip", "memories", "personal", "diary", "journal",
        "receipt", "id", "passport", "certificate", "resume", "cv",
    ],
    "Creative": [
        "design", "artwork", "logo", "banner", "poster", "illustration",
        "sketch", "draft", "mockup", "wireframe", "ui", "ux", "template",
        "font", "icon", "graphic", "animation",
    ],
    "Development": [
        "code", "source", "script", "project", "app", "software", "build",
        "config", "setup", "deploy", "debug", "test", "readme", "api",
        "backend", "frontend", "database", "migration",
    ],
    "Media": [
        "movie", "film", "series", "episode", "music", "song", "album",
        "podcast", "video", "clip", "recording", "soundtrack",
    ],
}

TAG_KEYWORDS: Dict[str, List[str]] = {
    "important":   ["final", "important", "urgent", "critical", "asap"],
    "draft":       ["draft", "wip", "work-in-progress", "temp", "tmp"],
    "archive":     ["archive", "backup", "old", "2020", "2021", "2022", "legacy"],
    "template":    ["template", "boilerplate", "sample", "example"],
    "confidential":["confidential", "private", "secret", "nda", "sensitive"],
}


def _tokenize(name: str) -> List[str]:
    """Split filename into lowercase tokens."""
    name = Path(name).stem.lower()
    tokens = re.split(r"[\s_\-\.]+", name)
    return tokens


def classify_by_name(filename: str) -> Tuple[str, float]:
    """Return (category, confidence) based on filename keywords."""
    tokens = _tokenize(filename)
    scores: Dict[str, int] = {cat: 0 for cat in CATEGORY_KEYWORDS}

    for cat, kws in CATEGORY_KEYWORDS.items():
        for kw in kws:
            if kw in tokens or any(kw in t for t in tokens):
                scores[cat] += 1

    best_cat = max(scores, key=scores.get)
    best_score = scores[best_cat]
    total = sum(scores.values()) or 1
    confidence = round(best_score / total, 2) if best_score > 0 else 0.0

    if best_score == 0:
        return ("Uncategorized", 0.0)
    return (best_cat, min(confidence * 2, 1.0))


def generate_tags(filename: str) -> List[str]:
    """Auto-generate tags based on filename."""
    tokens = _tokenize(filename)
    tags = []
    for tag, kws in TAG_KEYWORDS.items():
        for kw in kws:
            if kw in tokens or any(kw in t for t in tokens):
                tags.append(tag)
                break

    # Year tag
    year_match = re.search(r"\b(20\d{2})\b", filename)
    if year_match:
        tags.append(year_match.group(1))

    return list(set(tags))


def generate_summary(filename: str, file_type: str, size_bytes: int) -> str:
    """Generate a plain-English summary for a file."""
    cat, conf = classify_by_name(filename)
    size_str = _human_size(size_bytes)
    confidence_str = f"{int(conf*100)}%"

    summary = (
        f"This {file_type} file ({size_str}) appears to be related to "
        f"{cat} based on its name. "
        f"AI confidence: {confidence_str}."
    )

    tags = generate_tags(filename)
    if tags:
        summary += f" Suggested tags: {', '.join(tags)}."

    return summary


def _human_size(size_bytes: int) -> str:
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"


def natural_language_search(query: str, files: List[Dict]) -> List[Dict]:
    """
    Simple NLP search — maps natural language intent to file filters.
    Example: "my AI assignments from last semester"
    → category=Education, tags=assignment, recent=True
    """
    query_lower = query.lower()
    tokens = re.split(r"\s+", query_lower)

    results = []
    for f in files:
        score = 0
        name = (f.get("filename") or "").lower()
        cat  = (f.get("category") or "").lower()
        ai_sum = (f.get("ai_summary") or "").lower()
        tags = (f.get("tags") or "").lower()

        for token in tokens:
            if len(token) < 3:
                continue
            if token in name: score += 3
            if token in cat:  score += 2
            if token in ai_sum: score += 1
            if token in tags: score += 2

        if score > 0:
            results.append({**f, "_score": score})

    results.sort(key=lambda x: x["_score"], reverse=True)
    return results
