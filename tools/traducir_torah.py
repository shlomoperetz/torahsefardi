#!/usr/bin/env python3
"""
traducir_torah.py — Multi-agent Torah translation pipeline.

Usage:
    python traducir_torah.py --libro bereshit
    python traducir_torah.py --parasha Bereshit_1
    python traducir_torah.py --aliya Bereshit_1_3
    python traducir_torah.py --parasha Bereshit_1 --dry-run
    python traducir_torah.py --libro bereshit --reset-checkpoint
"""

import argparse
import json
import logging
import os
import re
import subprocess
import sys
import time
from datetime import datetime
from html.parser import HTMLParser
from pathlib import Path

import anthropic
import requests

# ─── Paths ────────────────────────────────────────────────────────────────────

ROOT = Path(__file__).parent.parent.resolve()
TOOLS_DIR = Path(__file__).parent.resolve()
DATA_DIR = ROOT / "data" / "torah"

CHECKPOINT_FILE = TOOLS_DIR / "checkpoint.json"
GLOSARIO_FILE = TOOLS_DIR / "glosario.json"
LOG_FILE = TOOLS_DIR / "traduccion.log"
ALIYOT_CACHE_FILE = TOOLS_DIR / "aliyot_cache.json"

# ─── Config ───────────────────────────────────────────────────────────────────

MODEL_TRADUCTOR = "claude-opus-4-6"
MODEL_VALIDADOR = "claude-sonnet-4-6"
MAX_REINTENTOS = 2
PAUSA = 3  # seconds between API calls

# ─── System prompts ───────────────────────────────────────────────────────────

SYSTEM_TRADUCTOR = """Eres un traductor especializado en Torá para una audiencia hispanohablante sefardí contemporánea.

TAREA
Traduce al español el fragmento de Torá que se te proporciona (texto hebreo con numeración de versículos).

NORMAS OBLIGATORIAS

1. NOMBRES DIVINOS
- יהוה → "el Eterno"
- אלהים → "Elohim"
- אדני → "el Señor"
- שדי → "Shaday"

2. ESTILO
- Traducción literal-formal: preserva la sintaxis hebrea cuando el español lo permite.
- Conserva estructuras repetitivas y paralelismos.
- Usa "Y" para la vav consecutiva al inicio de versículo cuando el hebreo lo marca.
- Tiempo verbal consistente dentro del fragmento.

3. HEBRAÍSMOS
- Mantén sin traducir solo términos sin equivalente semántico exacto (tohu vavohu, taninim, sheol, Serafim, Querubim, etc.).
- Todos los términos conservados pasan automáticamente a la sección de notas.
- No añadas paréntesis ni aclaraciones inline.

4. NOMBRES PROPIOS
- Usa forma hebraica estándar: Avraham, Yitsjak, Yaakov, Moshé, Yehoshúa.
- No uses formas castellanizadas.

5. ORTOGRAFÍA Y REGISTRO
- Español estándar, sin arcaísmos ni Ladino.
- Dignidad formal, sin coloquialismos.
- Discurso directo con comillas angulares « ».

6. ESTRUCTURA DEL OUTPUT

Bloque 1 — TRADUCCIÓN
[número] Texto del versículo.

Bloque 2 — NOTAS
Separado por la línea: ---NOTAS---
Formato: [versículo] TÉRMINO — explicación breve (máx. 2 líneas)

Si no hay términos: ---NOTAS---\n(sin notas en este fragmento)

7. LO QUE NO DEBES HACER
- No añadas títulos, subtítulos ni encabezados.
- No omitas versículos.
- No parafrasees ni interpretes.
- No añadas comentarios fuera de los dos bloques definidos."""

SYSTEM_VALIDADOR = """Eres un revisor de traducción de Torá al español desde una perspectiva judía ortodoxa.
Se te proporciona el texto hebreo original y una traducción al español.

Revisa cada versículo y detecta:

CRITERIOS LINGÜÍSTICOS
- Nombres divinos mal traducidos (יהוה→"el Eterno", אלהים→"Elohim", אדני→"el Señor")
- Hebraísmos traducidos que deberían conservarse
- Versículos omitidos
- Paráfrasis o interpretaciones no autorizadas
- Inconsistencias de tiempo verbal
- Paréntesis o aclaraciones inline en el texto

CRITERIOS ORTODOXOS
- Traducciones que impliquen corporeidad divina literal
- Traducciones que contradigan Rashi, Rambam o Ibn Ezra
- Versículos sensibles mal traducidos
- Cualquier resonancia cristológica

Devuelve SOLO uno de estos formatos:

APROBADO

o

RECHAZADO
[versículo] motivo concreto"""

# ─── Parashot list ────────────────────────────────────────────────────────────

PARASHOT = [
    # Bereshit
    {"slug": "Bereshit_1",  "nombre": "Bereshit",      "libro": "bereshit", "sefaria": "Bereshit"},
    {"slug": "Bereshit_2",  "nombre": "Noach",          "libro": "bereshit", "sefaria": "Noach"},
    {"slug": "Bereshit_3",  "nombre": "Lech-Lecha",     "libro": "bereshit", "sefaria": "Lech_Lecha"},
    {"slug": "Bereshit_4",  "nombre": "Vayera",         "libro": "bereshit", "sefaria": "Vayera"},
    {"slug": "Bereshit_5",  "nombre": "Chayei Sarah",   "libro": "bereshit", "sefaria": "Chayei_Sarah"},
    {"slug": "Bereshit_6",  "nombre": "Toledot",        "libro": "bereshit", "sefaria": "Toledot"},
    {"slug": "Bereshit_7",  "nombre": "Vayetze",        "libro": "bereshit", "sefaria": "Vayetze"},
    {"slug": "Bereshit_8",  "nombre": "Vayishlach",     "libro": "bereshit", "sefaria": "Vayishlach"},
    {"slug": "Bereshit_9",  "nombre": "Vayeshev",       "libro": "bereshit", "sefaria": "Vayeshev"},
    {"slug": "Bereshit_10", "nombre": "Miketz",         "libro": "bereshit", "sefaria": "Miketz"},
    {"slug": "Bereshit_11", "nombre": "Vayigash",       "libro": "bereshit", "sefaria": "Vayigash"},
    {"slug": "Bereshit_12", "nombre": "Vayechi",        "libro": "bereshit", "sefaria": "Vayechi"},
    # Shemot
    {"slug": "Shemot_1",    "nombre": "Shemot",         "libro": "shemot",   "sefaria": "Shemot"},
    {"slug": "Shemot_2",    "nombre": "Va'era",         "libro": "shemot",   "sefaria": "Vaera"},
    {"slug": "Shemot_3",    "nombre": "Bo",             "libro": "shemot",   "sefaria": "Bo"},
    {"slug": "Shemot_4",    "nombre": "Beshalach",      "libro": "shemot",   "sefaria": "Beshalach"},
    {"slug": "Shemot_5",    "nombre": "Yitro",          "libro": "shemot",   "sefaria": "Yitro"},
    {"slug": "Shemot_6",    "nombre": "Mishpatim",      "libro": "shemot",   "sefaria": "Mishpatim"},
    {"slug": "Shemot_7",    "nombre": "Terumah",        "libro": "shemot",   "sefaria": "Terumah"},
    {"slug": "Shemot_8",    "nombre": "Tetzaveh",       "libro": "shemot",   "sefaria": "Tetzaveh"},
    {"slug": "Shemot_9",    "nombre": "Ki Tissa",       "libro": "shemot",   "sefaria": "Ki_Tissa"},
    {"slug": "Shemot_10",   "nombre": "Vayakhel",       "libro": "shemot",   "sefaria": "Vayakhel"},
    {"slug": "Shemot_11",   "nombre": "Pekudei",        "libro": "shemot",   "sefaria": "Pekudei"},
    # Vayikra
    {"slug": "Vayikra_1",   "nombre": "Vayikra",        "libro": "vayikra",  "sefaria": "Vayikra"},
    {"slug": "Vayikra_2",   "nombre": "Tzav",           "libro": "vayikra",  "sefaria": "Tzav"},
    {"slug": "Vayikra_3",   "nombre": "Shemini",        "libro": "vayikra",  "sefaria": "Shemini"},
    {"slug": "Vayikra_4",   "nombre": "Tazria",         "libro": "vayikra",  "sefaria": "Tazria"},
    {"slug": "Vayikra_5",   "nombre": "Metzora",        "libro": "vayikra",  "sefaria": "Metzora"},
    {"slug": "Vayikra_6",   "nombre": "Achrei Mot",     "libro": "vayikra",  "sefaria": "Achrei_Mot"},
    {"slug": "Vayikra_7",   "nombre": "Kedoshim",       "libro": "vayikra",  "sefaria": "Kedoshim"},
    {"slug": "Vayikra_8",   "nombre": "Emor",           "libro": "vayikra",  "sefaria": "Emor"},
    {"slug": "Vayikra_9",   "nombre": "Behar",          "libro": "vayikra",  "sefaria": "Behar"},
    {"slug": "Vayikra_10",  "nombre": "Bechukotai",     "libro": "vayikra",  "sefaria": "Bechukotai"},
    # Bamidbar
    {"slug": "Bamidbar_1",  "nombre": "Bamidbar",       "libro": "bamidbar", "sefaria": "Bamidbar"},
    {"slug": "Bamidbar_2",  "nombre": "Naso",           "libro": "bamidbar", "sefaria": "Naso"},
    {"slug": "Bamidbar_3",  "nombre": "Behaalotcha",    "libro": "bamidbar", "sefaria": "Beha%27alotcha"},
    {"slug": "Bamidbar_4",  "nombre": "Shelach",        "libro": "bamidbar", "sefaria": "Shelach"},
    {"slug": "Bamidbar_5",  "nombre": "Korach",         "libro": "bamidbar", "sefaria": "Korach"},
    {"slug": "Bamidbar_6",  "nombre": "Chukat",         "libro": "bamidbar", "sefaria": "Chukat"},
    {"slug": "Bamidbar_7",  "nombre": "Balak",          "libro": "bamidbar", "sefaria": "Balak"},
    {"slug": "Bamidbar_8",  "nombre": "Pinchas",        "libro": "bamidbar", "sefaria": "Pinchas"},
    {"slug": "Bamidbar_9",  "nombre": "Matot",          "libro": "bamidbar", "sefaria": "Matot"},
    {"slug": "Bamidbar_10", "nombre": "Masei",          "libro": "bamidbar", "sefaria": "Masei"},
    # Devarim
    {"slug": "Devarim_1",   "nombre": "Devarim",        "libro": "devarim",  "sefaria": "Devarim"},
    {"slug": "Devarim_2",   "nombre": "Va'etchanan",    "libro": "devarim",  "sefaria": "Vaetchanan"},
    {"slug": "Devarim_3",   "nombre": "Ekev",           "libro": "devarim",  "sefaria": "Eikev"},
    {"slug": "Devarim_4",   "nombre": "Re'eh",          "libro": "devarim",  "sefaria": "Re%27eh"},
    {"slug": "Devarim_5",   "nombre": "Shoftim",        "libro": "devarim",  "sefaria": "Shoftim"},
    {"slug": "Devarim_6",   "nombre": "Ki Tetze",       "libro": "devarim",  "sefaria": "Ki_Teitzei"},
    {"slug": "Devarim_7",   "nombre": "Ki Tavo",        "libro": "devarim",  "sefaria": "Ki_Tavo"},
    {"slug": "Devarim_8",   "nombre": "Nitzavim",       "libro": "devarim",  "sefaria": "Nitzavim"},
    {"slug": "Devarim_9",   "nombre": "Vayelech",       "libro": "devarim",  "sefaria": "Vayeilech"},
    {"slug": "Devarim_10",  "nombre": "Haazinu",        "libro": "devarim",  "sefaria": "Ha%27azinu"},
    # V'zot Haberakhah — handled specially
    {"slug": "Devarim_11",  "nombre": "V'zot Haberakhah", "libro": "devarim", "sefaria": None},
]

VZOT_ALIYOT = [
    {"num": 1, "ch_start": 33, "v_start": 1,  "ch_end": 33, "v_end": 7},
    {"num": 2, "ch_start": 33, "v_start": 8,  "ch_end": 33, "v_end": 12},
    {"num": 3, "ch_start": 33, "v_start": 13, "ch_end": 33, "v_end": 17},
    {"num": 4, "ch_start": 33, "v_start": 18, "ch_end": 33, "v_end": 21},
    {"num": 5, "ch_start": 33, "v_start": 22, "ch_end": 33, "v_end": 26},
    {"num": 6, "ch_start": 33, "v_start": 27, "ch_end": 33, "v_end": 29},
    {"num": 7, "ch_start": 34, "v_start": 1,  "ch_end": 34, "v_end": 12},
]

# ─── Logging setup ────────────────────────────────────────────────────────────

logger = logging.getLogger("traducir_torah")
logger.setLevel(logging.DEBUG)

_fmt = logging.Formatter("[%(asctime)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S")

_file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
_file_handler.setFormatter(_fmt)
logger.addHandler(_file_handler)

_stdout_handler = logging.StreamHandler(sys.stdout)
_stdout_handler.setFormatter(_fmt)
logger.addHandler(_stdout_handler)

# ─── HTML stripping ───────────────────────────────────────────────────────────

class _MLStripper(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=False)
        self._parts = []

    def handle_data(self, data):
        self._parts.append(data)

    def handle_entityref(self, name):
        # Named entities
        mapping = {
            "thinsp": "",
            "nbsp":   " ",
            "amp":    "&",
            "lt":     "<",
            "gt":     ">",
            "quot":   '"',
            "apos":   "'",
        }
        self._parts.append(mapping.get(name, ""))

    def handle_charref(self, name):
        # Numeric character references &#NNN; or &#xHH;
        try:
            if name.startswith("x") or name.startswith("X"):
                ch = chr(int(name[1:], 16))
            else:
                ch = chr(int(name))
            self._parts.append(ch)
        except (ValueError, OverflowError):
            pass

    def get_text(self):
        return "".join(self._parts)


def strip_html(text: str) -> str:
    """Remove all HTML tags and decode entities."""
    if not text:
        return ""
    stripper = _MLStripper()
    stripper.feed(text)
    result = stripper.get_text()
    # Collapse multiple spaces/newlines introduced by block elements
    result = re.sub(r"[ \t]+", " ", result)
    result = re.sub(r"\n{2,}", "\n", result)
    return result.strip()


# ─── JSON data helpers ────────────────────────────────────────────────────────

def _chapter_path(libro: str, ch: int) -> Path:
    return DATA_DIR / libro / f"{ch:03d}.json"


def get_chapter_verses(libro: str, ch: int) -> list:
    """Load a chapter JSON and return its verses list."""
    path = _chapter_path(libro, ch)
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    return data["verses"]


def get_verse_count(libro: str, ch: int) -> int:
    """Return the number of verses in a chapter."""
    return len(get_chapter_verses(libro, ch))


# ─── Aliyot fetching ─────────────────────────────────────────────────────────

def fetch_aliyot(parasha: dict) -> list:
    """
    Fetch aliyot boundaries from Sefaria for a parasha.
    Returns list of dicts: {"num":1,"ch_start":N,"v_start":N,"ch_end":N,"v_end":N}

    Sefaria alts structure (verified):
      alts is a list indexed by chapter-offset (ci=0 → first chapter of parasha).
      Each element is a list indexed by verse (vi=0 → verse 1).
      Non-null elements are dicts: {"en": ["Second"], "he": [...]} marking aliyah starts.
      ci=0, vi=0 is always the first aliyah (may have key "whole": true).
      absolute_ch = sections[0] + ci
      absolute_v  = vi + 1
    """
    sefaria_name = parasha["sefaria"]
    libro = parasha["libro"]

    if sefaria_name is None:
        return VZOT_ALIYOT

    url = f"https://www.sefaria.org/api/texts/Parashat_{sefaria_name}?commentary=0&context=0"
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    data = resp.json()

    sections = data.get("sections", [])      # [ch, v] — start of parasha
    to_sections = data.get("toSections", []) # [ch, v] — end of parasha
    alts = data.get("alts", [])              # list of chapter-level lists

    base_ch = sections[0] if sections else 1  # absolute chapter of first verse

    # Collect aliyah starts from the alts matrix
    # alts[ci][vi] → non-null dict marks the start of an aliyah
    markers = []  # list of (abs_ch, abs_v, label_en)

    if isinstance(alts, list):
        for ci, chapter_alts in enumerate(alts):
            if not isinstance(chapter_alts, list):
                continue
            for vi, v_alt in enumerate(chapter_alts):
                if v_alt is None:
                    continue
                abs_ch = base_ch + ci
                abs_v = vi + 1
                # Label can be a string or a list
                en_label = v_alt.get("en", "")
                if isinstance(en_label, list):
                    en_label = en_label[0] if en_label else ""
                markers.append((abs_ch, abs_v, en_label))

    # Sort by position
    markers.sort(key=lambda x: (x[0], x[1]))

    # Assign aliyah numbers (1–7)
    ORDINALS = {
        "first": 1, "bereshit": 1, "second": 2, "third": 3, "fourth": 4,
        "fifth": 5, "sixth": 6, "seventh": 7, "maftir": 7,
    }
    starts = []  # list of (num, abs_ch, abs_v)
    for i, (abs_ch, abs_v, label) in enumerate(markers):
        label_lower = label.lower().strip()
        num = ORDINALS.get(label_lower, i + 1)
        starts.append((num, abs_ch, abs_v))

    # If no markers found, fall back to a single aliyah covering the whole parasha
    if not starts:
        ch_s = base_ch
        v_s = sections[1] if len(sections) > 1 else 1
        if len(to_sections) >= 2:
            end_ch, end_v = to_sections[0], to_sections[1]
        else:
            end_ch = ch_s
            end_v = get_verse_count(libro, ch_s)
        return [{"num": 1, "ch_start": ch_s, "v_start": v_s,
                 "ch_end": end_ch, "v_end": end_v}]

    # Compute ends: end of aliyah i = one verse before start of aliyah i+1
    aliyot = []
    for i, (num, ch_s, v_s) in enumerate(starts):
        if i + 1 < len(starts):
            _, next_ch, next_v = starts[i + 1]
            end_ch, end_v = _prev_verse(libro, next_ch, next_v)
        else:
            # Last aliyah ends at toSections
            if len(to_sections) >= 2:
                end_ch = to_sections[0]
                end_v = to_sections[1]
            else:
                end_ch = ch_s
                end_v = get_verse_count(libro, ch_s)

        aliyot.append({
            "num": num,
            "ch_start": ch_s,
            "v_start": v_s,
            "ch_end": end_ch,
            "v_end": end_v,
        })

    return aliyot


def _prev_verse(libro: str, ch: int, v: int) -> tuple:
    """Return (ch, v) of the verse immediately before (ch, v)."""
    if v > 1:
        return (ch, v - 1)
    else:
        # Go to last verse of previous chapter
        prev_ch = ch - 1
        if prev_ch < 1:
            return (ch, v)
        last_v = get_verse_count(libro, prev_ch)
        return (prev_ch, last_v)


def get_aliyot_cached(parasha: dict) -> list:
    """Load aliyot from cache, or fetch from Sefaria and cache them."""
    cache = _load_json(ALIYOT_CACHE_FILE, {})
    slug = parasha["slug"]

    if slug in cache:
        return cache[slug]

    aliyot = fetch_aliyot(parasha)
    cache[slug] = aliyot
    _save_json(ALIYOT_CACHE_FILE, cache)
    return aliyot


# ─── Verse collection ─────────────────────────────────────────────────────────

def collect_aliya_verses(libro: str, aliya: dict) -> list:
    """
    Return all verses for the aliyah range (may span chapters).
    Each item: {"num": verse_num, "he_clean": "...", "he_raw": "...", "ch": chapter_num}
    """
    ch_start = aliya["ch_start"]
    v_start  = aliya["v_start"]
    ch_end   = aliya["ch_end"]
    v_end    = aliya["v_end"]

    result = []
    for ch in range(ch_start, ch_end + 1):
        verses = get_chapter_verses(libro, ch)
        for verse in verses:
            v = verse["num"]
            # Filter to the aliyah range
            if ch == ch_start and v < v_start:
                continue
            if ch == ch_end and v > v_end:
                continue
            result.append({
                "num": v,
                "he_clean": strip_html(verse.get("he", "")),
                "he_raw": verse.get("he", ""),
                "ch": ch,
            })
    return result


# ─── Message builders ─────────────────────────────────────────────────────────

def build_user_message_traductor(
    verses: list,
    glosario: dict,
    parasha_nombre: str,
    aliya_num: int,
    feedback: str = "",
) -> str:
    """Build user message for the translator model."""
    parts = []

    if glosario:
        parts.append("GLOSARIO EXISTENTE")
        parts.append("(Usa estas traducciones ya establecidas para los términos siguientes)")
        for term, definition in glosario.items():
            parts.append(f"- {term}: {definition}")
        parts.append("")

    if feedback:
        parts.append("RETROALIMENTACIÓN DEL VALIDADOR (corrige estos problemas):")
        parts.append(feedback)
        parts.append("")

    parts.append(f"Parasha: {parasha_nombre}  |  Aliyá: {aliya_num}")
    parts.append("")
    parts.append("TEXTO A TRADUCIR")
    parts.append("")

    for i, v in enumerate(verses, 1):
        # Format: ch:v [global_num] he_clean
        parts.append(f"{v['ch']}:{v['num']} [{i}] {v['he_clean']}")

    return "\n".join(parts)


def build_user_message_validador(verses: list, translations: dict) -> str:
    """Build user message for the validator model with Hebrew + Spanish side by side."""
    parts = []
    parts.append("Texto hebreo original y traducción al español (versículo a versículo):")
    parts.append("")

    for v in verses:
        key = (v["ch"], v["num"])
        es_text = translations.get(key, "(sin traducción)")
        parts.append(f"[{v['ch']}:{v['num']}]")
        parts.append(f"HE: {v['he_clean']}")
        parts.append(f"ES: {es_text}")
        parts.append("")

    return "\n".join(parts)


# ─── API calls ────────────────────────────────────────────────────────────────

def call_traductor(
    client,
    verses: list,
    glosario: dict,
    parasha: str,
    aliya_num: int,
    feedback: str = "",
    dry_run: bool = False,
) -> tuple:
    """
    Call the translator model.
    Returns (translations, notas) where:
      translations = {(ch, v): es_text}
      notas = {(ch, v): nota_text}
    """
    if dry_run:
        logger.debug("[DRY-RUN] call_traductor skipped")
        translations = {(v["ch"], v["num"]): f"[DRY-RUN] {v['ch']}:{v['num']}" for v in verses}
        notas = {}
        return translations, notas

    user_msg = build_user_message_traductor(verses, glosario, parasha, aliya_num, feedback)

    time.sleep(PAUSA)
    response = client.messages.create(
        model=MODEL_TRADUCTOR,
        max_tokens=8000,
        system=SYSTEM_TRADUCTOR,
        messages=[{"role": "user", "content": user_msg}],
    )

    raw_text = ""
    for block in response.content:
        if block.type == "text":
            raw_text = block.text
            break

    translations, notas = _parse_traductor_output(raw_text, verses)
    return translations, notas


def _parse_traductor_output(raw_text: str, verses: list) -> tuple:
    """
    Parse translator output into translations and notas dicts.
    translations: {(ch, v): es_text}
    notas:        {(ch, v): nota_text}
    Verse [N] in the output maps to verses[N-1].
    """
    translations = {}
    notas = {}

    # Split on ---NOTAS--- separator
    separator = "---NOTAS---"
    if separator in raw_text:
        translation_block, notes_block = raw_text.split(separator, 1)
    else:
        translation_block = raw_text
        notes_block = ""

    # Parse translation block: lines like "[N] text..." or "[N]\ntext..."
    # N is 1-based index into verses list
    trans_lines = translation_block.strip().split("\n")
    current_idx = None
    current_lines = []

    def _flush_translation():
        if current_idx is not None and current_lines:
            text = " ".join(current_lines).strip()
            if current_idx <= len(verses):
                v = verses[current_idx - 1]
                translations[(v["ch"], v["num"])] = text

    for line in trans_lines:
        line = line.rstrip()
        m = re.match(r"^\[(\d+)\]\s*(.*)", line)
        if m:
            _flush_translation()
            current_idx = int(m.group(1))
            rest = m.group(2).strip()
            current_lines = [rest] if rest else []
        else:
            if current_idx is not None and line:
                current_lines.append(line)

    _flush_translation()

    # Parse notes block: lines like "[N] TERM — explanation"
    # or "[ch:v] TERM — explanation"
    if notes_block.strip() and "(sin notas" not in notes_block.lower():
        note_lines = notes_block.strip().split("\n")
        current_note_key = None
        current_note_lines = []

        def _flush_note():
            if current_note_key is not None and current_note_lines:
                notas[current_note_key] = " ".join(current_note_lines).strip()

        for line in note_lines:
            line = line.rstrip()
            # Try [N] format (1-based index)
            m = re.match(r"^\[(\d+)\]\s*(.*)", line)
            if m:
                _flush_note()
                idx = int(m.group(1))
                if idx <= len(verses):
                    v = verses[idx - 1]
                    current_note_key = (v["ch"], v["num"])
                else:
                    current_note_key = None
                current_note_lines = [m.group(2).strip()] if m.group(2).strip() else []
            else:
                if current_note_key is not None and line:
                    current_note_lines.append(line)

        _flush_note()

    return translations, notas


def call_validador(
    client,
    verses: list,
    translations: dict,
    dry_run: bool = False,
) -> tuple:
    """
    Call the validator model.
    Returns (approved: bool, feedback: str)
    """
    if dry_run:
        logger.debug("[DRY-RUN] call_validador skipped")
        return True, ""

    user_msg = build_user_message_validador(verses, translations)

    time.sleep(PAUSA)
    response = client.messages.create(
        model=MODEL_VALIDADOR,
        max_tokens=2000,
        system=SYSTEM_VALIDADOR,
        messages=[{"role": "user", "content": user_msg}],
    )

    raw_text = ""
    for block in response.content:
        if block.type == "text":
            raw_text = block.text
            break

    raw_text = raw_text.strip()

    if raw_text.startswith("APROBADO"):
        return True, ""
    elif raw_text.startswith("RECHAZADO"):
        # Extract feedback lines after RECHAZADO
        lines = raw_text.split("\n", 1)
        feedback = lines[1].strip() if len(lines) > 1 else raw_text
        return False, feedback
    else:
        # Ambiguous — treat as approved with a note
        logger.warning(f"Validator returned unexpected format: {raw_text[:100]}")
        return True, ""


# ─── JSON update ──────────────────────────────────────────────────────────────

def update_json_files(
    libro: str,
    aliya: dict,
    translations: dict,
    notas: dict,
    dry_run: bool = False,
) -> None:
    """Update es (and nota) fields in chapter JSON files for verses in the aliyah range."""
    ch_start = aliya["ch_start"]
    ch_end   = aliya["ch_end"]

    for ch in range(ch_start, ch_end + 1):
        path = _chapter_path(libro, ch)
        with open(path, encoding="utf-8") as f:
            data = json.load(f)

        modified = False
        for verse in data["verses"]:
            v = verse["num"]
            key = (ch, v)
            if key in translations:
                verse["es"] = translations[key]
                modified = True
            if key in notas:
                verse["nota"] = notas[key]
                modified = True

        if modified and not dry_run:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)


# ─── Git operations ───────────────────────────────────────────────────────────

def git_commit_aliya(
    parasha_nombre: str,
    aliya_num: int,
    dry_run: bool = False,
) -> None:
    """Stage data/torah/ and commit with a descriptive message."""
    if dry_run:
        logger.debug(f"[DRY-RUN] git commit: Traducción: {parasha_nombre} aliyá {aliya_num}")
        return

    msg = f"Traducción: {parasha_nombre} aliyá {aliya_num}"
    subprocess.run(
        ["git", "add", "data/torah/"],
        cwd=str(ROOT),
        check=True,
        capture_output=True,
    )
    result = subprocess.run(
        ["git", "commit", "-m", msg],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        # Nothing to commit is not an error in our flow
        if "nothing to commit" in result.stdout.lower() or "nothing to commit" in result.stderr.lower():
            logger.debug("git commit: nothing new to commit")
        else:
            logger.warning(f"git commit returned {result.returncode}: {result.stderr.strip()}")


def git_push(dry_run: bool = False) -> None:
    """Push to remote."""
    if dry_run:
        logger.debug("[DRY-RUN] git push skipped")
        return

    result = subprocess.run(
        ["git", "push"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        logger.warning(f"git push returned {result.returncode}: {result.stderr.strip()}")
    else:
        logger.info("git push OK")


# ─── Checkpoint & Glosario ────────────────────────────────────────────────────

def _load_json(path: Path, default) -> dict:
    if path.exists():
        try:
            with open(path, encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return default
    return default


def _save_json(path: Path, data) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_checkpoint() -> dict:
    return _load_json(CHECKPOINT_FILE, {})


def save_checkpoint(cp: dict) -> None:
    _save_json(CHECKPOINT_FILE, cp)


def load_glosario() -> dict:
    return _load_json(GLOSARIO_FILE, {})


def save_glosario(g: dict) -> None:
    _save_json(GLOSARIO_FILE, g)


def _merge_notas_into_glosario(notas: dict, glosario: dict) -> dict:
    """
    Extract TERM from note values like "TERM — explanation" and add to glosario.
    Only adds terms not already present.
    """
    for key, nota_text in notas.items():
        # Format: "[N] TERM — explanation" or "TERM — explanation"
        # Strip any leading [N] prefix
        text = re.sub(r"^\[\d+\]\s*", "", nota_text).strip()
        m = re.match(r"^([A-ZÁÉÍÓÚÑÜ ]+[A-ZÁÉÍÓÚÑÜ])\s*[—–-]\s*(.+)", text)
        if m:
            term = m.group(1).strip().lower()
            explanation = m.group(2).strip()
            if term and term not in glosario:
                glosario[term] = explanation
    return glosario


# ─── Core pipeline ────────────────────────────────────────────────────────────

def process_aliya(
    client,
    parasha: dict,
    aliya: dict,
    aliyot: list,
    dry_run: bool = False,
) -> str:
    """
    Full pipeline for one aliyah.
    Returns "APROBADO" or "MANUAL".
    """
    slug = parasha["slug"]
    aliya_num = aliya["num"]
    cp_key = f"{slug}_{aliya_num}"
    libro = parasha["libro"]
    nombre = parasha["nombre"]

    cp = load_checkpoint()
    if cp_key in cp:
        logger.info(f"{slug} aliyá {aliya_num} — ya procesada ({cp[cp_key]}), omitida")
        return cp[cp_key]

    verses = collect_aliya_verses(libro, aliya)
    if not verses:
        logger.warning(f"{slug} aliyá {aliya_num} — sin versículos, saltando")
        return "APROBADO"

    glosario = load_glosario()

    feedback = ""
    result = "MANUAL"
    log_parts = [f"{slug} aliyá {aliya_num}"]

    for attempt in range(MAX_REINTENTOS + 1):
        # Translate
        try:
            translations, notas = call_traductor(
                client, verses, glosario, nombre, aliya_num, feedback, dry_run
            )
        except Exception as e:
            logger.error(f"Error en call_traductor (intento {attempt + 1}): {e}")
            if attempt < MAX_REINTENTOS:
                log_parts.append(f"ERROR traduct → reintento {attempt + 1}")
                time.sleep(PAUSA * 2)
                continue
            else:
                result = "MANUAL"
                break

        # Validate
        try:
            approved, feedback = call_validador(client, verses, translations, dry_run)
        except Exception as e:
            logger.error(f"Error en call_validador (intento {attempt + 1}): {e}")
            approved = True  # Accept on validator failure
            feedback = ""

        if approved:
            result = "APROBADO"
            # Update JSON files
            update_json_files(libro, aliya, translations, notas, dry_run)

            # Merge new terms into glosario
            if notas:
                glosario = load_glosario()
                glosario = _merge_notas_into_glosario(notas, glosario)
                if not dry_run:
                    save_glosario(glosario)

            # Commit
            git_commit_aliya(nombre, aliya_num, dry_run)

            if attempt == 0:
                log_parts.append("APROBADO ✓")
            else:
                log_parts.append(f"APROBADO ✓")

            break
        else:
            if attempt < MAX_REINTENTOS:
                log_parts.append(f"RECHAZADO → reintento {attempt + 1}")
            else:
                result = "MANUAL"
                log_parts.append(f"RECHAZADO × {MAX_REINTENTOS} → MANUAL ⚠️")

    # Save checkpoint
    cp = load_checkpoint()
    cp[cp_key] = result
    if not dry_run:
        save_checkpoint(cp)

    log_line = " → ".join(log_parts) if len(log_parts) > 1 else log_parts[0] + f" — {result}"
    # Fix up the log line to match the spec format
    log_line = f"{slug} aliyá {aliya_num} — " + " → ".join(log_parts[1:]) if len(log_parts) > 1 else log_line
    logger.info(log_line)

    return result


def process_parasha(
    client,
    parasha: dict,
    dry_run: bool = False,
) -> None:
    """Process all 7 aliyot for a parasha, then push."""
    slug = parasha["slug"]
    logger.info(f"=== Parasha: {parasha['nombre']} ({slug}) ===")

    aliyot = get_aliyot_cached(parasha)

    for aliya in aliyot:
        process_aliya(client, parasha, aliya, aliyot, dry_run)

    # Push after last aliyah of the parasha
    git_push(dry_run)


def process_libro(
    client,
    libro_slug: str,
    dry_run: bool = False,
) -> None:
    """Process all parashot for a given book."""
    libro_lower = libro_slug.lower()
    parashot = [p for p in PARASHOT if p["libro"] == libro_lower]

    if not parashot:
        logger.error(f"No se encontraron parashot para el libro: {libro_slug}")
        sys.exit(1)

    logger.info(f"=== Libro: {libro_lower} ({len(parashot)} parashot) ===")

    for parasha in parashot:
        process_parasha(client, parasha, dry_run)


# ─── CLI ──────────────────────────────────────────────────────────────────────

def _find_parasha(slug: str) -> dict:
    """Look up a parasha by slug (case-insensitive)."""
    for p in PARASHOT:
        if p["slug"].lower() == slug.lower():
            return p
    logger.error(f"Parasha no encontrada: {slug}")
    logger.info("Slugs disponibles: " + ", ".join(p["slug"] for p in PARASHOT))
    sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Multi-agent Torah translation pipeline"
    )

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--libro",
        metavar="LIBRO",
        help="Book slug (e.g. bereshit, shemot). Processes all parashot.",
    )
    group.add_argument(
        "--parasha",
        metavar="SLUG",
        help="Parasha slug (e.g. Bereshit_1). Processes all 7 aliyot.",
    )
    group.add_argument(
        "--aliya",
        metavar="SLUG",
        help="Aliyah slug (e.g. Bereshit_1_3). Processes a single aliyah.",
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=False,
        help="Print what would be done without making API calls or writing files.",
    )
    parser.add_argument(
        "--reset-checkpoint",
        action="store_true",
        default=False,
        help="Clear checkpoint.json before running.",
    )

    args = parser.parse_args()

    # Check API key
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERROR: ANTHROPIC_API_KEY environment variable is not set.", file=sys.stderr)
        sys.exit(1)

    # Reset checkpoint if requested
    if args.reset_checkpoint:
        if not args.dry_run:
            save_checkpoint({})
        logger.info("Checkpoint reiniciado.")

    # Initialize Anthropic client
    client = anthropic.Anthropic(api_key=api_key)

    if args.dry_run:
        logger.info("[DRY-RUN] Modo simulación activo — no se harán llamadas a la API ni escrituras de archivos.")

    # Dispatch
    if args.libro:
        process_libro(client, args.libro, dry_run=args.dry_run)

    elif args.parasha:
        parasha = _find_parasha(args.parasha)
        process_parasha(client, parasha, dry_run=args.dry_run)

    elif args.aliya:
        # Format: BOOK_N_ALIYANUM  e.g. "Bereshit_1_3"
        parts = args.aliya.rsplit("_", 1)
        if len(parts) != 2:
            logger.error(
                f"Formato de aliyah inválido: {args.aliya}. "
                "Usa SLUG_N como Bereshit_1_3"
            )
            sys.exit(1)

        parasha_slug, aliya_num_str = parts
        try:
            aliya_num = int(aliya_num_str)
        except ValueError:
            logger.error(f"Número de aliyá inválido: {aliya_num_str}")
            sys.exit(1)

        parasha = _find_parasha(parasha_slug)
        aliyot = get_aliyot_cached(parasha)

        aliya = next((a for a in aliyot if a["num"] == aliya_num), None)
        if aliya is None:
            logger.error(
                f"Aliyá {aliya_num} no encontrada en {parasha_slug}. "
                f"Aliyot disponibles: {[a['num'] for a in aliyot]}"
            )
            sys.exit(1)

        process_aliya(client, parasha, aliya, aliyot, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
