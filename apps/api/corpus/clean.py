"""Limpia el markdown crudo de docs (FastAPI MkDocs / Supabase MDX) a texto plano
apto para el corpus RAG.

De _raw/*.md|*.mdx produce ./*.md limpios:
- saca frontmatter YAML (y usa su `title` si existe)
- saca includes de MkDocs `{* ... *}` y anclas `{ #id }`
- saca marcadores de admonition/tab `///`, `////`
- saca componentes JSX de MDX (<Tabs>, <TabPanel>, <Admonition>, <$Partial/>...)
- saca tags HTML inline (<dfn>, <abbr>) y comentarios
- colapsa líneas en blanco de más

Uso:  python corpus/clean.py
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

RAW = Path(__file__).parent / "_raw"
OUT = Path(__file__).parent / "docs"


def _extract_frontmatter_title(text: str) -> tuple[str, str | None]:
    """Devuelve (texto_sin_frontmatter, title|None)."""
    if not text.startswith("---"):
        return text, None
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, flags=re.S)
    if not m:
        return text, None
    fm = m.group(1)
    tm = re.search(r"^title:\s*['\"]?(.+?)['\"]?\s*$", fm, flags=re.M)
    title = tm.group(1).strip() if tm else None
    return text[m.end():], title


def clean(text: str) -> tuple[str, str | None]:
    text, title = _extract_frontmatter_title(text)

    # MkDocs includes de código externo y anclas de heading
    text = re.sub(r"(?m)^\s*\{\*.*?\*\}\s*$\n?", "", text)
    text = re.sub(r"\s*\{\s*#[^}]*\}", "", text)

    # Marcadores de admonition / tabs de MkDocs (/// tip, ///, //// tab | ...)
    text = re.sub(r"(?m)^\s*/{3,}.*$\n?", "", text)

    # Comentarios HTML
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)

    # Componentes MDX: <Componente ...> / </Componente> / <$Partial .../>
    text = re.sub(r"<\$[^>]*?>", "", text, flags=re.S)
    text = re.sub(r"<[A-Z][A-Za-z0-9.]*\b[^>]*?/?>", "", text, flags=re.S)
    text = re.sub(r"</[A-Z][A-Za-z0-9.]*>", "", text)

    # HTML en minúscula (div, iframe, img, br, span...) preservando autolinks <http...>
    # (el patrón exige `>` inmediato o un espacio tras el nombre; `<https://x>` no matchea).
    text = re.sub(r"</?[a-z][a-z0-9]*(?:\s[^>]*?)?>", "", text, flags=re.S)

    # Tags HTML inline sueltos
    text = re.sub(r"</?(?:dfn|abbr)\b[^>]*>", "", text)

    # Colapsar 3+ líneas en blanco a 2
    text = re.sub(r"\n{3,}", "\n\n", text).strip()

    # Asegurar un título de primer nivel
    if title and not text.lstrip().startswith("#"):
        text = f"# {title}\n\n{text}"

    return text, title


def main() -> None:
    if not RAW.is_dir():
        print(f"No existe {RAW}")
        sys.exit(1)

    files = sorted(p for p in RAW.iterdir() if p.suffix in {".md", ".mdx"})
    print(f"Limpiando {len(files)} archivo(s)...")
    for src in files:
        cleaned, title = clean(src.read_text(encoding="utf-8"))
        out_name = src.stem.replace("_", "-") + ".md"
        (OUT / out_name).write_text(cleaned, encoding="utf-8")
        print(f"  [ok] {out_name}  ({len(cleaned)} chars)"
              + (f'  title="{title}"' if title else ""))


if __name__ == "__main__":
    main()
