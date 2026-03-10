#!/usr/bin/env python3
"""
Descarga Bereshit (Génesis) completo de la API de Sefaria.
Guarda cada capítulo como data/torah/bereshit/NNN.json
"""
import urllib.request
import json
import time
import os

BOOK = "bereshit"
SEFARIA_BOOK = "Genesis"
CHAPTERS = 50
OUTPUT_DIR = f"data/torah/{BOOK}"

BOOK_META = {
    "book": BOOK,
    "book_he": "בְּרֵאשִׁית",
    "book_es": "Génesis",
}

os.makedirs(OUTPUT_DIR, exist_ok=True)

def fetch_chapter(ch):
    url = f"https://www.sefaria.org/api/texts/{SEFARIA_BOOK}.{ch}?lang=he&commentary=0&context=0"
    with urllib.request.urlopen(url, timeout=15) as r:
        return json.loads(r.read())

def clean_he(text):
    """Devuelve el texto tal como viene de Sefaria (con cantilaciones)."""
    return text.strip() if text else ""

def build_json(ch, data):
    he_verses = data.get("he", [])
    he_title = data.get("heTitle", f"בְּרֵאשִׁית {ch}")
    verses = []
    for i, he in enumerate(he_verses, 1):
        verses.append({
            "num": i,
            "he": clean_he(he),
            "es": "",   # se llena después con translate_claude.py
        })
    return {
        **BOOK_META,
        "chapter": ch,
        "title_he": he_title,
        "verses": verses,
    }

errors = []
for ch in range(1, CHAPTERS + 1):
    path = f"{OUTPUT_DIR}/{ch:03d}.json"
    try:
        data = fetch_chapter(ch)
        chapter = build_json(ch, data)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(chapter, f, ensure_ascii=False, indent=2)
        print(f"✓ Bereshit {ch:2d} — {len(chapter['verses'])} versículos")
        time.sleep(0.4)
    except Exception as e:
        print(f"✗ Bereshit {ch}: {e}")
        errors.append(ch)
        time.sleep(1.5)

print(f"\n=== HECHO ===")
print(f"Archivos: {len(os.listdir(OUTPUT_DIR))}")
print(f"Errores: {errors if errors else 'ninguno'}")
