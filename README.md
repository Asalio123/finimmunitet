# ФинИммунитет — сайт-навигатор

Статический сайт проекта финансовой безопасности подростков Азнакаевского района и Татарстана.

## Стек

Самописный генератор: **Python + Jinja2 + Markdown** (~200 строк `build.py`), один CSS без фреймворков, чистый JS (~20 строк) для фильтра разборов. Шрифты self-host (Inter + Unbounded, SIL OFL). Деплой: `git push` → GitHub Actions → GitHub Pages.

## Структура

```
content/
  pages/    страницы (index.md, stopdrop.md, razbory.md, about.md, contacts.md)
  news/     лента новостей: ГГГГ-ММ-ДД-слаг.md (date, title, summary)
  cards/    карточки схем: ГГГГ-ММ-ДД-слаг.md (date, tag: звонки|соцсети|подработка|карты)
  uchitelyam/ методички (октябрь)
templates/  base + page/index/cards/card/news_item
static/     css, js, fonts, img
tools/      make_assets.py — генерация favicon/logo/og (PIL)
```

## Локальная сборка

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python build.py
cd dist && python3 -m http.server 8000
```

Переменные: `SITE_URL` (canonical/OG), `BASE_PATH` (подпапка project site), `METRICA_ID` (Яндекс.Метрика). На GitHub Actions `SITE_URL`/`BASE_PATH` выводятся из имени репозитория автоматически.

## Добавить контент

- **Новость:** `content/news/2026-09-05-slug.md` — frontmatter `date`, `title`, `summary`; push = публикация.
- **Разбор схемы:** `content/cards/2026-09-05-slug.md` — frontmatter `date`, `tag`, `summary`; тело: `## Как работает` / `## Красные флаги` / `## Что делать` / `Источник`.
- В поле `title` с двоеточием — брать в кавычки.

## Деплой

См. `DEPLOY.md` (создание репо, включение Pages, домен finimmunitet.ru в ноябре).
