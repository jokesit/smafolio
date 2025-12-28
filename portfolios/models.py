import sys
from io import BytesIO
from PIL import Image
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db import models
from django.conf import settings 
from urllib.parse import urlparse, parse_qs

# ==========================================
# 1. ฟังก์ชันช่วยบีบอัดรูปภาพ (Utility Function)
# ==========================================
def compress_image(uploaded_image, max_size=(1200, 1200)):
    """
    ฟังก์ชันสำหรับบีบอัดและย่อขนาดรูปภาพ
    - uploaded_image: ไฟล์รูปภาพต้นฉบับ
    - max_size: ขนาดสูงสุด (กว้าง, สูง) ที่ต้องการ (Default 1200px)
    """
    # ถ้าไม่มีรูปส่งมา ให้ข้ามไป
    if not uploaded_image:
        return None

    # เปิดรูปภาพด้วย Pillow
    img = Image.open(uploaded_image)
    
    # แปลงโหมดสีเป็น RGB (เผื่อไฟล์เดิมเป็น PNG ที่มีพื้นหลังโปร่งใส จะได้ Save เป็น JPEG ได้)
    if img.mode != 'RGB':
        img = img.convert('RGB')

    # ย่อรูปภาพ (Thumbnail จะรักษาสัดส่วนภาพเดิม ไม่ให้เพี้ยน)
    # ถ้าภาพเดิมเล็กกว่า 1200px อยู่แล้ว มันจะไม่ขยาย (ภาพไม่แตก)
    img.thumbnail(max_size, Image.LANCZOS)

    # เตรียม Buffer สำหรับเขียนไฟล์ใหม่
    output_io = BytesIO()
    
    # บันทึกภาพลง Buffer (Format JPEG, Quality 85%)
    img.save(output_io, format='JPEG', quality=85, optimize=True)
    output_io.seek(0)

    # สร้าง InMemoryUploadedFile ใหม่เพื่อส่งกลับไปบันทึก
    new_image = InMemoryUploadedFile(
        output_io,
        'ImageField',
        f"{uploaded_image.name.split('.')[0]}.jpg", # เปลี่ยนนามสกุลเป็น .jpg
        'image/jpeg',
        sys.getsizeof(output_io),
        None
    )
    
    return new_image

# ==========================================
# 2. Models
# ==========================================

class Category(models.Model):
    """หมวดหมู่ผลงาน เช่น กิจกรรม, วิชาการ, จิตอาสา"""
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

class PortfolioItem(models.Model):
    """ชิ้นงานแต่ละชิ้น"""
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='portfolio_items')
    title = models.CharField(max_length=200)
    description = models.TextField(help_text="รายละเอียดของผลงาน")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    
    # รูปภาพปก
    cover_image = models.ImageField(upload_to='portfolio_covers/')
    
    # เพิ่ม Field สำหรับเก็บลิงก์วิดีโอ
    video_link = models.URLField(blank=True, null=True, help_text="รองรับลิงก์จาก YouTube")


    # วันที่
    event_date = models.DateField(null=True, blank=True, help_text="วันที่ทำกิจกรรม/ผลงาน")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['-event_date', '-created_at'] # เรียงจากใหม่ไปเก่า

    def save(self, *args, **kwargs):
        # ตรวจสอบว่ามีรูปภาพหรือไม่
        if self.cover_image:
            # กรณีเป็นการแก้ไข (มี pk แล้ว)
            if self.pk:
                try:
                    old_instance = PortfolioItem.objects.get(pk=self.pk)
                    # ถ้ารูปใหม่ ไม่ตรงกับรูปเก่า แสดงว่ามีการอัปโหลดใหม่ -> ให้บีบอัด
                    if old_instance.cover_image != self.cover_image:
                        self.cover_image = compress_image(self.cover_image)
                except PortfolioItem.DoesNotExist:
                    pass # กรณีหาไม่เจอ (เผื่อไว้)
            
            # กรณีสร้างใหม่ (ยังไม่มี pk) -> บีบอัดเลย
            else:
                self.cover_image = compress_image(self.cover_image)

        super().save(*args, **kwargs)

    #  เพิ่มฟังก์ชันแปลงลิงก์ YouTube ให้เป็น Embed URL
    def get_embed_url(self):
        if not self.video_link:
            return None

        try:
            url_data = urlparse(self.video_link)
            video_id = None

            if url_data.hostname == 'youtu.be':
                video_id = url_data.path.lstrip('/')
            elif url_data.hostname in ['www.youtube.com', 'youtube.com']:
                if url_data.path == '/watch':
                    video_id = parse_qs(url_data.query).get('v', [None])[0]
                elif url_data.path.startswith('/embed/'):
                    video_id = url_data.path.split('/')[2]
                elif url_data.path.startswith('/shorts/'):
                    video_id = url_data.path.split('/')[2]

            if video_id:
                # ใช้ youtube-nocookie + เพิ่ม params ป้องกัน error
                return (
                    f"https://www.youtube-nocookie.com/embed/{video_id}"
                    "?rel=0&modestbranding=1"
                )

        except Exception as e:
            print(f"YouTube URL error: {e}")

        return None


# for upload many image
class PortfolioImage(models.Model):
    """รูปภาพเพิ่มเติมสำหรับผลงาน (Gallery)"""
    portfolio_item = models.ForeignKey(PortfolioItem, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='portfolio_gallery/')
    
    def __str__(self):
        return f"Image for {self.portfolio_item.title}"

    def save(self, *args, **kwargs):
        # ใช้ Logic เดียวกันกับ PortfolioItem
        if self.image:
            if self.pk:
                try:
                    old_instance = PortfolioImage.objects.get(pk=self.pk)
                    if old_instance.image != self.image:
                        self.image = compress_image(self.image)
                except PortfolioImage.DoesNotExist:
                    pass
            else:
                self.image = compress_image(self.image)

        super().save(*args, **kwargs)