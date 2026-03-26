#!/usr/bin/env python3
"""
Genera los archivos .md de content/ para cada capítulo del Tanaj.
Uso: python tools/gen_content.py bereshit
     python tools/gen_content.py all         (Torá completa)
     python tools/gen_content.py neviim      (todos los Profetas)
     python tools/gen_content.py ketuvim     (todos los Escritos)
     python tools/gen_content.py tanakh      (todo el Tanaj)
"""
import json
import os
import sys

# ── Torah ──────────────────────────────────────────────────────────────────
TORAH_BOOKS = {
    "bereshit": {"title_he": "בְּרֵאשִׁית", "book_es": "Génesis",      "order": 1},
    "shemot":   {"title_he": "שְׁמוֹת",     "book_es": "Éxodo",        "order": 2},
    "vayikra":  {"title_he": "וַיִּקְרָא",  "book_es": "Levítico",     "order": 3},
    "bamidbar": {"title_he": "בְּמִדְבַּר", "book_es": "Números",      "order": 4},
    "devarim":  {"title_he": "דְּבָרִים",   "book_es": "Deuteronomio", "order": 5},
}

# ── Nevi'im ────────────────────────────────────────────────────────────────
NEVIIM_BOOKS = {
    "yehoshua":     {"title_he": "יְהוֹשֻׁעַ",          "book_es": "Josué",                 "order": 1},
    "shoftim":      {"title_he": "שֹׁפְטִים",            "book_es": "Jueces",                "order": 2},
    "shmuel1":      {"title_he": "שְׁמוּאֵל א",          "book_es": "1 Samuel",              "order": 3},
    "shmuel2":      {"title_he": "שְׁמוּאֵל ב",          "book_es": "2 Samuel",              "order": 4},
    "melakhim1":    {"title_he": "מְלָכִים א",           "book_es": "1 Reyes",               "order": 5},
    "melakhim2":    {"title_he": "מְלָכִים ב",           "book_es": "2 Reyes",               "order": 6},
    "yeshayahu":    {"title_he": "יְשַׁעְיָהוּ",         "book_es": "Isaías",                "order": 7},
    "yirmiyahu":    {"title_he": "יִרְמְיָהוּ",          "book_es": "Jeremías",              "order": 8},
    "yehezkel":     {"title_he": "יְחֶזְקֵאל",           "book_es": "Ezequiel",              "order": 9},
    "hoshea":       {"title_he": "הוֹשֵׁעַ",             "book_es": "Oseas",                 "order": 10},
    "yoel":         {"title_he": "יוֹאֵל",               "book_es": "Joel",                  "order": 11},
    "amos":         {"title_he": "עָמוֹס",               "book_es": "Amós",                  "order": 12},
    "ovadyah":      {"title_he": "עֹבַדְיָה",            "book_es": "Abdías",                "order": 13},
    "yonah":        {"title_he": "יוֹנָה",               "book_es": "Jonás",                 "order": 14},
    "mikhah":       {"title_he": "מִיכָה",               "book_es": "Miqueas",               "order": 15},
    "nahum":        {"title_he": "נַחוּם",               "book_es": "Nahúm",                 "order": 16},
    "havakkuk":     {"title_he": "חֲבַקּוּק",            "book_es": "Habacuc",               "order": 17},
    "tzefanyah":    {"title_he": "צְפַנְיָה",            "book_es": "Sofonías",              "order": 18},
    "haggai":       {"title_he": "חַגַּי",               "book_es": "Hageo",                 "order": 19},
    "zekharyah":    {"title_he": "זְכַרְיָה",            "book_es": "Zacarías",              "order": 20},
    "malakhi":      {"title_he": "מַלְאָכִי",            "book_es": "Malaquías",             "order": 21},
}

# ── Ketuvim ────────────────────────────────────────────────────────────────
KETUVIM_BOOKS = {
    "tehilim":          {"title_he": "תְּהִלִּים",           "book_es": "Salmos",                    "order": 1},
    "mishlei":          {"title_he": "מִשְׁלֵי",             "book_es": "Proverbios",                "order": 2},
    "iyov":             {"title_he": "אִיּוֹב",              "book_es": "Job",                       "order": 3},
    "shir_hashirim":    {"title_he": "שִׁיר הַשִּׁירִים",    "book_es": "Cantar de los Cantares",    "order": 4},
    "rut":              {"title_he": "רוּת",                 "book_es": "Rut",                       "order": 5},
    "ekhah":            {"title_he": "אֵיכָה",               "book_es": "Lamentaciones",             "order": 6},
    "kohelet":          {"title_he": "קֹהֶלֶת",              "book_es": "Eclesiastés",               "order": 7},
    "esther":           {"title_he": "אֶסְתֵּר",             "book_es": "Ester",                     "order": 8},
    "daniel":           {"title_he": "דָּנִיֵּאל",           "book_es": "Daniel",                    "order": 9},
    "ezra":             {"title_he": "עֶזְרָא",              "book_es": "Esdras",                    "order": 10},
    "nekhemyah":        {"title_he": "נְחֶמְיָה",            "book_es": "Nehemías",                  "order": 11},
    "divreiy_hayamim1": {"title_he": "דִּבְרֵי הַיָּמִים א", "book_es": "1 Crónicas",                "order": 12},
    "divreiy_hayamim2": {"title_he": "דִּבְרֵי הַיָּמִים ב", "book_es": "2 Crónicas",                "order": 13},
}

SECTIONS = {
    "torah":   TORAH_BOOKS,
    "neviim":  NEVIIM_BOOKS,
    "ketuvim": KETUVIM_BOOKS,
}

SECTION_META = {
    "torah":   {"title_he": "הַתּוֹרָה",    "book_es": "La Torá",    "order": 1},
    "neviim":  {"title_he": "נְבִיאִים",    "book_es": "Profetas",   "order": 2},
    "ketuvim": {"title_he": "כְּתוּבִים",   "book_es": "Escritos",   "order": 3},
}


def ensure_section_index(section):
    """Create content/{section}/_index.md if missing."""
    meta = SECTION_META[section]
    index_path = f"content/{section}/_index.md"
    if not os.path.exists(index_path):
        os.makedirs(f"content/{section}", exist_ok=True)
        content = f"""---
title: "{meta['title_he']}"
book_es: "{meta['book_es']}"
order: {meta['order']}
---
"""
        with open(index_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"  ✓ creado {index_path}")


def ensure_book_index(section, book, meta):
    """Create content/{section}/{book}/_index.md if missing."""
    index_path = f"content/{section}/{book}/_index.md"
    if not os.path.exists(index_path):
        os.makedirs(f"content/{section}/{book}", exist_ok=True)
        content = f"""---
title: "{meta['title_he']}"
book_es: "{meta['book_es']}"
book: "{book}"
order: {meta['order']}
---
"""
        with open(index_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"  ✓ creado {index_path}")


def gen_book(section, book):
    meta = SECTIONS[section].get(book)
    if not meta:
        print(f"Libro desconocido: {book} en sección {section}")
        return

    data_dir    = f"data/{section}/{book}"
    content_dir = f"content/{section}/{book}"

    if not os.path.isdir(data_dir):
        print(f"  ✗ No existe {data_dir} — ejecuta fetch_tanakh.py primero")
        return

    ensure_section_index(section)
    ensure_book_index(section, book, meta)
    os.makedirs(content_dir, exist_ok=True)

    files = sorted(f for f in os.listdir(data_dir) if f.endswith(".json"))
    count = 0
    for fname in files:
        path = f"{data_dir}/{fname}"
        with open(path, encoding="utf-8") as f:
            data = json.load(f)

        ch = data["chapter"]
        title_he = data.get("title_he", f"{meta['title_he']} {ch}")
        md_path  = f"{content_dir}/{ch:03d}.md"

        content = f"""---
title: "{title_he}"
chapter: {ch}
book: "{book}"
book_es: "{meta['book_es']}"
weight: {ch}
---
"""
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(content)
        count += 1

    print(f"✓ {section}/{book}: {count} archivos en {content_dir}/")


def main():
    if len(sys.argv) < 2:
        print("Uso: python tools/gen_content.py <libro|sección|all|tanakh>")
        sys.exit(1)

    arg = sys.argv[1].lower()

    if arg in ("all", "torah"):
        for book in TORAH_BOOKS:
            if os.path.isdir(f"data/torah/{book}"):
                gen_book("torah", book)
    elif arg == "tanakh":
        for sec, books in SECTIONS.items():
            for book in books:
                if os.path.isdir(f"data/{sec}/{book}"):
                    gen_book(sec, book)
    elif arg in SECTIONS:
        for book in SECTIONS[arg]:
            if os.path.isdir(f"data/{arg}/{book}"):
                gen_book(arg, book)
    else:
        # Try to find book in any section
        found = False
        for sec, books in SECTIONS.items():
            if arg in books:
                gen_book(sec, arg)
                found = True
                break
        if not found:
            print(f"Desconocido: {arg}")
            sys.exit(1)


if __name__ == "__main__":
    main()
