#!/usr/bin/env python3
"""Fidelity audit for rewritten Thai text (Thai Humanizer V3).

This script compares a source text with its rewrite and reports findings in three
separate tiers. It is an *aid* for the Stage E quality gate, not a proof of
semantic fidelity: passing it does NOT guarantee that meaning was preserved.

TIER 1 - Deterministic failures (exact inventory comparison)
  - Numbers (Arabic and Thai digits), percentages, decimals, times, dates
  - URLs, email addresses
  - Version strings (v2.4.0, 1.12.3), HTTP endpoints (GET /v1/users)
  - Code identifiers (snake_case, camelCase, dotted.keys, --flags, UPPER_SNAKE)
  - Fenced code blocks and inline `code` spans that disappeared or changed
  - Protected terms passed with --terms-file
  - Negation markers whose total count dropped (ไม่มี, ไม่รองรับ, ห้าม, ...)
  - Slide duration markers ([Slide 1: 30s])
  - With --context technical: loss of headings, list items, tables, warnings

TIER 2 - Suspected semantic violations (heuristic; need human confirmation)
  - Value/entity relationship changes (e.g. two prices swapped between products)
  - Reversed negation scope (ไม่รองรับ X -> รองรับ X)
  - Missing conditions, exclusivity, bounds, or exceptions (ถ้า, เฉพาะ, ไม่เกิน, ยกเว้น)
  - Dropped uncertainty / hedging, or added certainty boosters
  - Proposed / planned functionality described as completed
  - Actor substitution (ฝ่าย IT -> ผู้ใช้)
  - Added causal connectors / invented reasons (เพื่อ, เพราะ, เนื่องจาก)
  - New Latin-script entities or capability claims not in the source
  - Fabricated testimonials or personal experiences
  - Legacy V2 checks: transit, immediacy, rationale, guarantee, status upgrades
  - Structure loss (headings/lists/tables) when context is not technical

TIER 3 - Stylistic warnings (non-fatal unless --strict)
  - Introduced AI-slop phrases, slide pacing density
  - Formal / bureaucratic register in social or founder posts (--context social|founder)
  - Unnecessary churn when minimal editing is expected (--context minimal)
  - Large shortening of the source

Exit codes: 0 = pass, 1 = failure, 2 = usage / file error.
By default Tier 1 and Tier 2 findings fail; --semantic-advisory makes Tier 2
non-fatal; --strict makes Tier 3 fatal.
"""
from __future__ import annotations

import argparse
from collections import Counter
import difflib
import json
from pathlib import Path
import re
import sys

if sys.platform == "win32":
    try:
        if sys.stdout.encoding != "utf-8":
            sys.stdout.reconfigure(encoding="utf-8")
        if sys.stderr.encoding != "utf-8":
            sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

VERSION = "3.1.0"

CONTEXTS = (
    "general",
    "social",
    "founder",
    "marketing",
    "business",
    "academic",
    "technical",
    "spoken",
    "minimal",
)

DISCLAIMER = (
    "Automated checks compare inventories and patterns only. They cannot prove that "
    "meaning, relationships between facts, tone, or naturalness were preserved; "
    "a human (or the Stage E review) must still read source and rewrite side by side."
)

# ---------------------------------------------------------------------------
# Token inventories (Tier 1)
# ---------------------------------------------------------------------------

CODE_FENCE = re.compile(r"```[^\n]*\n.*?```", re.DOTALL)
INLINE_CODE = re.compile(r"`[^`\n]+`")
URL = re.compile(r"https?://[^\s<>()\[\]{}\"'`]+", re.IGNORECASE)
EMAIL = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
ENDPOINT = re.compile(r"\b(?:GET|POST|PUT|PATCH|DELETE|HEAD|OPTIONS)\s+/[^\s`'\")]*")
VERSION_STR = re.compile(
    r"(?<![A-Za-z0-9_.])(?:v\d+(?:\.\d+)*(?:-[0-9A-Za-z.]+)?|\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.]+)?)(?![A-Za-z0-9_])"
)
IDENTIFIER = re.compile(
    r"(?<![A-Za-z0-9_\-])(?:"
    r"--?[a-z][a-z0-9]*(?:-[a-z0-9]+)+|--[a-z][a-z0-9]+"  # CLI flags
    r"|[A-Za-z][A-Za-z0-9]*(?:_[A-Za-z0-9]+)+"  # snake_case / UPPER_SNAKE
    r"|[a-z]+[A-Z][A-Za-z0-9]*"  # camelCase
    r"|[a-z][a-z0-9]*(?:\.[a-z][a-z0-9_]*){1,}(?=[\s,;:)`]|$)"  # dotted.config.keys
    r")"
)
# Python Unicode \d includes Thai numerals (๐-๙).
NUMBER = re.compile(r"(?<![A-Za-z0-9_])(?:[+-]?(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?[%％]?)")

SLIDE_DURATION_PATTERN = re.compile(
    r"\[(?:slide|สไลด์)\s*(\d+)[\s:-]*(\d+)\s*(?:วินาที|วิ|s|sec|seconds)\]",
    re.IGNORECASE,
)

NEGATION_MARKERS = [
    "ไม่มี",
    "ไม่ได้",
    "ไม่เคย",
    "ไม่ควร",
    "ไม่สามารถ",
    "ไม่รองรับ",
    "ไม่ต้อง",
    "มิได้",
    "มิใช่",
    "ไม่ใช่",
    "ห้าม",
    "ยกเว้น",
    "ปราศจาก",
]

# Negations whose positive form is specific enough to detect scope reversal.
REVERSIBLE_NEGATIONS = {
    "ไม่รองรับ": "รองรับ",
    "ไม่มี": "มี",
    "ไม่สามารถ": "สามารถ",
    "ไม่ใช่": "ใช่",
    "ไม่ควร": "ควร",
    "ไม่เคย": "เคย",
    "ไม่ต้อง": "ต้อง",
    "ไม่ได้รับ": "ได้รับ",
}

# ---------------------------------------------------------------------------
# Relationship / semantic heuristics (Tier 2)
# ---------------------------------------------------------------------------

UNIT_WORDS = (
    r"บาท|฿|thb|usd|ดอลลาร์|%|％|gb|mb|tb|kb|ms|วินาที|นาที|ชั่วโมง|ชม\.|วัน|สัปดาห์|เดือน|ปี|"
    r"ทีม|คน|ที่นั่ง|ชิ้น|กล่อง|แก้ว|จาน|ชุด|ห้อง|กก\.|กิโลกรัม|กรัม|ลิตร|มล\.|เมตร|กม\.|ครั้ง|เครื่อง|"
    r"users?|seats?"
)
BOUND_VALUE = re.compile(
    r"(?<![A-Za-z0-9_.,:])(?P<cur>[$฿]\s?)?(?P<num>\d{1,3}(?:,\d{3})+(?:\.\d+)?|\d+(?:\.\d+)?)"
    r"(?P<unit>\s*(?:" + UNIT_WORDS + r"))?",
    re.IGNORECASE,
)
LATIN_PHRASE = re.compile(
    r"(?<![A-Za-z0-9_\-./@])[A-Za-z][A-Za-z0-9+\-]*(?:\.[A-Za-z][A-Za-z0-9]*)*"
    r"(?:[ ][A-Za-z][A-Za-z0-9+\-]*)*"
)
LATIN_STOPWORDS = {
    "thb", "usd", "gb", "mb", "tb", "kb", "ms", "s", "sec", "seconds", "slide",
    "a", "an", "the", "and", "or", "of", "to", "for", "in", "on", "with", "is",
}
BINDING_WINDOW = 15

CONDITION_GROUPS = {
    "conditional (ถ้า/หาก/กรณี/เมื่อ)": re.compile(
        r"ถ้า(?!คุณ(?:กำลัง)?มองหา)|หาก(?!คุณ(?:กำลัง)?มองหา)|กรณี|เมื่อ(?!วาน|ก่อน|กี้|เช้า|คืน)|\bif\b|\bunless\b", re.IGNORECASE
    ),
    "exclusivity (เฉพาะ/เท่านั้น)": re.compile(r"เฉพาะ|เท่านั้น|\bonly\b", re.IGNORECASE),
    "upper bound (ไม่เกิน/สูงสุด)": re.compile(r"ไม่เกิน|สูงสุด|มากสุด|\bat most\b|\bup to\b", re.IGNORECASE),
    "lower bound (อย่างน้อย/ขั้นต่ำ)": re.compile(r"อย่างน้อย|ขั้นต่ำ|ไม่ต่ำกว่า|\bat least\b|\bminimum\b", re.IGNORECASE),
    "exception (ยกเว้น/นอกจาก)": re.compile(r"ยกเว้น|นอกจาก(?!นี้)|\bexcept\b", re.IGNORECASE),
    "deadline (ภายใน/ก่อนวันที่)": re.compile(r"ภายใน(?!ร้าน|บ้าน|ห้อง|อาคาร|งาน)|ก่อนวันที่|ก่อนเวลา"),
}

HEDGES = re.compile(
    r"อาจ(?!ารย์)|น่าจะ|คาดว่า|ประมาณ|ราว\s?ๆ|เกือบ|คาดการณ์|ประเมินว่า|ไม่แน่ใจ|"
    r"\bmay\b|\bmight\b|\bestimated\b|\bapproximately\b|\blikely\b",
    re.IGNORECASE,
)
CERTAINTY_BOOSTERS = re.compile(
    r"แน่นอน|อย่างแน่นอน|รับประกัน|การันตี|ทุกครั้ง|ไม่มีพลาด|\bdefinitely\b|\bguaranteed?\b",
    re.IGNORECASE,
)

PLANNING_MARKERS = re.compile(
    r"วางแผน|มีแผน|แผนจะ|กำลังพัฒนา|อยู่ระหว่าง|กำลังทดสอบ|ทดสอบ|ต้นแบบ|เตรียม|เร็ว\s?ๆ\s?นี้|"
    r"เป้าหมาย|ข้อเสนอ|เสนอให้|ห้องแล็บ|ห้องปฏิบัติการ|แบบจำลอง|"
    r"\broadmap\b|\bplanned\b|\bproposed\b|\bupcoming\b|\bcoming soon\b|\bprototype\b|\bsimulation\b",
    re.IGNORECASE,
)
FUTURE_JA = re.compile(r"(?<!น่า)(?<!อาจ)(?<!ที่)จะ(?!ต้อง)")
COMPLETION_MARKERS = re.compile(
    r"(?<!ไม่)(?:แล้ว)(?!ก็|จึง|ค่อย|แต่|เสร็จ)|เรียบร้อย|สำเร็จ|ใช้งานได้จริง|พร้อมใช้งาน|"
    r"\breleased\b|\blaunched\b|\bshipped\b|\bnow available\b|\bavailable now\b|\bis live\b",
    re.IGNORECASE,
)
LEGACY_COMPLETION = re.compile(r"ใช้งานได้จริงทั่วประเทศ|สำเร็จแล้วอย่างสมบูรณ์|การันตียอดขาย")

ROLE_TERMS = [
    "ผู้ใช้", "ลูกค้า", "ผู้ดูแลระบบ", "แอดมิน", "ทีมงาน", "ฝ่าย", "บริษัท", "ผู้จัดการ",
    "หัวหน้า", "พนักงาน", "ผู้สมัคร", "ผู้เข้าร่วม", "นักศึกษา", "นักเรียน", "อาจารย์",
    "ผู้ขาย", "ผู้ซื้อ", "ร้าน", "ระบบ", "ผู้ปกครอง", "ผู้เขียน", "ผู้วิจัย",
]

CAUSAL_CONNECTORS = re.compile(
    r"เพื่อ(?!น)|เพราะ|เนื่องจาก|ด้วยเหตุนี้|ส่งผลให้|จึง|\bbecause\b|\bso that\b|\bin order to\b",
    re.IGNORECASE,
)
CAPABILITY_VERBS = re.compile(
    r"(?<!ไม่)รองรับ|เชื่อมต่อ|ซิงค์|ส่งออก|นำเข้า|\bintegrat\w*|\bsupports?\b|\bsync\w*",
    re.IGNORECASE,
)
TESTIMONIAL = re.compile(
    r"(?:ลูกค้า|ผู้ใช้|หลายคน|คนส่วนใหญ่|ใคร\s?ๆ|เพื่อน ?ๆ)(?:[^\s]{0,12})?\s?"
    r"(?:บอกว่า|ชอบ|ชื่นชม|ประทับใจ|รีวิว|ติดใจ|ติดใจกันมาก|ต่างบอก)"
)
PERSONAL_EXPERIENCE = re.compile(r"(?:ผม|ฉัน|ดิฉัน|เรา|ตัวเอง)(?:เอง)?(?:ก็)?เคย(?:เจอ|ประสบ|ผ่าน|ลำบาก|ท้อ)")

# Legacy V2 heuristic lists (kept small on purpose; do not grow into banned-word catalogs)
TRANSIT_PATTERNS = [
    re.compile(r"\b(?:bts|mrt|brt|arl)\b", re.IGNORECASE),
    re.compile(r"airport\s+rail\s+link|รถไฟฟ้า|รถเมล์|วินมอเตอร์ไซค์|สองแถว|เรือด่วน|รถตู้", re.IGNORECASE),
]
IMMEDIACY_PATTERNS = [
    re.compile(r"\breal-time\b", re.IGNORECASE),
    re.compile(r"ได้ทันที|แบบเรียลไทม์|อัตโนมัติในพริบตา|รวดเร็วทันใจ"),
]
CAUSAL_RATIONALE_TERMS = [
    "เพื่อดูแลได้ทั่วถึง",
    "เพื่อดูแลได้อย่างทั่วถึง",
    "เพื่อให้ดูแลได้ทั่วถึง",
    "เพื่อให้ทีมงานสามารถดูแลได้อย่างทั่วถึง",
    "เพื่อให้สามารถดูแลได้อย่างทั่วถึง",
    "เพื่อเก็บฟีดแบ็ก",
    "เพื่อนำฟีดแบ็ก",
    "เพื่อการดูแลที่ใกล้ชิด",
    "เพื่อซัพพอร์ตอย่างใกล้ชิด",
    "เพื่อให้มั่นใจในคุณภาพ",
]
GUARANTEE_PATTERNS = [
    re.compile(r"การันตีความสด|สดใหม่\s*100%|รับประกันความสด|การันตีความปลอดภัย|ปลอดภัย\s*100%|รับประกันความปลอดภัย"),
    re.compile(r"การันตีกำไร|ยั่งยืนแน่นอน|คืนทุนทันที|สำเร็จแน่นอน|ไร้ความเสี่ยง"),
]

# ---------------------------------------------------------------------------
# Stylistic heuristics (Tier 3)
# ---------------------------------------------------------------------------

AI_SLOP_PHRASES = [
    "ถือเป็นอีกหนึ่งตัวเลือกที่น่าสนใจ",
    "ถือเป็นอีกหนึ่งตัวเลือก",
    "ในส่วนของ",
    "สามารถจัดสรรเวลา",
    "ควรค่าแก่การแวะไปลอง",
    "ควรค่าแก่การไปลอง",
    "ไม่ควรพลาดด้วยประการทั้งปวง",
    "ตอบโจทย์ทุกไลฟ์สไตล์",
    "ตอบโจทย์ความต้องการ",
    "บอกเลยว่า",
    "มาร่วมเปิดประสบการณ์",
    "เป็นสิ่งที่น่าจับตามอง",
    "มีความจำเป็นอย่างยิ่งที่จะต้อง",
    "เคยไหมที่",
    "หากคุณกำลังมองหา",
]

# Register cues that read as official/bureaucratic. Only used for social/founder contexts.
FORMAL_REGISTER = re.compile(
    r"ประกอบการพิจารณา|จึงเรียนมา|ขอความกรุณา|ทั้งนี้|ดังกล่าว|อนึ่ง|เป็นที่เรียบร้อย|"
    r"ท่าน(?!กลาง)|ทางเรามีความยินดี|ขอขอบพระคุณ"
)
ENGAGEMENT_BAIT = re.compile(
    r"อย่าลืม(?:กด)?(?:ไลก์|แชร์|ติดตาม|เซฟ)|คอมเมนต์บอก|รีบเลย|ห้ามพลาด|พลาดไม่ได้|แท็กเพื่อน"
)

HEADING = re.compile(r"^\s{0,3}#{1,6}\s+\S", re.MULTILINE)
LIST_ITEM = re.compile(r"^\s*(?:[-*+•]|\d+[.)])\s+\S", re.MULTILINE)
TABLE_ROW = re.compile(r"^\s*\|.*\|\s*$", re.MULTILINE)
WARNING_BLOCK = re.compile(
    r"\[!(?:WARNING|CAUTION|IMPORTANT|NOTE)\]|⚠️|\*\*(?:คำเตือน|ข้อควรระวัง|Warning|Breaking)\*\*|^\s*>\s*(?:คำเตือน|ข้อควรระวัง)",
    re.IGNORECASE | re.MULTILINE,
)

THAI_DIGITS = str.maketrans("๐๑๒๓๔๕๖๗๘๙", "0123456789")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def redact_matches(text: str, pattern: re.Pattern[str]) -> tuple[Counter[str], str]:
    matches = pattern.findall(text)
    return Counter(matches), pattern.sub(" ", text)


def inventory(text: str) -> dict[str, Counter[str]]:
    """Exact token inventories. Order matters: redact containers before contents."""
    blocks, text = redact_matches(text, CODE_FENCE)
    inline, text = redact_matches(text, INLINE_CODE)
    urls, text = redact_matches(text, URL)
    emails, text = redact_matches(text, EMAIL)
    endpoints, text = redact_matches(text, ENDPOINT)
    versions, text = redact_matches(text, VERSION_STR)
    identifiers, text = redact_matches(text, IDENTIFIER)
    numbers = Counter(NUMBER.findall(text))
    # Numbers inside code are also facts: count them from the redacted code too.
    for code in list(blocks) + list(inline):
        for _ in range(blocks.get(code, 0) + inline.get(code, 0)):
            numbers.update(NUMBER.findall(code))
    return {
        "code blocks": Counter({k.strip(): v for k, v in blocks.items()}),
        "inline code": inline,
        "URLs": urls,
        "emails": emails,
        "HTTP endpoints": endpoints,
        "versions": versions,
        "identifiers": identifiers,
        "numbers": numbers,
    }


def delta(source: Counter[str], edited: Counter[str]) -> tuple[Counter[str], Counter[str]]:
    return source - edited, edited - source


def strip_code(text: str) -> str:
    return INLINE_CODE.sub(" ", CODE_FENCE.sub(" ", text))


def count(pattern: re.Pattern[str], text: str) -> int:
    return len(pattern.findall(text))


def added_matches(pattern: re.Pattern[str], source: str, edited: str) -> list[str]:
    src = {m.group(0).lower() for m in pattern.finditer(source)}
    return sorted({m.group(0).lower() for m in pattern.finditer(edited)} - src)


def latin_entities(text: str) -> set[str]:
    text = URL.sub(" ", EMAIL.sub(" ", strip_code(text)))
    text = ENDPOINT.sub(" ", VERSION_STR.sub(" ", text))
    out = set()
    for m in LATIN_PHRASE.finditer(text):
        phrase = m.group(0).strip()
        if phrase.lower() in LATIN_STOPWORDS or len(phrase) < 2:
            continue
        out.add(phrase.lower())
    return out


# ---------------------------------------------------------------------------
# Tier 1 checks
# ---------------------------------------------------------------------------

def check_inventories(source: str, edited: str) -> tuple[list[str], list[str]]:
    failures, suspected = [], []
    s, e = inventory(source), inventory(edited)
    for label in s:
        missing, added = delta(s[label], e[label])
        if label in ("code blocks", "inline code"):
            # Removing or changing code is a hard failure; adding code formatting is only suspicious.
            if missing:
                failures.append(f"{label}: missing or modified={dict(missing)}")
            if added:
                suspected.append(f"{label}: added={dict(added)} (verify the source supports it)")
            continue
        if missing or added:
            failures.append(f"{label}: missing={dict(missing)} extra={dict(added)}")
    return failures, suspected


def check_negations(source: str, edited: str) -> list[str]:
    issues = []
    source_lower = source.lower()
    edited_lower = edited.lower()
    total_source_neg = sum(source_lower.count(n) for n in NEGATION_MARKERS)
    total_edited_neg = sum(edited_lower.count(n) for n in NEGATION_MARKERS)
    for neg in NEGATION_MARKERS:
        s_count = source_lower.count(neg)
        e_count = edited_lower.count(neg)
        if s_count > 0 and e_count == 0 and total_edited_neg < total_source_neg:
            issues.append(
                f"dropped negation: {neg!r} present in source ({s_count}) but missing/reduced in rewritten ({e_count})"
            )
    return issues


def check_slide_pacing(source: str, edited: str) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    source_slides = set(SLIDE_DURATION_PATTERN.findall(source))
    edited_slides = set(SLIDE_DURATION_PATTERN.findall(edited))
    if not source_slides:
        return errors, warnings
    for num, dur in sorted(source_slides - edited_slides):
        errors.append(f"dropped or modified slide duration marker: Slide {num} ({dur}s)")
    split_pat = re.compile(
        r"(\[(?:slide|สไลด์)\s*(\d+)[\s:-]*(\d+)\s*(?:วินาที|วิ|s|sec|seconds)\])",
        re.IGNORECASE,
    )
    splits = split_pat.split(edited)
    i = 1
    while i < len(splits):
        slide_num, duration, content = splits[i + 1], int(splits[i + 2]), splits[i + 3]
        clean_chars = len(re.sub(r"\s+", "", content))
        if duration > 0 and clean_chars / duration > 16.0:
            warnings.append(
                f"presentation pacing warning: Slide {slide_num} ({duration}s) has {clean_chars} chars "
                f"(~{clean_chars / duration:.1f} chars/sec); risks exceeding duration, recommend read-aloud timing."
            )
        i += 4
    return errors, warnings


def structure_profile(text: str) -> dict[str, int]:
    return {
        "headings": count(HEADING, text),
        "list items": count(LIST_ITEM, text),
        "table rows": count(TABLE_ROW, text),
        "warnings/callouts": count(WARNING_BLOCK, text),
        "code blocks": count(CODE_FENCE, text),
    }


def check_structure(source: str, edited: str) -> list[str]:
    issues = []
    s, e = structure_profile(source), structure_profile(edited)
    for key, s_val in s.items():
        if key == "code blocks":
            continue  # covered by the code inventory
        if s_val and e[key] < s_val:
            issues.append(
                f"structure loss: {key} reduced from {s_val} to {e[key]} (scannable formatting removed)"
            )
    return issues


# ---------------------------------------------------------------------------
# Tier 2 checks
# ---------------------------------------------------------------------------

def entity_spans(text: str, terms: list[str]) -> list[tuple[int, int, str]]:
    spans: list[tuple[int, int, str]] = []
    taken = [False] * len(text)
    for term in sorted({t for t in terms if t}, key=len, reverse=True):
        for m in re.finditer(re.escape(term), text):
            if not any(taken[m.start():m.end()]):
                spans.append((m.start(), m.end(), term.lower()))
                for k in range(m.start(), m.end()):
                    taken[k] = True
    for m in LATIN_PHRASE.finditer(text):
        phrase = m.group(0).strip()
        if phrase.lower() in LATIN_STOPWORDS or len(phrase) < 2:
            continue
        if any(taken[m.start():m.start() + len(phrase)]):
            continue
        spans.append((m.start(), m.start() + len(phrase), phrase.lower()))
    return sorted(spans)


def value_bindings(text: str, terms: list[str]) -> dict[str, set[str]]:
    """Bind unit-bearing values (prices, quantities, durations) to an entity.

    The entity written before the value wins ("Croissant 75 บาท"); an entity written
    after the value is used only when none precedes it within the window.

    A value binds to an entity only when they sit within BINDING_WINDOW characters
    on the same line with no other value or entity between them. Unbound values are ignored.
    """
    text = URL.sub(lambda m: " " * len(m.group(0)), text)
    entities = entity_spans(text, terms)
    values = []
    for m in BOUND_VALUE.finditer(text):
        if not (m.group("cur") or m.group("unit")):
            continue
        num = m.group("num").translate(THAI_DIGITS).replace(",", "")
        unit = (m.group("unit") or m.group("cur") or "").strip().lower()
        values.append((m.start(), m.end(), f"{num} {unit}".strip()))
    bindings: dict[str, set[str]] = {}
    for v_start, v_end, value in values:
        best = None
        for e_start, e_end, name in entities:
            if e_end <= v_start:
                gap = text[e_end:v_start]
                after = False
            elif e_start >= v_end:
                gap = text[v_end:e_start]
                after = True
            else:
                continue
            if len(gap) > BINDING_WINDOW or "\n" in gap or re.search(r"\d", gap):
                continue
            score = (after, len(gap))  # prefer "entity ... value" order, then proximity
            if best is None or score < best[0]:
                best = (score, name)
        if best:
            bindings.setdefault(best[1], set()).add(value)
    return bindings


def check_relationships(source: str, edited: str, terms: list[str]) -> list[str]:
    issues = []
    s_bind, e_bind = value_bindings(source, terms), value_bindings(edited, terms)
    for entity, s_vals in s_bind.items():
        e_vals = e_bind.get(entity)
        if e_vals and not (s_vals & e_vals):
            owners = [other for other, vals in s_bind.items() if other != entity and vals & e_vals]
            hint = f"; in the source that value belonged to {owners}" if owners else ""
            issues.append(
                f"relationship change: {entity!r} is bound to {sorted(s_vals)} in source but to "
                f"{sorted(e_vals)} in rewrite{hint}"
            )
    return issues


def _object_head(text: str, pos: int) -> str:
    rest = text[pos:].lstrip()
    latin = re.match(r"[A-Za-z][A-Za-z0-9+\-.]*", rest)
    if latin:
        return latin.group(0)
    thai = re.match(r"[฀-๿]{1,5}", rest)
    return thai.group(0) if thai else ""


def check_negation_reversal(source: str, edited: str) -> list[str]:
    issues = []
    for neg, positive in REVERSIBLE_NEGATIONS.items():
        for m in re.finditer(re.escape(neg), source):
            obj = _object_head(source, m.end())
            if len(obj) < 2:
                continue
            negated = re.compile(re.escape(neg) + r"\s?" + re.escape(obj))
            if negated.search(edited):
                continue
            positive_pat = re.compile(r"(?<!ไม่)(?<!มิ)" + re.escape(positive) + r"\s?" + re.escape(obj))
            if positive_pat.search(edited):
                issues.append(
                    f"negation reversed: source says {neg + ' ' + obj!r} but rewrite asserts {positive + ' ' + obj!r}"
                )
    return issues


def check_negation_added(source: str, edited: str) -> list[str]:
    s_n = sum(source.count(n) for n in NEGATION_MARKERS)
    e_n = sum(edited.count(n) for n in NEGATION_MARKERS)
    if e_n > s_n:
        return [f"negation introduced: negation markers rose from {s_n} to {e_n}; a positive statement may now read as negative"]
    return []


# "เฉพาะ ... เท่านั้น" in one clause is a single restriction; collapse it before counting.
REDUNDANT_EXCLUSIVITY = re.compile(r"(เฉพาะ[^\n]{0,40}?)เท่านั้น")


def check_conditions(source: str, edited: str) -> list[str]:
    issues = []
    s_clean = REDUNDANT_EXCLUSIVITY.sub(r"\1", strip_code(source))
    e_clean = REDUNDANT_EXCLUSIVITY.sub(r"\1", strip_code(edited))
    for label, pat in CONDITION_GROUPS.items():
        s_n, e_n = count(pat, s_clean), count(pat, e_clean)
        if s_n > e_n:
            issues.append(f"possible missing condition: {label} appears {s_n}x in source but {e_n}x in rewrite")
    return issues


def check_certainty(source: str, edited: str) -> list[str]:
    issues = []
    s_n, e_n = count(HEDGES, source), count(HEDGES, edited)
    if s_n > e_n:
        issues.append(f"possible certainty upgrade: uncertainty markers reduced from {s_n} to {e_n}")
    for term in added_matches(CERTAINTY_BOOSTERS, source, edited):
        issues.append(f"possible certainty upgrade: certainty booster {term!r} added without source basis")
    return issues


def check_status(source: str, edited: str) -> list[str]:
    issues = []
    s_plan = count(PLANNING_MARKERS, source) + count(FUTURE_JA, source)
    e_plan = count(PLANNING_MARKERS, edited) + count(FUTURE_JA, edited)
    if not s_plan:
        return issues
    for m in LEGACY_COMPLETION.finditer(edited):
        if m.group(0) not in source:
            issues.append(
                f"unsupported status upgrade: {m.group(0)!r} claims proven implementation while source establishes prototype/planning"
            )
    s_done, e_done = count(COMPLETION_MARKERS, source), count(COMPLETION_MARKERS, edited)
    if e_done > s_done and e_plan < s_plan and not issues:
        issues.append(
            f"unsupported status upgrade: planning/future markers fell {s_plan}->{e_plan} while completion markers rose "
            f"{s_done}->{e_done} (proposed work may now read as done)"
        )
    elif count(PLANNING_MARKERS, source) and not count(PLANNING_MARKERS, edited) and not issues:
        issues.append("status qualifier dropped: source marks work as planned/prototype/future but rewrite has no such marker")
    return issues


def check_actors(source: str, edited: str) -> list[str]:
    s_roles = {r for r in ROLE_TERMS if r in source}
    e_roles = {r for r in ROLE_TERMS if r in edited}
    removed, added = s_roles - e_roles, e_roles - s_roles
    if removed and added:
        return [f"possible actor change: {sorted(removed)} no longer appear while {sorted(added)} were introduced"]
    return []


def check_causal_claims(source: str, edited: str) -> list[str]:
    issues = []
    source_lower, edited_lower = source.lower(), edited.lower()
    matched: list[str] = []
    for term in sorted(CAUSAL_RATIONALE_TERMS, key=len, reverse=True):
        if term in edited_lower and term not in source_lower and not any(term in m for m in matched):
            matched.append(term)
            issues.append(f"unsupported causal explanation: {term!r} added to justify limit/action without source basis")
    s_n, e_n = count(CAUSAL_CONNECTORS, strip_code(source)), count(CAUSAL_CONNECTORS, strip_code(edited))
    if e_n > s_n and not matched:
        issues.append(
            f"possible invented reason: causal/purpose connectors rose from {s_n} to {e_n}; confirm every 'why' is in the source"
        )
    return issues


def check_additions(source: str, edited: str, terms: list[str]) -> list[str]:
    issues = []
    s_lat, e_lat = latin_entities(source), latin_entities(edited)
    term_lower = {t.lower() for t in terms}
    new = sorted(x for x in e_lat - s_lat if x not in term_lower)
    if new:
        issues.append(f"new entity or term not in source: {new} (possible unsupported capability or unneeded loanword)")
    missing = sorted(x for x in s_lat - e_lat if x not in term_lower)
    if missing:
        issues.append(f"entity possibly dropped: {missing} (verify it was translated, not lost)")
    s_cap, e_cap = count(CAPABILITY_VERBS, source), count(CAPABILITY_VERBS, edited)
    if e_cap > s_cap:
        issues.append(f"possible unsupported capability: capability verbs rose from {s_cap} to {e_cap}")
    for term in added_matches(TESTIMONIAL, source, edited):
        issues.append(f"possible fabricated testimonial/customer opinion: {term!r}")
    for term in added_matches(PERSONAL_EXPERIENCE, source, edited):
        issues.append(f"possible invented personal experience: {term!r}")
    return issues


def check_legacy_claims(source: str, edited: str, flags: dict[str, bool]) -> list[str]:
    issues = []
    if flags.get("transit", True):
        for pat in TRANSIT_PATTERNS:
            for term in added_matches(pat, source, edited):
                issues.append(f"unsupported transit claim: {term!r} added to rewritten text without source basis")
    if flags.get("immediacy", True):
        for pat in IMMEDIACY_PATTERNS:
            for term in added_matches(pat, source, edited):
                issues.append(f"unsupported immediacy claim: {term!r} added to rewritten text without source basis")
    if flags.get("guarantees", True):
        for pat in GUARANTEE_PATTERNS:
            for term in added_matches(pat, source, edited):
                issues.append(f"unsupported guarantee claim: {term!r} added without source basis")
    return issues


# ---------------------------------------------------------------------------
# Tier 3 checks
# ---------------------------------------------------------------------------

def check_slop_phrases(source: str, edited: str) -> list[str]:
    warnings = []
    source_lower, edited_lower = source.lower(), edited.lower()
    matched: list[str] = []
    for phrase in sorted(AI_SLOP_PHRASES, key=len, reverse=True):
        if phrase in edited_lower and phrase not in source_lower and not any(phrase in m for m in matched):
            matched.append(phrase)
            warnings.append(f"robotic AI slop phrase introduced: {phrase!r}")
    return warnings


def check_register(source: str, edited: str, context: str) -> list[str]:
    if context not in ("social", "founder"):
        return []
    warnings = []
    for m in FORMAL_REGISTER.finditer(edited):
        origin = "retained from source" if m.group(0) in source else "introduced"
        warnings.append(f"formal register in {context} post ({origin}): {m.group(0)!r}")
    for term in added_matches(ENGAGEMENT_BAIT, source, edited):
        warnings.append(f"engagement bait / call to action introduced: {term!r}")
    return warnings


def similarity(source: str, edited: str) -> float:
    return difflib.SequenceMatcher(None, source, edited, autojunk=False).ratio()


def check_churn(source: str, edited: str, context: str) -> list[str]:
    warnings = []
    ratio = similarity(source, edited)
    if context == "minimal" and ratio < 0.85:
        warnings.append(
            f"unnecessary rewriting suspected: similarity {ratio:.2f} < 0.85 for text marked as already natural"
        )
    s_len, e_len = len(source.strip()), len(edited.strip())
    if s_len >= 200 and e_len / s_len < 0.5:
        warnings.append(
            f"substantial shortening: rewrite is {e_len / s_len:.0%} of source length; confirm no requested content was dropped"
        )
    return warnings


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------

def check(
    source: str,
    edited: str,
    terms: list[str] | None = None,
    context: str = "general",
    check_transit: bool = True,
    check_immediacy: bool = True,
    check_causal: bool = True,
    check_guarantees: bool = True,
    check_modality: bool = True,
    check_slides: bool = True,
    check_slop: bool = True,
    check_semantic: bool = True,
) -> dict:
    terms = [t for t in (terms or []) if t]
    deterministic: list[str] = []
    suspected: list[str] = []
    stylistic: list[str] = []

    # Tier 1
    inv_fail, inv_suspect = check_inventories(source, edited)
    deterministic.extend(inv_fail)
    suspected.extend(inv_suspect)
    for term in terms:
        old_count, new_count = source.count(term), edited.count(term)
        if old_count != new_count:
            deterministic.append(f"protected term {term!r}: original={old_count}, rewritten={new_count}")
    deterministic.extend(check_negations(source, edited))
    if check_slides:
        slide_errors, pacing_warnings = check_slide_pacing(source, edited)
        deterministic.extend(slide_errors)
        stylistic.extend(pacing_warnings)
    structure = check_structure(source, edited)
    (deterministic if context == "technical" else suspected).extend(structure)

    # Tier 2
    suspected.extend(
        check_legacy_claims(
            source, edited, {"transit": check_transit, "immediacy": check_immediacy, "guarantees": check_guarantees}
        )
    )
    if check_causal:
        suspected.extend(check_causal_claims(source, edited))
    if check_modality:
        suspected.extend(check_status(source, edited))
    if check_semantic:
        suspected.extend(check_relationships(source, edited, terms))
        suspected.extend(check_negation_reversal(source, edited))
        suspected.extend(check_negation_added(source, edited))
        suspected.extend(check_conditions(source, edited))
        suspected.extend(check_certainty(source, edited))
        suspected.extend(check_actors(source, edited))
        suspected.extend(check_additions(source, edited, terms))

    # Tier 3
    if check_slop:
        stylistic.extend(check_slop_phrases(source, edited))
    stylistic.extend(check_register(source, edited, context))
    stylistic.extend(check_churn(source, edited, context))

    return {
        "deterministic_failures": deterministic,
        "suspected_semantic_violations": suspected,
        "stylistic_warnings": stylistic,
        "metrics": {
            "similarity": round(similarity(source, edited), 3),
            "length_ratio": round(len(edited.strip()) / max(1, len(source.strip())), 3),
            "source_structure": structure_profile(source),
            "rewrite_structure": structure_profile(edited),
        },
        # Backward-compatible keys (V2.x)
        "errors": deterministic + suspected,
        "warnings": stylistic,
        "deterministic_errors": deterministic,
        "unsupported_claim_errors": suspected,
    }



def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("original", type=Path, help="Original UTF-8 text file")
    parser.add_argument("rewritten", type=Path, help="Rewritten UTF-8 text file")
    parser.add_argument("--terms-file", type=Path, help="UTF-8 file: one exact term per line (also used as entities for relationship checks)")
    parser.add_argument("--context", choices=CONTEXTS, default="general", help="Writing context from Stage A")
    parser.add_argument("--strict", action="store_true", help="Treat stylistic warnings as failures")
    parser.add_argument("--semantic-advisory", action="store_true", help="Report suspected semantic violations without failing")
    parser.add_argument("--no-transit-check", action="store_true")
    parser.add_argument("--no-immediacy-check", action="store_true")
    parser.add_argument("--no-causal-check", action="store_true")
    parser.add_argument("--no-guarantee-check", action="store_true")
    parser.add_argument("--no-modality-check", action="store_true")
    parser.add_argument("--no-slide-check", action="store_true")
    parser.add_argument("--no-slop-check", action="store_true")
    parser.add_argument("--no-semantic-check", action="store_true", help="Disable V3 relationship/condition/actor heuristics")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")
    parser.add_argument("--version", action="version", version=f"check_preservation {VERSION}")
    args = parser.parse_args()

    try:
        source = args.original.read_text(encoding="utf-8")
        edited = args.rewritten.read_text(encoding="utf-8")
        terms = (
            [
                line.strip()
                for line in args.terms_file.read_text(encoding="utf-8").splitlines()
                if line.strip() and not line.lstrip().startswith("#")
            ]
            if args.terms_file
            else []
        )
    except (OSError, UnicodeError) as exc:
        msg = f"ERROR: cannot read input: {exc}"
        if args.json:
            print(json.dumps({"status": "error", "message": msg}, ensure_ascii=False))
        else:
            print(msg, file=sys.stderr)
        return 2

    results = check(
        source,
        edited,
        terms=terms,
        context=args.context,
        check_transit=not args.no_transit_check,
        check_immediacy=not args.no_immediacy_check,
        check_causal=not args.no_causal_check,
        check_guarantees=not args.no_guarantee_check,
        check_modality=not args.no_modality_check,
        check_slides=not args.no_slide_check,
        check_slop=not args.no_slop_check,
        check_semantic=not args.no_semantic_check,
    )
    det = results["deterministic_failures"]
    sus = results["suspected_semantic_violations"]
    sty = results["stylistic_warnings"]
    has_failed = bool(det) or (bool(sus) and not args.semantic_advisory) or (args.strict and bool(sty))

    if args.json:
        payload = {
            "passed": not has_failed,
            "version": VERSION,
            "context": args.context,
            "strict": args.strict,
            "semantic_advisory": args.semantic_advisory,
            "deterministic_failures": det,
            "suspected_semantic_violations": sus,
            "stylistic_warnings": sty,
            "metrics": results["metrics"],
            "deterministic_errors": det,
            "unsupported_claim_errors": sus,
            "disclaimer": DISCLAIMER,
        }
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 1 if has_failed else 0

    if det:
        print("FAIL [DETERMINISTIC ERROR]: token, value, code, structure, or negation discrepancies:")
        for err in det:
            print(f" - [DETERMINISTIC] {err}")
    if sus:
        prefix = "WARN" if args.semantic_advisory else "FAIL"
        print(f"{prefix} [SUSPECTED SEMANTIC VIOLATION]: heuristics flagged possible meaning changes (confirm by reading):")
        for err in sus:
            print(f" - [SUSPECTED] {err}")
    if sty:
        prefix = "FAIL" if args.strict else "WARN"
        print(f"{prefix} [STYLE WARNING]: detected robotic AI slop phrasing or other stylistic issues:")
        for warn in sty:
            print(f" - [STYLE] {warn}")
    m = results["metrics"]
    print(f"INFO: similarity={m['similarity']} length_ratio={m['length_ratio']} context={args.context}")
    if not has_failed:
        print("PASS: no mismatch in checked values, code, protected terms, negations, or flagged relationships.")
    print(f"NOTE: {DISCLAIMER}")
    return 1 if has_failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
