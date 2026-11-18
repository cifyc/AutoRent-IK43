# AutoRent — базова структура коду (ЛР №4)

Навчальний вебсервіс оренди автомобілів. Студенти: **Смакота Іван, Перець Єгор (ІК-43)**. На основі лабораторних №1–3. Версія каркаса: `0.1.0`.

## 1. Що є в репозиторії

```text
AutoRent_Lab4_Project/
├── backend/                    Python, Django REST Framework
│   ├── manage.py
│   ├── config/                 налаштування, маршрути
│   ├── apps/catalog/           Car, MaintenanceBlock, каталог
│   ├── apps/bookings/          Booking, BookingService, API
│   └── autorent_core/          незалежні від Django бізнес-правила
├── frontend/                   React + TypeScript + Vite
│   └── src/                    каталог, API-клієнт, стилі
├── tests/                      unit-тести без зовнішніх пакетів
├── docs/                       архітектура, відповідність вимогам, Git-інструкція
├── docker-compose.yml          PostgreSQL + Django + Vite для локальної демонстрації
├── .env.example
└── .gitignore
```

## 2. Автономні тести (Windows, Linux, macOS)

Для Python 3.11+ у корені проєкту. На Windows бібліотеці `zoneinfo` потрібна база часових поясів `tzdata` (без неї тест `Europe/Kyiv` помилково завершується з `ZoneInfoNotFoundError`):

```bash
python -m pip install -r requirements-test.txt
python -m unittest discover -s tests -v
```

Якщо Python 3.14 встановлено в `C:\Python314`, у PowerShell можна виконати:

```powershell
& C:\Python314\python.exe -m pip install -r requirements-test.txt
& C:\Python314\python.exe -m unittest discover -s tests -v
```

Після публікації GitHub Actions запускає ці автономні тести на Windows та Ubuntu для Python 3.12 і 3.14. Поки онлайн-репозиторію немає, статус Actions не підтверджено.

Перевіряються: ціна (49 год = 3 доби), сусідні інтервали, коректність часу, 24-годинне скасування, правила переходів, часовий пояс. Ці тести не замінюють інтеграційного чи конкурентного тестування Django/PostgreSQL.

## 3. Запуск із Docker Compose (рекомендовано)

Потрібні Docker Engine та Compose, доступ до інтернету для завантаження образів і залежностей.

```bash
docker compose up --build -d
docker compose exec backend python manage.py makemigrations catalog bookings
docker compose exec backend python manage.py migrate
docker compose exec backend python manage.py createsuperuser
docker compose exec backend python manage.py seed_demo
```

**Важливо:** міграції створюються після першого `up`; доки вони не застосовані, API звернення до таблиць можуть відповідати помилкою. Відкрийте http://localhost:8000/admin/ та додайте опублікований Car. Каталог: http://localhost:5173/; API: http://localhost:8000/api/cars/.

Для повторного запуску після першого `makemigrations` достатньо `docker compose up -d`. У команді `docker compose down -v` обсяг бази буде видалено — не використовуйте її для збережених даних.

### Локальний запуск без Docker

Backend, Python 3.11+:

```bash
cd backend
python -m venv .venv
# macOS/Linux: source .venv/bin/activate
# Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
python manage.py makemigrations catalog bookings
python manage.py migrate
python manage.py createsuperuser
python manage.py seed_demo
python manage.py runserver
```

SQLite вмикається автоматично, якщо немає змінної `DB_HOST`; це **тільки для навчальної локальної роботи**. Для продемонстрованої блокувальної конкурентної логіки потрібна PostgreSQL.

Frontend, Node.js 20+:

```bash
cd frontend
npm install
npm run dev
```

## 4. Основні API-маршрути

| Метод | URL | Призначення |
|---|---|---|
| GET | `/api/cars/` | Опубліковані авто, фільтр `?city=Київ` |
| POST | `/api/bookings/` | Створити бронювання (сесія клієнта, прийняті умови) |
| GET | `/api/bookings/my/` | Власні бронювання |
| POST | `/api/bookings/{id}/cancel/` | Самостійне скасування ≥24 год |
| POST | `/api/bookings/{id}/activate/` | Видача (staff) |
| POST | `/api/bookings/{id}/complete/` | Повернення (staff) |
| POST | `/api/bookings/{id}/manager-cancel/` | Скасування менеджером із `reason` (staff) |

Формат POST `/api/bookings/`:

```json
{"car_id":1,"starts_at":"2027-01-10T12:00:00+02:00","ends_at":"2027-01-12T13:00:00+02:00","terms_accepted":true}
```

Для захищених запитів використовується session authentication Django. Вебсторінка каталогу в цьому каркасі ще не містить форми входу/бронювання; API можна перевірити через DRF browsable API після входу в адмінпанель/сесії. Виробничий захист і профілі користувачів не завершені.

## 5. Ролі учасників

- **Смакота Іван:** вимоги та UX, фронтенд React/TS, каталог, картки авто, клієнтські сценарії.
- **Перець Єгор:** Django/DRF, PostgreSQL, моделі Booking/Car, транзакції та тести.
- **Обидва:** уточнення вимог, код-рев’ю, інтеграція й документація.

У папці `docs/GIT_WORKFLOW.md` описано, як створити спільний GitHub-репозиторій, окремі гілки та Pull Requests. У підготовленій історії є технічні коміти та окремі зміни для фронтенду й серверних тестів. **Ці коміти зроблені під час підготовки проєкту, а не від імені другого студента.** Реальне рев'ю має зробити учасник команди зі свого облікового запису.

## 6. Межі та безпека

Це лабораторний каркас, не готовий сайт. На публічному хостингу не можна використовувати `DJANGO_DEBUG=1`, тестові паролі з Compose або запускати `runserver` як production-сервер. Не реалізовано: платіжні операції, справжню поштову чергу, 90-денний аудит, блокування входу після 5 невдалих спроб, перевірку 20 паралельних запитів і автоматизований деплой. Блокування `select_for_update()` гарантує серіалізацію тільки на PostgreSQL і тільки коли всі конкурентні записи виконуються через той самий сервіс, а не напряму в Django admin.
