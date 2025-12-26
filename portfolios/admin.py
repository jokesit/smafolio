from django.contrib import admin
from .models import Category, PortfolioItem

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)} # พิมพ์ชื่อแล้ว slug จะเด้งขึ้นเองอัตโนมัติ

@admin.register(PortfolioItem)
class PortfolioItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'owner', 'category', 'event_date', 'created_at')
    list_filter = ('category', 'event_date') # ตัวกรองด้านขวา
    search_fields = ('title', 'description', 'owner__email') # ช่องค้นหา