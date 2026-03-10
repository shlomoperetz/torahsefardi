# Torah Sefardí

La Torá en hebreo con traducción al español sefardí. Stack: Hugo + tema propio + Cloudflare Pages + datos en JSON.

## Estructura

```
data/torah/<libro>/<cap>.json   # Hebreo (Sefaria) + traducción sefardí
content/torah/<libro>/<cap>.md  # Front matter para Hugo
themes/minitorah/               # Tema Hugo personalizado
tools/                          # Scripts de fetch y traducción
```

## Setup

```bash
# Instalar Hugo
# Instalar dependencias Python
pip install anthropic

# Descargar hebreo de Sefaria
python tools/fetch_bereshit.py

# Traducir con Claude (requiere ANTHROPIC_API_KEY)
export ANTHROPIC_API_KEY=sk-...
python tools/translate_claude.py bereshit 1      # cap. 1
python tools/translate_claude.py bereshit 1-10   # caps. 1-10
python tools/translate_claude.py bereshit all    # todos

# Generar archivos content/
python tools/gen_content.py bereshit

# Servidor de desarrollo
hugo server
```

## Normas de traducción sefardí

- ת = t | ח = j | kamatz = a | צ = ts | שׁ = sh | שׂ = s
- יהוה = «El Eterno»
- Pronombres divinos en mayúscula: Él, Su, Sus, Le…

## Despliegue

Cloudflare Pages — rama `main`, comando `hugo --minify`, directorio `public/`.
