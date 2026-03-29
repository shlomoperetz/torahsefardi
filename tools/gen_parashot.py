#!/usr/bin/env python3
"""Generate parashot data and content files."""

import json
import os
import re

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

    # Write _index.md
    index_path = os.path.join(content_dir, "_index.md")
    with open(index_path, "w", encoding="utf-8") as f:
        f.write("---\ntitle: \"Parashot\"\n---\n")
    print(f"Written: {index_path}")

    for p in PARASHOT:
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
            url = f"/torah/{p['libro']}/{ch_start:03d}/#v{v_start}"

            aliyot_out.append({
                "num": num,
                "num_he": HE_NUMS[num - 1] if 1 <= num <= 7 else str(num),
                "ch_start": ch_start,
                "v_start": v_start,
                "ch_end": ch_end,
                "v_end": v_end,
                "ref_es": ref_es,
                "url": url,
                "primera_he": primera_he,
                "primera_es": primera_es,
            })

        data_out = {
            "nombre": p["nombre"],
            "nombre_he": p["nombre_he"],
            "nombre_es": p["nombre_es"],
            "libro": p["libro"],
            "libro_es": p["libro_es"],
            "libro_he": p["libro_he"],
            "num": p["num"],
            "aliyot": aliyot_out,
        }

        # Write data file
        data_path = os.path.join(data_dir, f"{slug}.json")
        with open(data_path, "w", encoding="utf-8") as f:
            json.dump(data_out, f, ensure_ascii=False, indent=2)

        # Write content file
        content_path = os.path.join(content_dir, f"{slug}.md")
        # Escape quotes in strings for YAML
        nombre_he_esc = p["nombre_he"].replace('"', '\\"')
        nombre_es_esc = p["nombre_es"].replace('"', '\\"')
        libro_es_esc = p["libro_es"].replace('"', '\\"')
        with open(content_path, "w", encoding="utf-8") as f:
            f.write(f"""---
title: "{p['nombre']}"
nombre_he: "{nombre_he_esc}"
nombre_es: "{nombre_es_esc}"
slug_parasha: "{slug}"
libro: "{p['libro']}"
libro_es: "{libro_es_esc}"
num: {p['num']}
weight: {p['num']}
---
""")

        print(f"Written: {slug} ({len(aliyot_out)} aliyot)")

    print(f"\nDone. Generated {len(PARASHOT)} parashot.")


if __name__ == "__main__":
    main()
