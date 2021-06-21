from django.contrib import admin
from api_store.models import Product, ProductReview, ProductCollection, Position, Order


# class ProductOrderPositionInlineFormset(BaseInlineFormSet):
#     def clean(self):
#         products = []
#         for form in self.forms:
#             product = form.cleaned_data.get("product")
#             if product in products:
#                 raise ValidationError('Товар не может повторяться в заказе')
#             products.append(form.cleaned_data.get("product"))
#
#         return super().clean()


class PositionInline(admin.TabularInline):
    model = Position


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    inlines = [PositionInline]


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = [PositionInline]


@admin.register(ProductReview)
class ProductAdmin(admin.ModelAdmin):
    pass


@admin.register(ProductCollection)
class ProductAdmin(admin.ModelAdmin):
    pass
