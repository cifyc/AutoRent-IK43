# GitHub — командний процес для ЛР №4

## Що підготовлено

Код: Django / DRF / PostgreSQL, React / TypeScript, автономні Python-тести, README та документація.
Локальний Git уже містить **справжні технічні коміти** (початковий каркас, інструкції та CI), а також **дві гілки із відмінними змінами**:

- `feature/frontend-catalog` — покращення UX каталогу: пошук із затримкою, очищення фільтра, повідомлення про результати.
- `feature/backend-booking` — додаткові тести бізнес-правил: часові пояси, застава, переходи станів.

Історію змін створено під час підготовки лабораторної. **Не можна представляти ці коміти як зроблені особисто Єгором чи Іваном.** Командне рецензування та коміти кожного учасника мають виконуватися ними самостійно.

## Публікація в GitHub

1. На https://github.com/new створити порожній репозиторій `AutoRent-IK43` у власному акаунті **без README, .gitignore і ліцензії**, оскільки файли вже існують.
2. Відкрити PowerShell або інший термінал у розпакованому корені `AutoRent_Lab4_Project` (у папці має бути `.git`).
3. Перевірити налаштування віддаленого репозиторію та відправити гілки:

```bash
git remote -v
git push -u origin main
git push -u origin feature/frontend-catalog
git push -u origin feature/backend-booking
```

Якщо в `.git/config` ще немає `origin`, додати:

```bash
git remote add origin https://github.com/cifyc/AutoRent-IK43.git
```

Якщо GitHub запитує автентифікацію, використати Git Credential Manager / браузер, **ніколи не надсилати паролі або токени в чат**.

## Pull Requests, код-рев'ю та злиття

1. У GitHub відкрити вкладку **Pull requests** → **New pull request**.
2. Обрати `base: main` та `compare: feature/frontend-catalog`, створити PR «Frontend: improve catalog filter UX».
3. Так само створити PR `feature/backend-booking` → `main` («Backend: extend booking domain tests»).
4. Запросити іншого учасника через **Settings → Collaborators**; його GitHub-логін має надати сам учасник.
5. Учасник переглядає код, залишає **Review**, після схвалення можна натиснути **Merge pull request**.
6. На сторінці **Actions** перевірити проходження Python-тестів (4 комбінації ОС та версій Python).
7. Для звіту зробити скриншоти вкладок **Code**, **Commits**, **Branches**, **Pull requests** та **Actions** після реального виконання.

**Не зливайте гілки без фактичного рев'ю лише заради вигляду історії.** Створення гілок і PR засвідчує організацію процесу, але не доводить авторства студентів.

## Посилання

Запланована адреса після створення репозиторію: `https://github.com/cifyc/AutoRent-IK43`.
Адреса не є підтвердженням існування репозиторію, доки сторінку не відкрито й не перевірено.
