#!/usr/bin/env python3
"""
gen_haftarot.py — Añade datos de haftará (tradición sefardí) a las parashot
y genera las páginas content/parashot/{slug}/haftara.md

Usage:
    python3 tools/gen_haftarot.py
"""

import json
from pathlib import Path

ROOT        = Path(__file__).parent.parent.resolve()
DATA_DIR    = ROOT / "data" / "parashot"
CONTENT_DIR = ROOT / "content" / "parashot"

# ─── Metadatos de libros de Nevi'im ──────────────────────────────────────────

LIBRO_META = {
    "yehoshua":  {"nombre": "Yehoshúa",    "nombre_he": "יְהוֹשֻׁעַ"},
    "shoftim":   {"nombre": "Shoftim",     "nombre_he": "שׁוֹפְטִים"},
    "shmuel1":   {"nombre": "Shemuel I",   "nombre_he": "שְׁמוּאֵל א"},
    "shmuel2":   {"nombre": "Shemuel II",  "nombre_he": "שְׁמוּאֵל ב"},
    "melakhim1": {"nombre": "Melakhim I",  "nombre_he": "מְלָכִים א"},
    "melakhim2": {"nombre": "Melakhim II", "nombre_he": "מְלָכִים ב"},
    "yeshayahu": {"nombre": "Yeshayahu",   "nombre_he": "יְשַׁעְיָהוּ"},
    "yirmiyahu": {"nombre": "Yirmiyahu",   "nombre_he": "יִרְמְיָהוּ"},
    "yehezkel":  {"nombre": "Yejezkel",    "nombre_he": "יְחֶזְקֵאל"},
    "hoshea":    {"nombre": "Hoshea",      "nombre_he": "הוֹשֵׁעַ"},
    "yoel":      {"nombre": "Yoel",        "nombre_he": "יוֹאֵל"},
    "amos":      {"nombre": "Amós",        "nombre_he": "עָמוֹס"},
    "ovadyah":   {"nombre": "Ovadyá",      "nombre_he": "עֹבַדְיָה"},
    "yonah":     {"nombre": "Yoná",        "nombre_he": "יוֹנָה"},
    "mikhah":    {"nombre": "Mikháh",      "nombre_he": "מִיכָה"},
    "nahum":     {"nombre": "Najúm",       "nombre_he": "נַחוּם"},
    "havakkuk":  {"nombre": "Javakúk",     "nombre_he": "חֲבַקּוּק"},
    "tzefanyah": {"nombre": "Tsefanyá",    "nombre_he": "צְפַנְיָה"},
    "haggai":    {"nombre": "Jagái",       "nombre_he": "חַגַּי"},
    "zekharyah": {"nombre": "Zejaryá",     "nombre_he": "זְכַרְיָה"},
    "malakhi":   {"nombre": "Malají",      "nombre_he": "מַלְאָכִי"},
}

# ─── Haftarot — tradición sefardí ────────────────────────────────────────────
# ranges: lista de {libro, ch_start, v_start, ch_end, v_end}
# Cuando hay varias rangos (o varios libros), el primero es el principal.

HAFTAROT = {
    # ══ BERESHIT ══════════════════════════════════════════════════════════════
    "bereshit-1": {  # Bereshit
        "ref_es": "Yeshayahu 42:5 – 43:10",
        "ranges": [{"libro": "yeshayahu", "ch_start": 42, "v_start": 5, "ch_end": 43, "v_end": 10}],
    },
    "bereshit-2": {  # Noaj
        "ref_es": "Yeshayahu 54:1 – 55:5",
        "ranges": [{"libro": "yeshayahu", "ch_start": 54, "v_start": 1, "ch_end": 55, "v_end": 5}],
    },
    "bereshit-3": {  # Lej-Lejá
        "ref_es": "Yeshayahu 40:27 – 41:16",
        "ranges": [{"libro": "yeshayahu", "ch_start": 40, "v_start": 27, "ch_end": 41, "v_end": 16}],
    },
    "bereshit-4": {  # Vayerá
        "ref_es": "Melakhim II 4:1–37",
        "ranges": [{"libro": "melakhim2", "ch_start": 4, "v_start": 1, "ch_end": 4, "v_end": 37}],
    },
    "bereshit-5": {  # Jayé Sará
        "ref_es": "Melakhim I 1:1–31",
        "ranges": [{"libro": "melakhim1", "ch_start": 1, "v_start": 1, "ch_end": 1, "v_end": 31}],
    },
    "bereshit-6": {  # Toledot
        "ref_es": "Malaji 1:1 – 2:7",
        "ranges": [{"libro": "malakhi", "ch_start": 1, "v_start": 1, "ch_end": 2, "v_end": 7}],
    },
    "bereshit-7": {  # Vayetsé — SEFARDÍ: Hoshea 11:7-12:12
        "ref_es": "Hoshea 11:7 – 12:12",
        "ranges": [{"libro": "hoshea", "ch_start": 11, "v_start": 7, "ch_end": 12, "v_end": 12}],
    },
    "bereshit-8": {  # Vayishláj
        "ref_es": "Ovadyá 1:1–21",
        "ranges": [{"libro": "ovadyah", "ch_start": 1, "v_start": 1, "ch_end": 1, "v_end": 21}],
    },
    "bereshit-9": {  # Vayeshev
        "ref_es": "Amós 2:6 – 3:8",
        "ranges": [{"libro": "amos", "ch_start": 2, "v_start": 6, "ch_end": 3, "v_end": 8}],
    },
    "bereshit-10": {  # Mikéts
        "ref_es": "Melakhim I 3:15 – 4:1",
        "ranges": [{"libro": "melakhim1", "ch_start": 3, "v_start": 15, "ch_end": 4, "v_end": 1}],
    },
    "bereshit-11": {  # Vayigash
        "ref_es": "Yejezkel 37:15–28",
        "ranges": [{"libro": "yehezkel", "ch_start": 37, "v_start": 15, "ch_end": 37, "v_end": 28}],
    },
    "bereshit-12": {  # Vayejí
        "ref_es": "Melakhim I 2:1–12",
        "ranges": [{"libro": "melakhim1", "ch_start": 2, "v_start": 1, "ch_end": 2, "v_end": 12}],
    },

    # ══ SHEMOT ════════════════════════════════════════════════════════════════
    "shemot-1": {  # Shemot
        "ref_es": "Yirmiyahu 1:1 – 2:3",
        "ranges": [{"libro": "yirmiyahu", "ch_start": 1, "v_start": 1, "ch_end": 2, "v_end": 3}],
    },
    "shemot-2": {  # Vaerá
        "ref_es": "Yejezkel 28:25 – 29:21",
        "ranges": [{"libro": "yehezkel", "ch_start": 28, "v_start": 25, "ch_end": 29, "v_end": 21}],
    },
    "shemot-3": {  # Bo
        "ref_es": "Yirmiyahu 46:13–28",
        "ranges": [{"libro": "yirmiyahu", "ch_start": 46, "v_start": 13, "ch_end": 46, "v_end": 28}],
    },
    "shemot-4": {  # Beshaláj
        "ref_es": "Shoftim 4:4 – 5:31",
        "ranges": [{"libro": "shoftim", "ch_start": 4, "v_start": 4, "ch_end": 5, "v_end": 31}],
    },
    "shemot-5": {  # Yitró — SEFARDÍ: solo 6:1-7:6
        "ref_es": "Yeshayahu 6:1 – 7:6",
        "ranges": [{"libro": "yeshayahu", "ch_start": 6, "v_start": 1, "ch_end": 7, "v_end": 6}],
    },
    "shemot-6": {  # Mishpatim
        "ref_es": "Yirmiyahu 34:8–22; 33:25–26",
        "ranges": [
            {"libro": "yirmiyahu", "ch_start": 34, "v_start": 8, "ch_end": 34, "v_end": 22},
            {"libro": "yirmiyahu", "ch_start": 33, "v_start": 25, "ch_end": 33, "v_end": 26},
        ],
    },
    "shemot-7": {  # Terumá
        "ref_es": "Melakhim I 5:26 – 6:13",
        "ranges": [{"libro": "melakhim1", "ch_start": 5, "v_start": 26, "ch_end": 6, "v_end": 13}],
    },
    "shemot-8": {  # Tetsavé
        "ref_es": "Yejezkel 43:10–27",
        "ranges": [{"libro": "yehezkel", "ch_start": 43, "v_start": 10, "ch_end": 43, "v_end": 27}],
    },
    "shemot-9": {  # Ki Tisá
        "ref_es": "Melakhim I 18:1–39",
        "ranges": [{"libro": "melakhim1", "ch_start": 18, "v_start": 1, "ch_end": 18, "v_end": 39}],
    },
    "shemot-10": {  # Vayakhel
        "ref_es": "Melakhim I 7:40–50",
        "ranges": [{"libro": "melakhim1", "ch_start": 7, "v_start": 40, "ch_end": 7, "v_end": 50}],
    },
    "shemot-11": {  # Pekudé
        "ref_es": "Melakhim I 7:51 – 8:21",
        "ranges": [{"libro": "melakhim1", "ch_start": 7, "v_start": 51, "ch_end": 8, "v_end": 21}],
    },

    # ══ VAYIKRA ═══════════════════════════════════════════════════════════════
    "vayikra-1": {  # Vayikrá
        "ref_es": "Yeshayahu 43:21 – 44:23",
        "ranges": [{"libro": "yeshayahu", "ch_start": 43, "v_start": 21, "ch_end": 44, "v_end": 23}],
    },
    "vayikra-2": {  # Tsav
        "ref_es": "Yirmiyahu 7:21 – 8:3; 9:22–23",
        "ranges": [
            {"libro": "yirmiyahu", "ch_start": 7, "v_start": 21, "ch_end": 8, "v_end": 3},
            {"libro": "yirmiyahu", "ch_start": 9, "v_start": 22, "ch_end": 9, "v_end": 23},
        ],
    },
    "vayikra-3": {  # Sheminí
        "ref_es": "Shemuel II 6:1 – 7:17",
        "ranges": [{"libro": "shmuel2", "ch_start": 6, "v_start": 1, "ch_end": 7, "v_end": 17}],
    },
    "vayikra-4": {  # Tazriá
        "ref_es": "Melakhim II 4:42 – 5:19",
        "ranges": [{"libro": "melakhim2", "ch_start": 4, "v_start": 42, "ch_end": 5, "v_end": 19}],
    },
    "vayikra-5": {  # Metsora
        "ref_es": "Melakhim II 7:3–20",
        "ranges": [{"libro": "melakhim2", "ch_start": 7, "v_start": 3, "ch_end": 7, "v_end": 20}],
    },
    "vayikra-6": {  # Ajaré Mot
        "ref_es": "Yejezkel 22:1–19",
        "ranges": [{"libro": "yehezkel", "ch_start": 22, "v_start": 1, "ch_end": 22, "v_end": 19}],
    },
    "vayikra-7": {  # Kedoshim — SEFARDÍ: Amós
        "ref_es": "Amós 9:7–15",
        "ranges": [{"libro": "amos", "ch_start": 9, "v_start": 7, "ch_end": 9, "v_end": 15}],
    },
    "vayikra-8": {  # Emor
        "ref_es": "Yejezkel 44:15–31",
        "ranges": [{"libro": "yehezkel", "ch_start": 44, "v_start": 15, "ch_end": 44, "v_end": 31}],
    },
    "vayikra-9": {  # Behar
        "ref_es": "Yirmiyahu 32:6–27",
        "ranges": [{"libro": "yirmiyahu", "ch_start": 32, "v_start": 6, "ch_end": 32, "v_end": 27}],
    },
    "vayikra-10": {  # Bejukotai
        "ref_es": "Yirmiyahu 16:19 – 17:14",
        "ranges": [{"libro": "yirmiyahu", "ch_start": 16, "v_start": 19, "ch_end": 17, "v_end": 14}],
    },

    # ══ BAMIDBAR ══════════════════════════════════════════════════════════════
    "bamidbar-1": {  # Bamidbar
        "ref_es": "Hoshea 2:1–22",
        "ranges": [{"libro": "hoshea", "ch_start": 2, "v_start": 1, "ch_end": 2, "v_end": 22}],
    },
    "bamidbar-2": {  # Nasó
        "ref_es": "Shoftim 13:2–25",
        "ranges": [{"libro": "shoftim", "ch_start": 13, "v_start": 2, "ch_end": 13, "v_end": 25}],
    },
    "bamidbar-3": {  # Behaálotjá
        "ref_es": "Zejaryá 2:14 – 4:7",
        "ranges": [{"libro": "zekharyah", "ch_start": 2, "v_start": 14, "ch_end": 4, "v_end": 7}],
    },
    "bamidbar-4": {  # Sheláj
        "ref_es": "Yehoshúa 2:1–24",
        "ranges": [{"libro": "yehoshua", "ch_start": 2, "v_start": 1, "ch_end": 2, "v_end": 24}],
    },
    "bamidbar-5": {  # Koráj
        "ref_es": "Shemuel I 11:14 – 12:22",
        "ranges": [{"libro": "shmuel1", "ch_start": 11, "v_start": 14, "ch_end": 12, "v_end": 22}],
    },
    "bamidbar-6": {  # Jukat
        "ref_es": "Shoftim 11:1–33",
        "ranges": [{"libro": "shoftim", "ch_start": 11, "v_start": 1, "ch_end": 11, "v_end": 33}],
    },
    "bamidbar-7": {  # Balak
        "ref_es": "Mikháh 5:6 – 6:8",
        "ranges": [{"libro": "mikhah", "ch_start": 5, "v_start": 6, "ch_end": 6, "v_end": 8}],
    },
    "bamidbar-8": {  # Pinjas
        "ref_es": "Melakhim I 18:46 – 19:21",
        "ranges": [{"libro": "melakhim1", "ch_start": 18, "v_start": 46, "ch_end": 19, "v_end": 21}],
    },
    "bamidbar-9": {  # Matot
        "ref_es": "Yirmiyahu 1:1 – 2:3",
        "ranges": [{"libro": "yirmiyahu", "ch_start": 1, "v_start": 1, "ch_end": 2, "v_end": 3}],
    },
    "bamidbar-10": {  # Masei
        "ref_es": "Yirmiyahu 2:4–28; 3:4",
        "ranges": [
            {"libro": "yirmiyahu", "ch_start": 2, "v_start": 4, "ch_end": 2, "v_end": 28},
            {"libro": "yirmiyahu", "ch_start": 3, "v_start": 4, "ch_end": 3, "v_end": 4},
        ],
    },

    # ══ DEVARIM ═══════════════════════════════════════════════════════════════
    "devarim-1": {  # Devarim
        "ref_es": "Yeshayahu 1:1–27",
        "ranges": [{"libro": "yeshayahu", "ch_start": 1, "v_start": 1, "ch_end": 1, "v_end": 27}],
    },
    "devarim-2": {  # Vaetjanán
        "ref_es": "Yeshayahu 40:1–26",
        "ranges": [{"libro": "yeshayahu", "ch_start": 40, "v_start": 1, "ch_end": 40, "v_end": 26}],
    },
    "devarim-3": {  # Ekev
        "ref_es": "Yeshayahu 49:14 – 51:3",
        "ranges": [{"libro": "yeshayahu", "ch_start": 49, "v_start": 14, "ch_end": 51, "v_end": 3}],
    },
    "devarim-4": {  # Reé
        "ref_es": "Yeshayahu 54:11 – 55:5",
        "ranges": [{"libro": "yeshayahu", "ch_start": 54, "v_start": 11, "ch_end": 55, "v_end": 5}],
    },
    "devarim-5": {  # Shoftim
        "ref_es": "Yeshayahu 51:12 – 52:12",
        "ranges": [{"libro": "yeshayahu", "ch_start": 51, "v_start": 12, "ch_end": 52, "v_end": 12}],
    },
    "devarim-6": {  # Ki Tetsé
        "ref_es": "Yeshayahu 54:1–10",
        "ranges": [{"libro": "yeshayahu", "ch_start": 54, "v_start": 1, "ch_end": 54, "v_end": 10}],
    },
    "devarim-7": {  # Ki Tavó
        "ref_es": "Yeshayahu 60:1–22",
        "ranges": [{"libro": "yeshayahu", "ch_start": 60, "v_start": 1, "ch_end": 60, "v_end": 22}],
    },
    "devarim-8": {  # Nitsavim
        "ref_es": "Yeshayahu 61:10 – 63:9",
        "ranges": [{"libro": "yeshayahu", "ch_start": 61, "v_start": 10, "ch_end": 63, "v_end": 9}],
    },
    "devarim-9": {  # Vayelej — SEFARDÍ: Hoshea + Mikháh
        "ref_es": "Hoshea 14:2–10; Mikháh 7:18–20",
        "ranges": [
            {"libro": "hoshea",  "ch_start": 14, "v_start": 2, "ch_end": 14, "v_end": 10},
            {"libro": "mikhah",  "ch_start": 7,  "v_start": 18,"ch_end": 7,  "v_end": 20},
        ],
    },
    "devarim-10": {  # Haazinú
        "ref_es": "Shemuel II 22:1–51",
        "ranges": [{"libro": "shmuel2", "ch_start": 22, "v_start": 1, "ch_end": 22, "v_end": 51}],
    },
    "devarim-11": {  # Vezot Haberajá
        "ref_es": "Yehoshúa 1:1–18",
        "ranges": [{"libro": "yehoshua", "ch_start": 1, "v_start": 1, "ch_end": 1, "v_end": 18}],
    },
}


def build_haftara_field(haf_data):
    """Builds the haftara dict to embed in the parasha JSON."""
    primary = haf_data["ranges"][0]
    meta = LIBRO_META.get(primary["libro"], {})
    return {
        "ref_es":       haf_data["ref_es"],
        "libro":        primary["libro"],
        "libro_nombre": meta.get("nombre", primary["libro"]),
        "libro_he":     meta.get("nombre_he", ""),
        "ranges":       haf_data["ranges"],
    }


def gen_haftara_md(slug, parasha_nombre, parasha_he):
    return f"""---
title: "Haftará — {parasha_nombre}"
layout: haftara
parasha_slug: {slug}
description: "Haftará de {parasha_nombre} — tradición sefardí"
---
"""


def main():
    updated = 0
    skipped = 0

    for slug, haf_data in HAFTAROT.items():
        data_path = DATA_DIR / f"{slug}.json"
        if not data_path.exists():
            print(f"  [!] No encontrado: {data_path}")
            skipped += 1
            continue

        # Update parasha data JSON
        with open(data_path, encoding="utf-8") as f:
            data = json.load(f)

        data["haftara"] = build_haftara_field(haf_data)

        with open(data_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        # Generate haftara content page
        haf_md_path = CONTENT_DIR / slug / "haftara.md"
        if not haf_md_path.parent.exists():
            print(f"  [!] Directorio no existe: {haf_md_path.parent}")
            skipped += 1
            continue

        with open(haf_md_path, "w", encoding="utf-8") as f:
            f.write(gen_haftara_md(
                slug,
                data.get("nombre", slug),
                data.get("nombre_he", ""),
            ))

        print(f"  ✓ {slug} → {haf_data['ref_es']}")
        updated += 1

    print(f"\nListo: {updated} haftarot generadas, {skipped} omitidas.")


if __name__ == "__main__":
    main()
