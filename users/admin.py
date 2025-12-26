from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Profile

# สร้าง Inline เพื่อให้แก้ Profile ได้ในหน้าแก้ User เลย (สะดวกมาก)
class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'

# ปรับแต่ง UserAdmin ให้รองรับ Custom User Model ของเรา
class CustomUserAdmin(UserAdmin):
    inlines = (ProfileInline,) # เอา Profile มาแปะไว้ข้างใน
    list_display = ('email', 'username', 'first_name', 'last_name', 'is_staff') # โชว์อีเมลเป็นหลัก
    ordering = ('email',)

# ลงทะเบียน
admin.site.register(User, CustomUserAdmin)
# admin.site.register(Profile) # ไม่ต้องแยกก็ได้ เพราะเราเอาไปใส่ใน UserAdmin แล้ว