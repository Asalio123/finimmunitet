#!/usr/bin/env python3
"""Сборка статического сайта «ФинИммунитет» (ТЗ: rmg-research-2026/M3_stack.md).

Поток: content/*.md + templates/ + static/ → dist/.
Каждая сущность = папка с index.html (чистые пути без .html).
В markdown-теле доступен контекст шаблонов ({{ site.tg_url }}, {{ base }}, ...):
сначала Jinja-рендер исходника, затем конвертация в HTML.

Запуск: .venv/bin/python build.py
Просмотр: cd dist && python3 -m http.server 8000

Переменные окружения:
  SITE_URL    — абсолютный адрес сайта для canonical/OG (пусто = локальная сборка)
  BASE_PATH   — префикс URL при сборке в подпапку (GitHub Pages project site)
  METRICA_ID  — номер счётчика Яндекс.Метрики (пусто = счётчик не ставится)
  GITHUB_REPOSITORY — задаётся в GitHub Actions: SITE_URL/BASE_PATH выводятся из него
"""
import os
import re
import shutil
from datetime import date, datetime
from pathlib import Path

import frontmatter
import markdown
import yaml
from jinja2 import Environment, FileSystemLoader, select_autoescape

ROOT = Path(__file__).parent
CONTENT = ROOT / "content"
STATIC = ROOT / "static"
DIST = ROOT / "dist"

TAGS = ["звонки", "соцсети", "подработка", "карты"]

MD = markdown.Markdown(extensions=["tables", "fenced_code", "sane_lists"])


def md_to_html(text: str) -> str:
    MD.reset()
    return MD.convert(text)


def load_site_config() -> dict:
    """content/site.yml — плоский YAML, парсим стандартно (>- и кавычки работают)."""
    return yaml.safe_load((CONTENT / "site.yml").read_text(encoding="utf-8"))


def entity_slug(filename: str) -> str:
    """2026-09-01-prodazha-karty.md → prodazha-karty (дата отрезается); страницы — как есть."""
    return re.sub(r"^\d{4}-\d{2}-\d{2}-", "", Path(filename).stem)


def normalize_date(meta: dict) -> None:
    d = meta.get("date")
    if isinstance(d, str) and d:
        try:
            meta["date"] = datetime.strptime(d, "%Y-%m-%d").date()
        except ValueError:
            meta["date"] = None
    meta["date_str"] = meta["date"].strftime("%d.%m.%Y") if meta.get("date") else ""


def collect(dirpath: Path, env: Environment, ctx: dict) -> list:
    """news/ и cards/: сортировка по дате DESC, html = jinja(md) с контекстом."""
    items = []
    if not dirpath.exists():
        return items
    for f in sorted(dirpath.glob("*.md")):
        post = frontmatter.load(f)
        post.metadata["slug"] = entity_slug(f.name)
        normalize_date(post.metadata)
        post.metadata["html"] = md_to_html(env.from_string(post.content).render(**ctx))
        items.append(post)
    return sorted(items, key=lambda p: p.metadata.get("date") or date.min, reverse=True)


def build():
    cfg = load_site_config()
    # dist/ пересобирается с нуля: иначе в нём вечно живут страницы от старых версий
    shutil.rmtree(DIST, ignore_errors=True)
    DIST.mkdir(exist_ok=True)
    build_date = datetime.now().strftime("%d.%m.%Y")

    base = os.environ.get("BASE_PATH", "").rstrip("/")
    site_url = os.environ.get("SITE_URL", "").rstrip("/")
    gh_repo = os.environ.get("GITHUB_REPOSITORY", "")
    if gh_repo and not site_url:
        owner, name = gh_repo.split("/", 1)
        site_url = f"https://{owner.lower()}.github.io"
        if name.lower() != f"{owner.lower()}.github.io":
            site_url += f"/{name}"
            base = os.environ.get("BASE_PATH", f"/{name}").rstrip("/")

    env = Environment(
        loader=FileSystemLoader(ROOT / "templates"),
        autoescape=select_autoescape(["html"]),
    )
    ctx = {
        "site": cfg,
        "build_date": build_date,
        "site_url": site_url,
        "base": base,
        "metrika_id": os.environ.get("METRICA_ID", ""),
        "tags": TAGS,
        "schemes_count": 0,
    }

    cards = collect(CONTENT / "cards", env, ctx)
    news = collect(CONTENT / "news", env, ctx)
    ctx["schemes_count"] = len(cards)

    # 1. статика → dist/
    for name in ["css", "js", "fonts", "img", "files"]:
        src = STATIC / name
        if src.exists():
            shutil.copytree(src, DIST / name, dirs_exist_ok=True)

    # 2. страницы (pages/index.md → dist/index.html, остальные → <slug>/index.html)
    for f in sorted((CONTENT / "pages").glob("*.md")):
        page = frontmatter.load(f)
        slug = Path(f).stem
        page.metadata["slug"] = slug
        normalize_date(page.metadata)
        page_html = md_to_html(env.from_string(page.content).render(**ctx))
        page.metadata["html"] = page_html
        tpl = page.metadata.get("template", "page")
        data = {}
        if tpl == "index":
            data["latest_news"] = news[:5]
        elif tpl == "cards":
            data["cards"] = cards
        html = env.get_template(f"{tpl}.html").render(
            page=page.metadata, content=page_html, **ctx, **data
        )
        out = DIST / "index.html" if slug == "index" else DIST / slug / "index.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(html, encoding="utf-8")

    # 3. страница каждой карточки и каждой новости
    card_slugs = {c.metadata["slug"] for c in cards}
    for item in cards + news:
        tpl = "card.html" if item.metadata["slug"] in card_slugs else "news_item.html"
        html = env.get_template(tpl).render(
            page=item.metadata, content=item.metadata["html"], **ctx
        )
        out = DIST / item.metadata["slug"] / "index.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(html, encoding="utf-8")

    # 4. sitemap + robots (только когда известен абсолютный адрес)
    if site_url:
        paths = ["/"] + [f"/{p.stem}/" for p in (CONTENT / "pages").glob("*.md") if p.stem != "index"]
        paths += [f"/{c.metadata['slug']}/" for c in cards] + [f"/{n.metadata['slug']}/" for n in news]
        entries = "".join(f"  <url><loc>{site_url}{p}</loc></url>\n" for p in dict.fromkeys(paths))
        (DIST / "sitemap.xml").write_text(
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            f"{entries}</urlset>", encoding="utf-8")
        (DIST / "robots.txt").write_text(
            f"User-agent: *\nAllow: /\nSitemap: {site_url}/sitemap.xml\n", encoding="utf-8")

    print(f"OK → dist/ | SITE_URL={site_url or 'локально'} BASE={base or '/'} | "
          f"карточек {len(cards)}, новостей {len(news)} | обновлено {build_date}")


if __name__ == "__main__":
    build()
