from django.test import TestCase

from .models import DiscountCode, Product


class OrderApiTests(TestCase):
    def setUp(self):
        self.p = Product.objects.create(name="هدفون", category="audio", price=2_000_000, stock=5)
        DiscountCode.objects.create(code="OFF10", percent=10)

    def post(self, qty=2, **over):
        body = {"full_name": "علی رضایی", "phone": "۰۹۱۲۳۴۵۶۷۸۹", "address": "تهران، خیابان آزادی، پلاک ۱",
                "items": [{"id": self.p.id, "quantity": qty}]}
        body.update(over)
        return self.client.post("/api/orders/", body, content_type="application/json")

    def test_discount_and_shipping(self):
        r = self.post(code="off10")
        self.assertEqual(r.status_code, 201)
        d = r.json()
        self.assertEqual((d["subtotal"], d["discount"], d["shipping"], d["total"]),
                         (4_000_000, 400_000, 150_000, 3_750_000))
        self.p.refresh_from_db()
        self.assertEqual(self.p.stock, 3)

    def test_free_shipping_above_threshold(self):
        d = self.post(qty=3).json()
        self.assertEqual((d["shipping"], d["total"]), (0, 6_000_000))

    def test_invalid_phone(self):
        r = self.post(phone="123")
        self.assertEqual(r.status_code, 400)
        self.assertIn("phone", r.json()["errors"])

    def test_insufficient_stock(self):
        self.assertEqual(self.post(qty=6).status_code, 409)
        self.p.refresh_from_db()
        self.assertEqual(self.p.stock, 5)

    def test_unknown_code(self):
        self.assertIn("code", self.post(code="NOPE").json()["errors"])

    def test_product_list_and_discount_endpoint(self):
        self.assertEqual(len(self.client.get("/api/products/?q=هدفون").json()["products"]), 1)
        self.assertTrue(self.client.get("/api/discount/off10/").json()["valid"])
        self.assertEqual(self.client.get("/api/discount/x/").status_code, 404)
