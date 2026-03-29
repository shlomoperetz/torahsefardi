#!/usr/bin/env python3
"""Generate parashot data, content files, and JS lookup map."""

import json
import os
import re
import shutil

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PARASHOT = [
    {"slug":"bereshit-1", "nombre":"Bereshit",      "nombre_he":"בְּרֵאשִׁית",  "nombre_es":"En el principio",    "libro":"bereshit","libro_es":"Génesis",     "libro_he":"בְּרֵאשִׁית", "num":1},
    {"slug":"bereshit-2", "nombre":"Noaj",           "nombre_he":"נֹחַ",         "nombre_es":"Noaj",                "libro":"bereshit","libro_es":"Génesis",     "libro_he":"בְּרֵאשִׁית", "num":2},
    {"slug":"bereshit-3", "nombre":"Lej-Lejá",       "nombre_he":"לֶךְ-לְךָ",    "nombre_es":"Ve a ti mismo",       "libro":"bereshit","libro_es":"Génesis",     "libro_he":"בְּרֵאשִׁית", "num":3},
    {"slug":"bereshit-4", "nombre":"Vayerá",         "nombre_he":"וַיֵּרָא",     "nombre_es":"Y se apareció",       "libro":"bereshit","libro_es":"Génesis",     "libro_he":"בְּרֵאשִׁית", "num":4},
    {"slug":"bereshit-5", "nombre":"Jayé Sará",      "nombre_he":"חַיֵּי שָׂרָה","nombre_es":"Vida de Sara",        "libro":"bereshit","libro_es":"Génesis",     "libro_he":"בְּרֵאשִׁית", "num":5},
    {"slug":"bereshit-6", "nombre":"Toledot",        "nombre_he":"תּוֹלְדֹת",    "nombre_es":"Generaciones",        "libro":"bereshit","libro_es":"Génesis",     "libro_he":"בְּרֵאשִׁית", "num":6},
    {"slug":"bereshit-7", "nombre":"Vayetsé",        "nombre_he":"וַיֵּצֵא",     "nombre_es":"Y salió",             "libro":"bereshit","libro_es":"Génesis",     "libro_he":"בְּרֵאשִׁית", "num":7},
    {"slug":"bereshit-8", "nombre":"Vayishláj",      "nombre_he":"וַיִּשְׁלַח",  "nombre_es":"Y envió",             "libro":"bereshit","libro_es":"Génesis",     "libro_he":"בְּרֵאשִׁית", "num":8},
    {"slug":"bereshit-9", "nombre":"Vayeshev",       "nombre_he":"וַיֵּשֶׁב",    "nombre_es":"Y se asentó",         "libro":"bereshit","libro_es":"Génesis",     "libro_he":"בְּרֵאשִׁית", "num":9},
    {"slug":"bereshit-10","nombre":"Mikéts",         "nombre_he":"מִקֵּץ",       "nombre_es":"Al cabo de",          "libro":"bereshit","libro_es":"Génesis",     "libro_he":"בְּרֵאשִׁית", "num":10},
    {"slug":"bereshit-11","nombre":"Vayigash",       "nombre_he":"וַיִּגַּשׁ",   "nombre_es":"Y se acercó",         "libro":"bereshit","libro_es":"Génesis",     "libro_he":"בְּרֵאשִׁית", "num":11},
    {"slug":"bereshit-12","nombre":"Vayejí",         "nombre_he":"וַיְחִי",      "nombre_es":"Y vivió",             "libro":"bereshit","libro_es":"Génesis",     "libro_he":"בְּרֵאשִׁית", "num":12},
    {"slug":"shemot-1",   "nombre":"Shemot",         "nombre_he":"שְׁמוֹת",      "nombre_es":"Nombres",             "libro":"shemot",  "libro_es":"Éxodo",       "libro_he":"שְׁמוֹת",    "num":1},
    {"slug":"shemot-2",   "nombre":"Vaerá",          "nombre_he":"וָאֵרָא",      "nombre_es":"Y me aparecí",        "libro":"shemot",  "libro_es":"Éxodo",       "libro_he":"שְׁמוֹת",    "num":2},
    {"slug":"shemot-3",   "nombre":"Bo",             "nombre_he":"בֹּא",         "nombre_es":"Entra",               "libro":"shemot",  "libro_es":"Éxodo",       "libro_he":"שְׁמוֹת",    "num":3},
    {"slug":"shemot-4",   "nombre":"Beshaláj",       "nombre_he":"בְּשַׁלַּח",   "nombre_es":"Cuando dejó ir",      "libro":"shemot",  "libro_es":"Éxodo",       "libro_he":"שְׁמוֹת",    "num":4},
    {"slug":"shemot-5",   "nombre":"Yitró",          "nombre_he":"יִתְרוֹ",      "nombre_es":"Yitró",               "libro":"shemot",  "libro_es":"Éxodo",       "libro_he":"שְׁמוֹת",    "num":5},
    {"slug":"shemot-6",   "nombre":"Mishpatim",      "nombre_he":"מִשְׁפָּטִים", "nombre_es":"Leyes",               "libro":"shemot",  "libro_es":"Éxodo",       "libro_he":"שְׁמוֹת",    "num":6},
    {"slug":"shemot-7",   "nombre":"Terumá",         "nombre_he":"תְּרוּמָה",    "nombre_es":"Ofrenda",             "libro":"shemot",  "libro_es":"Éxodo",       "libro_he":"שְׁמוֹת",    "num":7},
    {"slug":"shemot-8",   "nombre":"Tetsavé",        "nombre_he":"תְּצַוֶּה",    "nombre_es":"Ordenarás",           "libro":"shemot",  "libro_es":"Éxodo",       "libro_he":"שְׁמוֹת",    "num":8},
    {"slug":"shemot-9",   "nombre":"Ki Tisá",        "nombre_he":"כִּי תִשָּׂא",  "nombre_es":"Cuando tomes",        "libro":"shemot",  "libro_es":"Éxodo",       "libro_he":"שְׁמוֹת",    "num":9},
    {"slug":"shemot-10",  "nombre":"Vayakhel",       "nombre_he":"וַיַּקְהֵל",   "nombre_es":"Y congregó",          "libro":"shemot",  "libro_es":"Éxodo",       "libro_he":"שְׁמוֹת",    "num":10},
    {"slug":"shemot-11",  "nombre":"Pekudé",         "nombre_he":"פְקוּדֵי",     "nombre_es":"Cuentas de",          "libro":"shemot",  "libro_es":"Éxodo",       "libro_he":"שְׁמוֹת",    "num":11},
    {"slug":"vayikra-1",  "nombre":"Vayikrá",        "nombre_he":"וַיִּקְרָא",   "nombre_es":"Y llamó",             "libro":"vayikra", "libro_es":"Levítico",    "libro_he":"וַיִּקְרָא", "num":1},
    {"slug":"vayikra-2",  "nombre":"Tsav",           "nombre_he":"צַו",          "nombre_es":"Ordena",              "libro":"vayikra", "libro_es":"Levítico",    "libro_he":"וַיִּקְרָא", "num":2},
    {"slug":"vayikra-3",  "nombre":"Sheminí",        "nombre_he":"שְּׁמִינִי",   "nombre_es":"Octavo",              "libro":"vayikra", "libro_es":"Levítico",    "libro_he":"וַיִּקְרָא", "num":3},
    {"slug":"vayikra-4",  "nombre":"Tazriá",         "nombre_he":"תַזְרִיעַ",    "nombre_es":"Cuando conciba",      "libro":"vayikra", "libro_es":"Levítico",    "libro_he":"וַיִּקְרָא", "num":4},
    {"slug":"vayikra-5",  "nombre":"Metsora",        "nombre_he":"מְצֹרָע",      "nombre_es":"El leproso",          "libro":"vayikra", "libro_es":"Levítico",    "libro_he":"וַיִּקְרָא", "num":5},
    {"slug":"vayikra-6",  "nombre":"Ajaré Mot",      "nombre_he":"אַחֲרֵי מוֹת", "nombre_es":"Tras la muerte",      "libro":"vayikra", "libro_es":"Levítico",    "libro_he":"וַיִּקְרָא", "num":6},
    {"slug":"vayikra-7",  "nombre":"Kedoshim",       "nombre_he":"קְדֹשִׁים",    "nombre_es":"Santos seréis",       "libro":"vayikra", "libro_es":"Levítico",    "libro_he":"וַיִּקְרָא", "num":7},
    {"slug":"vayikra-8",  "nombre":"Emor",           "nombre_he":"אֱמֹר",        "nombre_es":"Di",                  "libro":"vayikra", "libro_es":"Levítico",    "libro_he":"וַיִּקְרָא", "num":8},
    {"slug":"vayikra-9",  "nombre":"Behar",          "nombre_he":"בְּהַר",       "nombre_es":"En el monte",         "libro":"vayikra", "libro_es":"Levítico",    "libro_he":"וַיִּקְרָא", "num":9},
    {"slug":"vayikra-10", "nombre":"Bejukotai",      "nombre_he":"בְּחֻקֹּתַי",  "nombre_es":"En mis estatutos",    "libro":"vayikra", "libro_es":"Levítico",    "libro_he":"וַיִּקְרָא", "num":10},
    {"slug":"bamidbar-1", "nombre":"Bamidbar",       "nombre_he":"בַּמִּדְבַּר", "nombre_es":"En el desierto",      "libro":"bamidbar","libro_es":"Números",     "libro_he":"בַּמִּדְבַּר","num":1},
    {"slug":"bamidbar-2", "nombre":"Nasó",           "nombre_he":"נָשֹׂא",       "nombre_es":"Eleva",               "libro":"bamidbar","libro_es":"Números",     "libro_he":"בַּמִּדְבַּר","num":2},
    {"slug":"bamidbar-3", "nombre":"Behaálotjá",     "nombre_he":"בְּהַעֲלֹתְךָ","nombre_es":"Al encender",         "libro":"bamidbar","libro_es":"Números",     "libro_he":"בַּמִּדְבַּר","num":3},
    {"slug":"bamidbar-4", "nombre":"Sheláj",         "nombre_he":"שְׁלַח",       "nombre_es":"Envía",               "libro":"bamidbar","libro_es":"Números",     "libro_he":"בַּמִּדְבַּר","num":4},
    {"slug":"bamidbar-5", "nombre":"Koráj",          "nombre_he":"קֹרַח",        "nombre_es":"Koraj",               "libro":"bamidbar","libro_es":"Números",     "libro_he":"בַּמִּדְבַּר","num":5},
    {"slug":"bamidbar-6", "nombre":"Jukat",          "nombre_he":"חֻקַּת",       "nombre_es":"Estatuto",            "libro":"bamidbar","libro_es":"Números",     "libro_he":"בַּמִּדְבַּר","num":6},
    {"slug":"bamidbar-7", "nombre":"Balak",          "nombre_he":"בָּלָק",       "nombre_es":"Balak",               "libro":"bamidbar","libro_es":"Números",     "libro_he":"בַּמִּדְבַּר","num":7},
    {"slug":"bamidbar-8", "nombre":"Pinjas",         "nombre_he":"פִּינְחָס",    "nombre_es":"Pinjas",              "libro":"bamidbar","libro_es":"Números",     "libro_he":"בַּמִּדְבַּר","num":8},
    {"slug":"bamidbar-9", "nombre":"Matot",          "nombre_he":"מַטּוֹת",      "nombre_es":"Tribus",              "libro":"bamidbar","libro_es":"Números",     "libro_he":"בַּמִּדְבַּר","num":9},
    {"slug":"bamidbar-10","nombre":"Masei",          "nombre_he":"מַסְעֵי",      "nombre_es":"Jornadas",            "libro":"bamidbar","libro_es":"Números",     "libro_he":"בַּמִּדְבַּר","num":10},
    {"slug":"devarim-1",  "nombre":"Devarim",        "nombre_he":"דְּבָרִים",    "nombre_es":"Palabras",            "libro":"devarim", "libro_es":"Deuteronomio","libro_he":"דְּבָרִים",  "num":1},
    {"slug":"devarim-2",  "nombre":"Vaetjanán",      "nombre_he":"וָאֶתְחַנַּן", "nombre_es":"Y supliqué",          "libro":"devarim", "libro_es":"Deuteronomio","libro_he":"דְּבָרִים",  "num":2},
    {"slug":"devarim-3",  "nombre":"Ekev",           "nombre_he":"עֵקֶב",        "nombre_es":"A causa de",          "libro":"devarim", "libro_es":"Deuteronomio","libro_he":"דְּבָרִים",  "num":3},
    {"slug":"devarim-4",  "nombre":"Reé",            "nombre_he":"רְאֵה",        "nombre_es":"Mira",                "libro":"devarim", "libro_es":"Deuteronomio","libro_he":"דְּבָרִים",  "num":4},
    {"slug":"devarim-5",  "nombre":"Shoftim",        "nombre_he":"שֹׁפְטִים",    "nombre_es":"Jueces",              "libro":"devarim", "libro_es":"Deuteronomio","libro_he":"דְּבָרִים",  "num":5},
    {"slug":"devarim-6",  "nombre":"Ki Tetsé",       "nombre_he":"כִּי-תֵצֵא",   "nombre_es":"Cuando salgas",       "libro":"devarim", "libro_es":"Deuteronomio","libro_he":"דְּבָרִים",  "num":6},
    {"slug":"devarim-7",  "nombre":"Ki Tavó",        "nombre_he":"כִּי-תָבוֹא",  "nombre_es":"Cuando entres",       "libro":"devarim", "libro_es":"Deuteronomio","libro_he":"דְּבָרִים",  "num":7},
    {"slug":"devarim-8",  "nombre":"Nitsavim",       "nombre_he":"נִצָּבִים",    "nombre_es":"Estáis de pie",       "libro":"devarim", "libro_es":"Deuteronomio","libro_he":"דְּבָרִים",  "num":8},
    {"slug":"devarim-9",  "nombre":"Vayelej",        "nombre_he":"וַיֵּלֶךְ",    "nombre_es":"Y fue",               "libro":"devarim", "libro_es":"Deuteronomio","libro_he":"דְּבָרִים",  "num":9},
    {"slug":"devarim-10", "nombre":"Haazinú",        "nombre_he":"הַאֲזִינוּ",   "nombre_es":"Escuchad",            "libro":"devarim", "libro_es":"Deuteronomio","libro_he":"דְּבָרִים",  "num":10},
    {"slug":"devarim-11", "nombre":"Vezot Haberajá", "nombre_he":"וְזֹאת הַבְּרָכָה","nombre_es":"Esta es la bendición","libro":"devarim","libro_es":"Deuteronomio","libro_he":"דְּבָרִים","num":11},
]

# Schedule 5786 diaspora (Shabbat date → parasha slug, None = holiday break)
PARASHA_SCHEDULE = [
    ("2025-10-18", "bereshit-1"),
    ("2025-10-25", "bereshit-2"),
    ("2025-11-01", "bereshit-3"),
    ("2025-11-08", "bereshit-4"),
    ("2025-11-15", "bereshit-5"),
    ("2025-11-22", "bereshit-6"),
    ("2025-11-29", "bereshit-7"),
    ("2025-12-06", "bereshit-8"),
    ("2025-12-13", "bereshit-9"),
    ("2025-12-20", "bereshit-10"),
    ("2025-12-27", "bereshit-11"),
    ("2026-01-03", "bereshit-12"),
    ("2026-01-10", "shemot-1"),
    ("2026-01-17", "shemot-2"),
    ("2026-01-24", "shemot-3"),
    ("2026-01-31", "shemot-4"),
    ("2026-02-07", "shemot-5"),
    ("2026-02-14", "shemot-6"),
    ("2026-02-21", "shemot-7"),
    ("2026-02-28", "shemot-8"),
    ("2026-03-07", "shemot-9"),
    ("2026-03-14", "shemot-10"),   # Vayakhel-Pekudei combinadas
    ("2026-03-21", "vayikra-1"),
    ("2026-03-28", "vayikra-2"),
    # Apr 4 = Shabbat Jol HaMoed Pesaj
    ("2026-04-11", "vayikra-3"),
    ("2026-04-18", "vayikra-4"),   # Tazriá-Metsora combinadas
    ("2026-04-25", "vayikra-6"),   # Ajaré Mot-Kedoshim combinadas
    ("2026-05-02", "vayikra-8"),
    ("2026-05-09", "vayikra-9"),   # Behar-Bejukotai combinadas
    ("2026-05-16", "bamidbar-1"),
    ("2026-05-23", "bamidbar-2"),
    ("2026-05-30", "bamidbar-3"),
    ("2026-06-06", "bamidbar-4"),
    ("2026-06-13", "bamidbar-5"),
    ("2026-06-20", "bamidbar-6"),
    ("2026-06-27", "bamidbar-7"),
    ("2026-07-04", "bamidbar-8"),
    ("2026-07-11", "bamidbar-9"),  # Matot-Masei combinadas
    ("2026-07-18", "devarim-1"),
    ("2026-07-25", "devarim-2"),
    ("2026-08-01", "devarim-3"),
    ("2026-08-08", "devarim-4"),
    ("2026-08-15", "devarim-5"),
    ("2026-08-22", "devarim-6"),
    ("2026-08-29", "devarim-7"),
    ("2026-09-05", "devarim-8"),   # Nitsavim-Vayelej combinadas
    # Sep 12 = RH / Sep 19 = Shabbat Shuva / Sep 26 = Sucot
    ("2026-10-03", "devarim-10"),  # Haazinú (Shabbat Shuva 5787)
]

HE_NUMS = ["א","ב","ג","ד","ה","ו","ז"]

BOOK_ABBR = {
    "bereshit": "Gén",
    "shemot": "Éx",
    "vayikra": "Lev",
    "bamidbar": "Núm",
    "devarim": "Deut",
}


def slug_to_cache_key(slug):
    parts = slug.split('-')
    libro = parts[0].capitalize()
    num = parts[-1]
    return f"{libro}_{num}"


def strip_html(text):
    return re.sub(r'<[^>]+>', '', text)


def load_chapter(libro, ch):
    path = os.path.join(BASE, "data", "torah", libro, f"{ch:03d}.json")
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def get_verse(libro, ch, v_num):
    data = load_chapter(libro, ch)
    if not data:
        return None, None
    for v in data.get("verses", []):
        if v["num"] == v_num:
            he_raw = v.get("he", "")
            he_clean = strip_html(he_raw)
            es = v.get("es", "")
            return he_clean[:60] + ("..." if len(he_clean) > 60 else ""), \
                   es[:80] + ("..." if len(es) > 80 else "")
    return None, None


def make_ref_es(libro, ch_start, v_start, ch_end, v_end):
    abbr = BOOK_ABBR.get(libro, libro)
    if ch_start == ch_end:
        return f"{abbr} {ch_start}:{v_start}–{v_end}"
    else:
        return f"{abbr} {ch_start}:{v_start}–{ch_end}:{v_end}"


def escape_yaml(s):
    return s.replace('"', '\\"')


def main():
    # Load aliyot cache
    cache_path = os.path.join(BASE, "tools", "aliyot_cache.json")
    with open(cache_path, encoding="utf-8") as f:
        aliyot_cache = json.load(f)

    # Create output dirs
    data_dir = os.path.join(BASE, "data", "parashot")
    content_dir = os.path.join(BASE, "content", "parashot")
    os.makedirs(data_dir, exist_ok=True)
    os.makedirs(content_dir, exist_ok=True)

    # Clean up old leaf .md files (not _index.md, not directories)
    for fname in os.listdir(content_dir):
        fpath = os.path.join(content_dir, fname)
        if fname != "_index.md" and fname.endswith(".md") and os.path.isfile(fpath):
            os.remove(fpath)
            print(f"Removed old: {fpath}")

    # Write section _index.md
    index_path = os.path.join(content_dir, "_index.md")
    with open(index_path, "w", encoding="utf-8") as f:
        f.write("---\ntitle: \"Parashot\"\n---\n")
    print(f"Written: {index_path}")

    # Build parasha data with global_num, prev_slug, next_slug
    all_data = []  # ordered list of (slug, data_out, p)

    for global_num, p in enumerate(PARASHOT, start=1):
        slug = p["slug"]
        cache_key = slug_to_cache_key(slug)
        aliyot_raw = aliyot_cache.get(cache_key, [])

        aliyot_out = []
        for a in aliyot_raw:
            num = a["num"]
            ch_start = a["ch_start"]
            v_start = a["v_start"]
            ch_end = a["ch_end"]
            v_end = a["v_end"]

            primera_he, primera_es = get_verse(p["libro"], ch_start, v_start)
            primera_he = primera_he or ""
            primera_es = primera_es or ""

            ref_es = make_ref_es(p["libro"], ch_start, v_start, ch_end, v_end)

            aliyot_out.append({
                "num": num,
                "num_he": HE_NUMS[num - 1] if 1 <= num <= 7 else str(num),
                "ch_start": ch_start,
                "v_start": v_start,
                "ch_end": ch_end,
                "v_end": v_end,
                "ref_es": ref_es,
                "primera_he": primera_he,
                "primera_es": primera_es,
            })

        prev_slug = PARASHOT[global_num - 2]["slug"] if global_num > 1 else ""
        next_slug = PARASHOT[global_num]["slug"] if global_num < len(PARASHOT) else ""

        data_out = {
            "slug": slug,
            "nombre": p["nombre"],
            "nombre_he": p["nombre_he"],
            "nombre_es": p["nombre_es"],
            "libro": p["libro"],
            "libro_es": p["libro_es"],
            "libro_he": p["libro_he"],
            "num": p["num"],
            "global_num": global_num,
            "prev_slug": prev_slug,
            "next_slug": next_slug,
            "aliyot": aliyot_out,
        }
        all_data.append((slug, data_out, p, global_num))

    # Write data files and content files
    for slug, data_out, p, global_num in all_data:
        # Write data file
        data_path = os.path.join(data_dir, f"{slug}.json")
        with open(data_path, "w", encoding="utf-8") as f:
            json.dump(data_out, f, ensure_ascii=False, indent=2)

        # Create branch bundle directory
        parasha_dir = os.path.join(content_dir, slug)
        os.makedirs(parasha_dir, exist_ok=True)

        # Write branch bundle _index.md
        index_md = os.path.join(parasha_dir, "_index.md")
        with open(index_md, "w", encoding="utf-8") as f:
            f.write(f"""---
title: "{escape_yaml(p['nombre'])}"
nombre_he: "{escape_yaml(p['nombre_he'])}"
nombre_es: "{escape_yaml(p['nombre_es'])}"
slug_parasha: "{slug}"
libro: "{p['libro']}"
libro_es: "{escape_yaml(p['libro_es'])}"
num: {p['num']}
global_num: {global_num}
weight: {global_num}
layout: parasha
---
""")

        # Write aliyah content files
        aliyot = data_out["aliyot"]
        for a in aliyot:
            n = a["num"]
            prev_aliya_url = ""
            if n > 1:
                prev_aliya_url = f"/parashot/{slug}/aliya-{n-1}/"
            elif data_out["prev_slug"]:
                prev_aliya_url = f"/parashot/{data_out['prev_slug']}/aliya-7/"

            next_aliya_url = ""
            if n < 7:
                next_aliya_url = f"/parashot/{slug}/aliya-{n+1}/"
            elif data_out["next_slug"]:
                next_aliya_url = f"/parashot/{data_out['next_slug']}/aliya-1/"

            aliya_md = os.path.join(parasha_dir, f"aliya-{n}.md")
            with open(aliya_md, "w", encoding="utf-8") as f:
                f.write(f"""---
title: "{escape_yaml(p['nombre'])} · Lectura {n}"
parasha_slug: "{slug}"
parasha_nombre: "{escape_yaml(p['nombre'])}"
parasha_nombre_he: "{escape_yaml(p['nombre_he'])}"
parasha_url: "/parashot/{slug}/"
libro: "{p['libro']}"
global_num: {global_num}
aliya_num: {n}
aliya_num_he: "{a['num_he']}"
ch_start: {a['ch_start']}
v_start: {a['v_start']}
ch_end: {a['ch_end']}
v_end: {a['v_end']}
ref_es: "{escape_yaml(a['ref_es'])}"
prev_aliya_url: "{prev_aliya_url}"
next_aliya_url: "{next_aliya_url}"
layout: aliya
---
""")

        print(f"Written: {slug} (global #{global_num}, {len(aliyot)} aliyot)")

    # --- Generate static/js/parasha-map.js ---
    # Build PARASHA_MAP: {libro: [{ch, v, slug, nombre, nombre_he, aliya_num, aliya_num_he},...]}
    parasha_map = {}
    for slug, data_out, p, global_num in all_data:
        libro = p["libro"]
        if libro not in parasha_map:
            parasha_map[libro] = []
        for a in data_out["aliyot"]:
            parasha_map[libro].append({
                "ch": a["ch_start"],
                "v": a["v_start"],
                "slug": slug,
                "nombre": p["nombre"],
                "nombre_he": p["nombre_he"],
                "aliya_num": a["num"],
                "aliya_num_he": a["num_he"],
                "aliya_url": f"/parashot/{slug}/aliya-{a['num']}/",
                "parasha_url": f"/parashot/{slug}/",
            })

    # Sort each libro's entries by ch then v
    for libro in parasha_map:
        parasha_map[libro].sort(key=lambda x: (x["ch"], x["v"]))

    # Build PARASHA_INFO: slug → {nombre, nombre_he, url}
    parasha_info = {}
    for slug, data_out, p, global_num in all_data:
        parasha_info[slug] = {
            "nombre": p["nombre"],
            "nombre_he": p["nombre_he"],
            "url": f"/parashot/{slug}/",
        }

    # Build schedule as list of [date, slug_or_null]
    schedule_js = []
    for date, slug in PARASHA_SCHEDULE:
        schedule_js.append([date, slug])

    js_path = os.path.join(BASE, "static", "js", "parasha-map.js")
    os.makedirs(os.path.dirname(js_path), exist_ok=True)
    with open(js_path, "w", encoding="utf-8") as f:
        f.write("// Auto-generated by gen_parashot.py — do not edit\n")
        f.write(f"var PARASHA_MAP={json.dumps(parasha_map, ensure_ascii=False)};\n")
        f.write(f"var PARASHA_INFO={json.dumps(parasha_info, ensure_ascii=False)};\n")
        f.write(f"var PARASHA_SCHEDULE={json.dumps(schedule_js, ensure_ascii=False)};\n")
    print(f"\nWritten: {js_path}")
    print(f"Done. Generated {len(PARASHOT)} parashot, {len(PARASHOT)*7} aliyot.")


if __name__ == "__main__":
    main()
