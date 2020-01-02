from django.contrib import admin
from .models import Coin


@admin.register(Coin)
class CoinAdmin(admin.ModelAdmin):
    list_display = ('code', 'name_ko', 'name_en', 'is_active')
    search_fields = ('code', 'name_ko',)
