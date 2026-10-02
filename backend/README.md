# Vitrin Backend (Django)

بک‌اند فروشگاه نمایشی «ویترین»: API محصولات، اعتبارسنجی کد تخفیف و ثبت سفارش.
قیمت‌ها و تخفیف همیشه روی سرور از دیتابیس محاسبه می‌شوند، نه از مقدارِ ارسال‌شده توسط مرورگر.

## اجرا

```bash
python -m venv venv
source venv/bin/activate        # ویندوز: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo      # محصولات نمونه + کد تخفیف OFF10
python manage.py createsuperuser
python manage.py runserver
```

پنل مدیریت: http://127.0.0.1:8000/admin/

## API

| متد | آدرس | توضیح |
|---|---|---|
| GET | `/api/products/?q=&category=&sort=price_asc\|price_desc` | فهرست محصولات |
| GET | `/api/discount/<code>/` | بررسی کد تخفیف |
| POST | `/api/orders/` | ثبت سفارش |

نمونه بدنه ثبت سفارش:

```json
{"full_name": "علی رضایی", "phone": "09123456789", "address": "تهران، خیابان آزادی، پلاک ۱",
 "code": "OFF10", "items": [{"id": 1, "quantity": 2}]}
```

## اتصال فرانت‌اند

```js
const API = "http://127.0.0.1:8000/api";
const { products } = await (await fetch(`${API}/products/`)).json();
```

آدرس سایت فرانت‌اند را در `CORS_ALLOWED_ORIGINS` (متغیر محیطی یا settings) بگذارید.
قوانین ارسال (`FREE_SHIPPING_THRESHOLD`, `SHIPPING_COST`) در `config/settings.py` است و باید با فرانت‌اند یکی باشد.

## تست

```bash
python manage.py test
```
