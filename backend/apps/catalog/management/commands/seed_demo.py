from decimal import Decimal
from django.core.management.base import BaseCommand
from apps.catalog.models import Car


class Command(BaseCommand):
    help = 'Додати три демонстраційні автомобілі (без дублювання записів).'

    def handle(self, *args, **options):
        samples = [
            ('Toyota', 'Corolla', 'Седан', 'Київ', 5, Decimal('1200.00'), Decimal('6000.00')),
            ('Skoda', 'Octavia', 'Універсал', 'Київ', 5, Decimal('1600.00'), Decimal('8000.00')),
            ('Renault', 'Duster', 'SUV', 'Львів', 5, Decimal('1800.00'), Decimal('9000.00')),
        ]
        for brand, model, category, city, seats, price, deposit in samples:
            car, created = Car.objects.get_or_create(
                brand=brand, model=model, city=city,
                defaults={'category': category, 'seats': seats,
                          'daily_rate_uah': price, 'deposit_uah': deposit,
                          'is_published': True},
            )
            self.stdout.write(('Створено: ' if created else 'Існує: ') + str(car))
