from django import forms
from .models import User, Profile
from allauth.account.forms import SignupForm


class CustomSignupForm(SignupForm):
    """Signup form ที่ตัด password help text ออก"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # ลบ help text ของ password
        if 'password1' in self.fields:
            self.fields['password1'].help_text = None

        if 'password2' in self.fields:
            self.fields['password2'].help_text = None

class UserUpdateForm(forms.ModelForm) :
    """ฟอร์มแก้ไขข้อมูลพื้นฐาน User (ชื่อ, นามสกุล)"""
    class Meta :
        model = User
        fields = ['username', 'first_name', 'last_name']
        # เพิ่มคำอธิบายหน่อย ว่าช่องนี้สำคัญ
        help_texts = {
            'username': 'ใช้สำหรับสร้างลิงก์ Portfolio ของคุณ (ต้องไม่ซ้ำกับคนอื่น)',
        }



class ProfileUpdateForm(forms.ModelForm) :
    """ฟอร์มแก้ไขข้อมูล Profile (รูป, Bio, สถานะ Public)"""
    class Meta :
        model = Profile
        fields = ['avatar', 'bio', 'facebook_link', 'github_link', 'is_public']
        widgets = {
            'bio' : forms.Textarea(attrs={'rows': 3}) # ปรับกล่องข้อความให้สูงขึ้น
        }