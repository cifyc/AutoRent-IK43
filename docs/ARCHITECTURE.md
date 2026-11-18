# Архітектура AutoRent — лабораторна №4

**Підхід:** модульний моноліт (лабораторна №2).

```text
Браузер (React/TS/Vite)
    | HTTP /api (у dev через Vite proxy)
    v
Django REST Framework
    |--> catalog: Car, MaintenanceBlock, CarViewSet
    |--> bookings: Booking, BookingViewSet, BookingService
    |       \--> autorent_core: Period, PricingPolicy, правила станів
    v
PostgreSQL (Docker Compose) або SQLite (лише для локального ознайомлення)
```

Точка синхронізації при створенні бронювання: `BookingService.create()` виконує `transaction.atomic()`, отримує `Car` через `select_for_update()`, перевіряє перетини бронювань і ТО, записує бронювання з ціною. Правильна конкурентна поведінка потребує PostgreSQL; SQLite не є середовищем для перевірки NFR-03.

Інтервали трактуються як `[start, end)`. Ставка, застава, кількість діб і підсумок зберігаються в бронюванні як знімок. Оплату онлайн не реалізовано.

## Межі каркаса

Працює на рівні коду: правила ціни, перетинів, допустимих станів; Django ORM моделі, API-каталог і базові захищені маршрути бронювання. Не готові: повний UX реєстрації й бронювання, розширена рольова модель, SMTP/outbox, аудит, rate limiting, резервне копіювання, production TLS, перевірки конкурентності 20 паралельними запитами, реальний деплой.

**ВАЖЛИВО:** пряме редагування `MaintenanceBlock` через Django admin не застосовує перевірку `BookingService.create_maintenance()`. Це треба доопрацювати перед використанням у реальному проєкті.
