# Деплой сайта — 6 шагов (один раз)

## Что нужно
Аккаунт GitHub (создай на github.com, если нет). Username выбирай спокойно — он попадёт в адрес сайта.

## Шаги

1. **Создай репозиторий** на github.com: New repository → имя `finimmunitet` → Public → без README.
   Адрес сайта будет `https://<твой-username>.github.io/finimmunitet/`.
   (Вариант: репо `<username>.github.io` — адрес чище, без /finimmunitet. Не критично.)

2. **Запушь код** (в папке finimmunitet):
   ```bash
   git init
   git add -A
   git commit -m "finimmunitet: первый коммит (каркас + MVP)"
   git branch -M main
   git remote add origin https://github.com/<username>/finimmunitet.git
   git push -u origin main
   ```
   GitHub спросит логин/пароль → пароль = Personal Access Token (Settings → Developer settings → Tokens (classic) → Generate new token, scope `repo`).

3. **Включи Pages:** репозиторий → Settings → Pages → Source: **GitHub Actions** (не «Deploy from branch»).

4. **Проверь деплой:** вкладка Actions — workflow `deploy` должен стать зелёным (~1 мин). Открой адрес сайта.

5. **Проверка из РФ без VPN (с телефона, мобильный интернет):** открывается? Шрифты грузятся? Кнопка «Написать нам» ведёт в VK-сообщество?

6. **Яндекс.Метрика** (после первого деплоя): metrika.yandex.ru → добавить счётчик → скопировать номер → положить в секреты репо как `METRIKA_ID` (Settings → Secrets and variables → Actions → New repository secret) и добавить в `.github/workflows/deploy.yml` строку `env: METRICA_ID: ${{ secrets.METRIKA_ID }}` на шаге `python build.py`. Если метрика не нужна сразу — сайт работает и без неё.

## Ежедневная работа

Новость/разбор = новый `.md` в `content/news/` или `content/cards/` → `git add . && git commit -m "..." && git push`. Сайт обновится сам за минуту.

## Ноябрь (после победы)

Покупаем finimmunitet.ru (строка сметы) → Settings → Pages → Custom domain: `finimmunitet.ru` → у регистратора DNS: A-записи 185.199.108–111.153 + CNAME www → `<username>.github.io`. HTTPS включится сам. `BASE_PATH` обнулится автоматически, если переименовать репо в `<username>.github.io`, либо задать `BASE_PATH=""` в workflow.

## Если GitHub Pages деградирует из РФ (маловероятно)

Зеркало за 10 минут: Cloudflare Pages (pages.dev), подключить тот же репо, Build command: `.venv/bin/python build.py` невозможен в их среде → команда `pip install -r requirements.txt && python build.py`, Output dir: `dist`. Верификация фетчем с машины — как в M1_hosting.md.
