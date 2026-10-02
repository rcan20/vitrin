from django.urls import path

from . import views

urlpatterns = [
    path("products/", views.product_list),
    path("discount/<str:code>/", views.discount_check),
    path("orders/", views.order_create),
]
