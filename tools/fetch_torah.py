#!/usr/bin/env python3
"""
Descarga los 5 libros de la Torá de la API de Sefaria.
Guarda cada capítulo en data/torah/{libro}/NNN.json
Uso: python tools/fetch_torah.py
     python tools/fetch_torah.py shemot       (solo un libro)
"""
import urllib.request
import json
import time
import os
import sys

BOOKS = [
    {
        "book":       "bereshit",
        "sefaria":    "Genesis",
        "chapters":   50,
        "book_he":    "בְּרֵאשִׁית",
        "book_es":    "Génesis",
        "title_he":   "בְּרֵאשִׁית",
    },
    {
        "book":       "shemot",
        "sefaria":    "Exodus",
        "chapters":   40,
        "book_he":    "שְׁמוֹת",
        "book_es":    "Éxodo",
        "title_he":   "שְׁמוֹת",
    },
    {
        "book":       "vayikra",
        "sefaria":    "Leviticus",
        "chapters":   27,
        "book_he":    "וַיִּקְרָא",
        "book_es":    "Levítico",
        "title_he":   "וַיִּקְרָא",
    },
    {
        "book":       "bamidbar",
        "sefaria":    "Numbers",
        "chapters":   36,
        "book_he":    "בְּמִדְבַּר",
        "book_es":    "Números",
        "title_he":   "בְּמִדְבַּר",
    },
    {
        "book":       "devarim",
        "sefaria":    "Deuteronomy",
        "chapters":   34,
        "book_he":    "דְּבָרִים",
        "book_es":    "Deuteronomio",
        "title_he":   "דְּבָרִים",
    },
]

def fetch_chapter(sefaria_name, ch):
    url = f"https://www.sefaria.org/api/texts/{sefaria_name}.{ch}?lang=he&commentary=0&context=0"
    with urllib.request.urlopen(url, timeout=20) as r:
        return json.loads(r.read())

def build_json(meta, ch, data):
    he_verses = data.get("he", [])
    he_title  = data.get("heTitle", f"{meta['title_he']} {ch}")
    verses = []
    for i, he in enumerate(he_verses, 1):
        text = he.strip() if he else ""
        # Recuperar traducción ES existente si ya existe el archivo
        verses.append({"num": i, "he": text, "es": ""})
    return {
        "book":     meta["book"],
        "book_he":  meta["book_he"],
        "book_es":  meta["book_es"],
        "chapter":  ch,
        "title_he": he_title,
        "verses":   verses,
    }

def merge_es(existing_path, new_verses):
    """Conserva las traducciones ES existentes."""
    if not os.path.exists(existing_path):
        return new_verses
    with open(existing_path, encoding="utf-8") as f:
        old = json.load(f)
    old_map = {v["num"]: v.get("es", "") for v in old.get("verses", [])}
    for v in new_verses:
        v["es"] = old_map.get(v["num"], "")
    return new_verses

def fetch_book(meta, skip_existing=False):
    book    = meta["book"]
    out_dir = f"data/torah/{book}"
    os.makedirs(out_dir, exist_ok=True)
    errors  = []

    print(f"\n── {book.upper()} ({meta['chapters']} capítulos) ──")
    for ch in range(1, meta["chapters"] + 1):
        path = f"{out_dir}/{ch:03d}.json"
        if skip_existing and os.path.exists(path):
            print(f"  skip {book} {ch:2d} (ya existe)")
            continue
        try:
            raw     = fetch_chapter(meta["sefaria"], ch)
            chapter = build_json(meta, ch, raw)
            chapter["verses"] = merge_es(path, chapter["verses"])
            with open(path, "w", encoding="utf-8") as f:
                json.dump(chapter, f, ensure_ascii=False, indent=2)
            print(f"  ✓ {book} {ch:2d} — {len(chapter['verses'])} versículos")
            time.sleep(0.35)
        except Exception as e:
            print(f"  ✗ {book} {ch}: {e}")
            errors.append(ch)
            time.sleep(1.5)

    print(f"  Errores: {errors if errors else 'ninguno'}")
    return errors

def main():
    target = sys.argv[1].lower() if len(sys.argv) > 1 else "all"

    books_to_fetch = [b for b in BOOKS if target == "all" or b["book"] == target]
    if not books_to_fetch:
        print(f"Libro desconocido: {target}")
        print("Opciones:", ", ".join(b["book"] for b in BOOKS))
        sys.exit(1)

    # Si es "all", saltar bereshit porque ya existe
    skip = (target == "all")

    total_errors = []
    for meta in books_to_fetch:
        errs = fetch_book(meta, skip_existing=skip)
        total_errors.extend(errs)

    print(f"\n=== COMPLETADO ===")
    print(f"Errores totales: {total_errors if total_errors else 'ninguno'}")

if __name__ == "__main__":
    main()
