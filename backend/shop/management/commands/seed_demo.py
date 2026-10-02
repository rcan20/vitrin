from django.core.management.base import BaseCommand

from shop.models import DiscountCode, Product

DEMO = [
    ("هدفون بی‌سیم", "audio", 2_400_000, 12),
    ("اسپیکر بلوتوثی", "audio", 1_900_000, 8),
    ("ساعت هوشمند", "wearable", 3_800_000, 5),
    ("پاوربانک ۲۰۰۰۰", "accessory", 1_100_000, 20),
    ("کیبورد مکانیکی", "accessory", 2_700_000, 7),
    ("موس بی‌سیم", "accessory", 650_000, 25),
]


class Command(BaseCommand):
    help = "Create demo products and a discount code (idempotent)."

    def handle(self, *args, **opts):
        for name, cat, price, stock in DEMO:
            Product.objects.get_or_create(name=name, defaults={"category": cat, "price": price, "stock": stock})
        DiscountCode.objects.get_or_create(code="OFF10", defaults={"percent": 10})
        self.stdout.write(self.style.SUCCESS("Demo data ready. Discount code: OFF10"))
