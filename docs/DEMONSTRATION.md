# Демонстрація на захисті (3–5 хвилин)

1. Відкрити README.md і показати `backend`, `frontend`, `tests`, `docs`.
2. Пояснити, що це модульний моноліт: React звертається до Django REST API, Django працює з PostgreSQL.
3. Відкрити `backend/apps/catalog/models.py`: Car і MaintenanceBlock; `backend/apps/bookings/models.py`: Booking зі станами, ціною та датами.
4. Відкрити `backend/autorent_core/rules.py`: `PricingPolicy.quote`, `Period.overlaps`, правила переходів. Навести приклад: 49 год / 24 год = 2,0417; округлення вгору до 3 діб; 3 × 1200 грн = 3600 грн. Застава окрема.
5. Відкрити `backend/apps/bookings/services.py`: транзакція, блокування автомобіля, запит на перетини, запис бронювання. Уточнити, що гарантія конкурентності стосується PostgreSQL, тест 20 паралельних запитів ще не проведений.
6. Запустити `python -m unittest discover -s tests -v` та показати результати.
7. За наявності Docker запустити PostgreSQL+Django+React; показати каталог і Django admin.
8. Показати `docs/GIT_WORKFLOW.md` та реальні GitHub PR після того, як ви з напарником їх створите.

Не називати лабораторний каркас повністю готовим продуктом.
