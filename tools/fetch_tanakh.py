#!/usr/bin/env python3
"""
Descarga libros del Tanaj de la API de Sefaria.
Uso: python tools/fetch_tanakh.py               (todo el Tanaj)
     python tools/fetch_tanakh.py neviim         (solo Profetas)
     python tools/fetch_tanakh.py ketuvim        (solo Escritos)
     python tools/fetch_tanakh.py yehoshua       (solo un libro)
"""
import urllib.request
import json
import time
import os
import sys

SECTIONS = {
    "neviim": [
        {"book": "yehoshua",        "sefaria": "Joshua",        "chapters": 24, "book_he": "יְהוֹשֻׁעַ",          "book_es": "Josué",                    "order": 1},
        {"book": "shoftim",         "sefaria": "Judges",        "chapters": 21, "book_he": "שֹׁפְטִים",           "book_es": "Jueces",                   "order": 2},
        {"book": "shmuel1",         "sefaria": "I Samuel",      "chapters": 31, "book_he": "שְׁמוּאֵל א",         "book_es": "1 Samuel",                 "order": 3},
        {"book": "shmuel2",         "sefaria": "II Samuel",     "chapters": 24, "book_he": "שְׁמוּאֵל ב",         "book_es": "2 Samuel",                 "order": 4},
        {"book": "melakhim1",       "sefaria": "I Kings",       "chapters": 22, "book_he": "מְלָכִים א",          "book_es": "1 Reyes",                  "order": 5},
        {"book": "melakhim2",       "sefaria": "II Kings",      "chapters": 25, "book_he": "מְלָכִים ב",          "book_es": "2 Reyes",                  "order": 6},
        {"book": "yeshayahu",       "sefaria": "Isaiah",        "chapters": 66, "book_he": "יְשַׁעְיָהוּ",        "book_es": "Isaías",                   "order": 7},
        {"book": "yirmiyahu",       "sefaria": "Jeremiah",      "chapters": 52, "book_he": "יִרְמְיָהוּ",         "book_es": "Jeremías",                 "order": 8},
        {"book": "yehezkel",        "sefaria": "Ezekiel",       "chapters": 48, "book_he": "יְחֶזְקֵאל",          "book_es": "Ezequiel",                 "order": 9},
        {"book": "hoshea",          "sefaria": "Hosea",         "chapters": 14, "book_he": "הוֹשֵׁעַ",            "book_es": "Oseas",                    "order": 10},
        {"book": "yoel",            "sefaria": "Joel",          "chapters": 4,  "book_he": "יוֹאֵל",              "book_es": "Joel",                     "order": 11},
        {"book": "amos",            "sefaria": "Amos",          "chapters": 9,  "book_he": "עָמוֹס",              "book_es": "Amós",                     "order": 12},
        {"book": "ovadyah",         "sefaria": "Obadiah",       "chapters": 1,  "book_he": "עֹבַדְיָה",           "book_es": "Abdías",                   "order": 13},
        {"book": "yonah",           "sefaria": "Jonah",         "chapters": 4,  "book_he": "יוֹנָה",              "book_es": "Jonás",                    "order": 14},
        {"book": "mikhah",          "sefaria": "Micah",         "chapters": 7,  "book_he": "מִיכָה",              "book_es": "Miqueas",                  "order": 15},
        {"book": "nahum",           "sefaria": "Nahum",         "chapters": 3,  "book_he": "נַחוּם",              "book_es": "Nahúm",                    "order": 16},
        {"book": "havakkuk",        "sefaria": "Habakkuk",      "chapters": 3,  "book_he": "חֲבַקּוּק",           "book_es": "Habacuc",                  "order": 17},
        {"book": "tzefanyah",       "sefaria": "Zephaniah",     "chapters": 3,  "book_he": "צְפַנְיָה",           "book_es": "Sofonías",                 "order": 18},
        {"book": "haggai",          "sefaria": "Haggai",        "chapters": 2,  "book_he": "חַגַּי",              "book_es": "Hageo",                    "order": 19},
        {"book": "zekharyah",       "sefaria": "Zechariah",     "chapters": 14, "book_he": "זְכַרְיָה",           "book_es": "Zacarías",                 "order": 20},
        {"book": "malakhi",         "sefaria": "Malachi",       "chapters": 3,  "book_he": "מַלְאָכִי",           "book_es": "Malaquías",                "order": 21},
    ],
    "ketuvim": [
        {"book": "tehilim",             "sefaria": "Psalms",        "chapters": 150, "book_he": "תְּהִלִּים",        "book_es": "Salmos",                    "order": 1},
        {"book": "mishlei",             "sefaria": "Proverbs",      "chapters": 31,  "book_he": "מִשְׁלֵי",          "book_es": "Proverbios",                "order": 2},
        {"book": "iyov",                "sefaria": "Job",           "chapters": 42,  "book_he": "אִיּוֹב",           "book_es": "Job",                       "order": 3},
        {"book": "shir_hashirim",       "sefaria": "Song of Songs", "chapters": 8,   "book_he": "שִׁיר הַשִּׁירִים", "book_es": "Cantar de los Cantares",    "order": 4},
        {"book": "rut",                 "sefaria": "Ruth",          "chapters": 4,   "book_he": "רוּת",              "book_es": "Rut",                       "order": 5},
        {"book": "ekhah",               "sefaria": "Lamentations",  "chapters": 5,   "book_he": "אֵיכָה",            "book_es": "Lamentaciones",             "order": 6},
        {"book": "kohelet",             "sefaria": "Ecclesiastes",  "chapters": 12,  "book_he": "קֹהֶלֶת",           "book_es": "Eclesiastés",               "order": 7},
        {"book": "esther",              "sefaria": "Esther",        "chapters": 10,  "book_he": "אֶסְתֵּר",          "book_es": "Ester",                     "order": 8},
        {"book": "daniel",              "sefaria": "Daniel",        "chapters": 12,  "book_he": "דָּנִיֵּאל",        "book_es": "Daniel",                    "order": 9},
        {"book": "ezra",                "sefaria": "Ezra",          "chapters": 10,  "book_he": "עֶזְרָא",           "book_es": "Esdras",                    "order": 10},
        {"book": "nekhemyah",           "sefaria": "Nehemiah",      "chapters": 13,  "book_he": "נְחֶמְיָה",         "book_es": "Nehemías",                  "order": 11},
        {"book": "divreiy_hayamim1",    "sefaria": "I Chronicles",  "chapters": 29,  "book_he": "דִּבְרֵי הַיָּמִים א", "book_es": "1 Crónicas",             "order": 12},
        {"book": "divreiy_hayamim2",    "sefaria": "II Chronicles", "chapters": 36,  "book_he": "דִּבְרֵי הַיָּמִים ב", "book_es": "2 Crónicas",             "order": 13},
    ],
}

# Flat map for lookup by book slug
ALL_BOOKS = {}
for sec, books in SECTIONS.items():
    for b in books:
        ALL_BOOKS[b["book"]] = {**b, "section": sec}


def fetch_chapter(sefaria_name, ch):
    url = f"https://www.sefaria.org/api/texts/{urllib.parse.quote(sefaria_name)}.{ch}?lang=he&commentary=0&context=0"
    with urllib.request.urlopen(url, timeout=20) as r:
        return json.loads(r.read())


def build_json(meta, ch, data):
    he_verses = data.get("he", [])
    he_title  = data.get("heTitle", f"{meta['book_he']} {ch}")
    verses = []
    for i, he in enumerate(he_verses, 1):
        text = he.strip() if he else ""
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
    if not os.path.exists(existing_path):
        return new_verses
    with open(existing_path, encoding="utf-8") as f:
        old = json.load(f)
    old_map = {v["num"]: v.get("es", "") for v in old.get("verses", [])}
    for v in new_verses:
        v["es"] = old_map.get(v["num"], "")
    return new_verses


def fetch_book(section, meta, skip_existing=False):
    book    = meta["book"]
    out_dir = f"data/{section}/{book}"
    os.makedirs(out_dir, exist_ok=True)
    errors  = []

    print(f"\n── {book.upper()} ({meta['chapters']} caps) ──")
    for ch in range(1, meta["chapters"] + 1):
        path = f"{out_dir}/{ch:03d}.json"
        if skip_existing and os.path.exists(path):
            print(f"  skip {book} {ch:2d}")
            continue
        try:
            raw     = fetch_chapter(meta["sefaria"], ch)
            chapter = build_json(meta, ch, raw)
            chapter["verses"] = merge_es(path, chapter["verses"])
            with open(path, "w", encoding="utf-8") as f:
                json.dump(chapter, f, ensure_ascii=False, indent=2)
            print(f"  ✓ {book} {ch:2d} — {len(chapter['verses'])} vs")
            time.sleep(0.35)
        except Exception as e:
            print(f"  ✗ {book} {ch}: {e}")
            errors.append(ch)
            time.sleep(1.5)

    print(f"  Errores: {errors if errors else 'ninguno'}")
    return errors


def main():
    import urllib.parse  # noqa — needed for fetch_chapter
    target = sys.argv[1].lower() if len(sys.argv) > 1 else "all"

    tasks = []  # list of (section, meta)

    if target == "all":
        for sec, books in SECTIONS.items():
            for b in books:
                tasks.append((sec, b))
    elif target in SECTIONS:
        for b in SECTIONS[target]:
            tasks.append((target, b))
    elif target in ALL_BOOKS:
        meta = ALL_BOOKS[target]
        tasks.append((meta["section"], meta))
    else:
        print(f"Desconocido: {target}")
        print("Secciones:", ", ".join(SECTIONS.keys()))
        print("Libros:", ", ".join(ALL_BOOKS.keys()))
        sys.exit(1)

    skip = (target == "all")
    total_errors = []
    for sec, meta in tasks:
        errs = fetch_book(sec, meta, skip_existing=skip)
        total_errors.extend(errs)

    print(f"\n=== COMPLETADO ===")
    print(f"Errores: {total_errors if total_errors else 'ninguno'}")


# Make urllib.parse available in fetch_chapter
import urllib.parse  # noqa

if __name__ == "__main__":
    main()
