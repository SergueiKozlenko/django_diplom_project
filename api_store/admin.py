from django.contrib import admin
from api_store.models import Product, ProductReview, ProductCollection, Position, Order


class PositionInline(admin.TabularInline):
    model = Position


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    inlines = [PositionInline]


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = [PositionInline]
    readonly_fields = ['total_amount']

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        self.saved_obj = obj

    def _changeform_view(self, request, object_id, form_url, extra_context):
        ret = super()._changeform_view(request, object_id, form_url, extra_context)
        if hasattr(self, 'saved_obj'):
            self.saved_obj.total_amount = sum(
                p.product.price * p.quantity
                for p in self.saved_obj.positions.all()
            )
            self.saved_obj.save()
        return ret


@admin.register(ProductReview)
class ProductAdmin(admin.ModelAdmin):
    pass


@admin.register(ProductCollection)
class ProductAdmin(admin.ModelAdmin):
    pass
