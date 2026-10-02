import json
import re

from django.db import transaction
from django.db.models import F, Q
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from .models import DiscountCode, Order, OrderItem, Product
from .pricing import calculate_totals

DIGITS = str.maketrans("۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩", "01234567890123456789")
PHONE_RE = re.compile(r"^09\d{9}$")


def product_json(p):
    return {"id": p.id, "name": p.name, "category": p.category, "price": p.price,
            "image_url": p.image_url, "stock": p.stock}


@require_GET
def product_list(request):
    qs = Product.objects.filter(is_active=True)
    if request.GET.get("category"):
        qs = qs.filter(category=request.GET["category"])
    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(Q(name__icontains=q) | Q(category__icontains=q))
    order = {"price_asc": "price", "price_desc": "-price"}.get(request.GET.get("sort"), "id")
    return JsonResponse({"products": [product_json(p) for p in qs.order_by(order)]})


@require_GET
def discount_check(request, code):
    d = DiscountCode.objects.filter(code__iexact=code.strip(), is_active=True).first()
    if not d:
        return JsonResponse({"valid": False}, status=404)
    return JsonResponse({"valid": True, "code": d.code, "percent": d.percent})


def _fail(errors, status=400):
    return JsonResponse({"ok": False, "errors": errors}, status=status)


@csrf_exempt  # public, anonymous endpoint called from another origin; no cookies/session used
@require_POST
def order_create(request):
    try:
        data = json.loads(request.body)
        if not isinstance(data, dict):
            raise ValueError
    except (ValueError, UnicodeDecodeError):
        return _fail({"body": "درخواست باید JSON معتبر باشد."})

    errors = {}
    name = str(data.get("full_name", "")).strip()
    phone = str(data.get("phone", "")).translate(DIGITS).strip()
    address = str(data.get("address", "")).strip()
    if len(name) < 3:
        errors["full_name"] = "نام و نام خانوادگی را کامل وارد کنید."
    if not PHONE_RE.match(phone):
        errors["phone"] = "شماره موبایل معتبر نیست."
    if len(address) < 10:
        errors["address"] = "آدرس را کامل وارد کنید."

    wanted = {}
    for item in data.get("items") or []:
        try:
            pid, qty = int(item["id"]), int(item["quantity"])
        except (KeyError, TypeError, ValueError):
            errors["items"] = "فهرست اقلام نامعتبر است."
            break
        if not 1 <= qty <= 99:
            errors["items"] = "تعداد هر کالا باید بین ۱ تا ۹۹ باشد."
            break
        wanted[pid] = wanted.get(pid, 0) + qty
    if not wanted and "items" not in errors:
        errors["items"] = "سبد خرید خالی است."

    discount = None
    code = str(data.get("code") or "").strip()
    if code:
        discount = DiscountCode.objects.filter(code__iexact=code, is_active=True).first()
        if not discount:
            errors["code"] = "کد تخفیف معتبر نیست."
    if errors:
        return _fail(errors)

    with transaction.atomic():
        products = {p.id: p for p in Product.objects.select_for_update()
                    .filter(id__in=wanted, is_active=True)}
        lines = []
        for pid, qty in wanted.items():
            p = products.get(pid)
            if not p:
                return _fail({"items": f"کالای {pid} موجود نیست."})
            if p.stock < qty:
                return _fail({"items": f"موجودی «{p.name}» کافی نیست."}, status=409)
            lines.append((p, qty))

        totals = calculate_totals(lines, discount)
        order = Order.objects.create(full_name=name, phone=phone, address=address,
                                     discount_code=discount, **totals)
        OrderItem.objects.bulk_create(
            OrderItem(order=order, product=p, quantity=q, unit_price=p.price) for p, q in lines)
        for p, q in lines:
            Product.objects.filter(pk=p.pk).update(stock=F("stock") - q)

    return JsonResponse({"ok": True, "order_id": order.id, **totals}, status=201)
