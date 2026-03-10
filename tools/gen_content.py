#!/usr/bin/env python3
"""
Genera los archivos .md de content/ para cada capítulo.
Uso: python tools/gen_content.py bereshit
     python tools/gen_content.py all
"""
import json
import os
import sys

DATA_DIR = "data/torah"
CONTENT_DIR = "content/torah"

BOOKS = {
    "bereshit": {"title_he": "בְּרֵאשִׁית", "book_es": "Génesis", "order": 1},
    "shemot":   {"title_he": "שְׁמוֹת",    "book_es": "Éxodo",    "order": 2},
    "vayikra":  {"title_he": "וַיִּקְרָא", "book_es": "Levítico", "order": 3},
    "bamidbar": {"title_he": "בְּמִדְבַּר","book_es": "Números",  "order": 4},
    "devarim":  {"title_he": "דְּבָרִים",  "book_es": "Deuteronomio","order":5},
}


def gen_book(book):
    meta = BOOKS.get(book)
    if not meta:
        print(f"Libro desconocido: {book}")
        return

    data_dir = f"{DATA_DIR}/{book}"
    content_dir = f"{CONTENT_DIR}/{book}"
    os.makedirs(content_dir, exist_ok=True)

    files = sorted(f for f in os.listdir(data_dir) if f.endswith(".json"))
    count = 0
    for fname in files:
        path = f"{data_dir}/{fname}"
        with open(path, encoding="utf-8") as f:
            data = json.load(f)

        ch = data["chapter"]
        title_he = data.get("title_he", f"{meta['title_he']} {ch}")
        md_path = f"{content_dir}/{ch:03d}.md"

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

    print(f"✓ {book}: {count} archivos generados en {content_dir}/")


def main():
    if len(sys.argv) < 2:
        print("Uso: python tools/gen_content.py <libro|all>")
        sys.exit(1)

    arg = sys.argv[1]
    if arg == "all":
        for book in BOOKS:
            if os.path.isdir(f"{DATA_DIR}/{book}"):
                gen_book(book)
    else:
        gen_book(arg)


if __name__ == "__main__":
    main()
