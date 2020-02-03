from django.contrib import admin
from .models import OrderCondition, Order


@admin.register(OrderCondition)
class OrderConditionAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'coin', 'is_active'
    )
    search_fields = ('user__name', 'user__email',)
    raw_id_fields = ('user', 'coin',)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'get_user_name', 'get_coin_name', 'status',
    )
    raw_id_fields = ('condition',)
    search_fields = ('condition__user__name', 'condition__user__email',)

    def get_user_name(self, obj):
        return obj.condition.user.name

    def get_coin_name(self, obj):
        return obj.condition.coin

    get_user_name.short_description = '주문자'
    get_coin_name.short_description = '주문 코인'
