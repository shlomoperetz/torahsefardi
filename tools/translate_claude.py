#!/usr/bin/env python3
"""
Genera traducción española sefardí usando Claude API.
Uso:
  python tools/translate_claude.py bereshit 1        # traduce cap. 1
  python tools/translate_claude.py bereshit 1-10     # traduce caps. 1 a 10
  python tools/translate_claude.py bereshit all      # traduce todos

Requiere: pip install anthropic
Requiere: ANTHROPIC_API_KEY en entorno
"""
import json
import os
import sys
import time
import anthropic

DATA_DIR = "data/torah"

SYSTEM_PROMPT = """Eres un traductor experto de hebreo bíblico al español sefardí clásico.

NORMAS DE TRADUCCIÓN SEFARDÍ (obligatorias):
- ת = t (nunca "s" ashkenazí)
- ח = j (sonido aspirado, como "jamón")
- kamatz = a (pronunciación sefardí, no "o")
- צ = ts (nunca "tz")
- שׁ = sh, שׂ = s
- יהוה = "El Eterno" (siempre, en todas las apariciones)
- Pronombres referidos a Dios en MAYÚSCULA: Él, Su, Sus, Él, Le, Lo, etc.
- Terminología sefardí: "Señor" solo si no es יהוה; preferir vocabulario judeo-español cuando sea apropiado
- Mantén fidelidad al texto hebreo. No parafrasees. Sé literal pero elegante.
- No añadas notas ni explicaciones. Solo la traducción.

El output debe ser un array JSON con objetos {"num": N, "es": "traducción"}.
"""

def translate_chapter(client, book, chapter_data):
    verses = chapter_data["verses"]
    book_es = chapter_data.get("book_es", book)
    ch = chapter_data["chapter"]

    # Build the Hebrew text to send
    he_text = "\n".join(
        f'{v["num"]}. {v["he"]}' for v in verses
    )

    user_msg = f"""Traduce al español sefardí el capítulo {ch} de {book_es} (hebreo bíblico):

{he_text}

Responde ÚNICAMENTE con un array JSON:
[{{"num": 1, "es": "traducción del versículo 1"}}, {{"num": 2, "es": "traducción del versículo 2"}}, ...]"""

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_msg}],
    )

    raw = response.content[0].text.strip()

    # Extract JSON array from response
    start = raw.find("[")
    end = raw.rfind("]") + 1
    if start == -1 or end == 0:
        raise ValueError(f"No se encontró array JSON en la respuesta: {raw[:200]}")

    translations = json.loads(raw[start:end])
    return {str(v["num"]): v["es"] for v in translations}


def process_chapter(client, book, ch):
    path = f"{DATA_DIR}/{book}/{ch:03d}.json"
    if not os.path.exists(path):
        print(f"✗ No existe: {path}")
        return False

    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    # Skip if already translated
    if all(v.get("es") for v in data["verses"]):
        print(f"  (ya traducido) {book} {ch}")
        return True

    print(f"→ Traduciendo {book} {ch} ({len(data['verses'])} versículos)...")

    try:
        translations = translate_chapter(client, book, data)
        for v in data["verses"]:
            t = translations.get(str(v["num"]))
            if t:
                v["es"] = t
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"✓ {book} {ch} — {len(translations)} versículos traducidos")
        return True
    except Exception as e:
        print(f"✗ Error en {book} {ch}: {e}")
        return False


def main():
    if len(sys.argv) < 3:
        print("Uso: python tools/translate_claude.py <libro> <capítulo|rango|all>")
        print("Ejemplo: python tools/translate_claude.py bereshit 1")
        print("         python tools/translate_claude.py bereshit 1-5")
        print("         python tools/translate_claude.py bereshit all")
        sys.exit(1)

    book = sys.argv[1]
    ch_arg = sys.argv[2]

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERROR: Define ANTHROPIC_API_KEY en el entorno")
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)

    # Determine chapters to process
    book_dir = f"{DATA_DIR}/{book}"
    if not os.path.isdir(book_dir):
        print(f"ERROR: No existe el directorio {book_dir}")
        sys.exit(1)

    if ch_arg == "all":
        files = sorted(f for f in os.listdir(book_dir) if f.endswith(".json"))
        chapters = [int(f.replace(".json", "")) for f in files]
    elif "-" in ch_arg:
        start, end = ch_arg.split("-")
        chapters = list(range(int(start), int(end) + 1))
    else:
        chapters = [int(ch_arg)]

    print(f"Procesando {len(chapters)} capítulo(s) de {book}...")
    errors = []
    for ch in chapters:
        ok = process_chapter(client, book, ch)
        if not ok:
            errors.append(ch)
        if len(chapters) > 1:
            time.sleep(1.5)  # rate limit

    print(f"\n=== HECHO ===")
    print(f"Errores: {errors if errors else 'ninguno'}")


if __name__ == "__main__":
    main()
