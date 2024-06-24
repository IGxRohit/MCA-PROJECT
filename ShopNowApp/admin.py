# admin.py
from django.contrib import admin
from ShopNowApp.models import Product,Order,OrderItem,Cart

admin.site.register(Product)
admin.site.register(Cart)
admin.site.register(Order)
admin.site.register(OrderItem)

