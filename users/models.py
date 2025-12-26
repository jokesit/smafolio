from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """
    Custom User Model: ใช้อีเมลในการ Login แทน Username
    """
    email = models.EmailField(_('email address'), unique=True)

    # บังคับให้ใช้ email เป็นตัวยืนยันตัวตนหลัก
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username'] # username ยังต้องมีอยู่ (ไว้ทำ URL) แต่ไม่ต้องใช้ login

    def __str__(self):
        return self.email
    


class Profile(models.Model):
    """
    เก็บข้อมูลเพิ่มเติมของ User เช่น รูปภาพ, Bio, และการตั้งค่า
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(upload_to='avatars/', default='avatars/default.png', blank=True)
    bio = models.TextField(max_length=500, blank=True, help_text="เขียนแนะนำตัวสั้นๆ")
    
    # Settings
    is_public = models.BooleanField(default=True, help_text="เปิดให้คนอื่นเห็น Portfolio นี้หรือไม่")
    
    # Social Links (เผื่อไว้)
    facebook_link = models.URLField(blank=True)
    github_link = models.URLField(blank=True)

    def __str__(self):
        return f'{self.user.username} Profile'
    




# Signal: สร้าง Profile อัตโนมัติเมื่อมีการสร้าง User ใหม่
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()