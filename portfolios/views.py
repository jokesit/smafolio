import base64 # ✅ เพิ่ม
import qrcode # ✅ เพิ่ม
from django.urls import reverse # ✅ เพิ่ม
from io import BytesIO
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.contrib import messages
from .models import PortfolioItem, PortfolioImage
from .forms import PortfolioItemForm
# Import Form จาก users app
from users.forms import UserUpdateForm, ProfileUpdateForm
from django.forms import inlineformset_factory
from weasyprint import HTML
from django.http import HttpResponse
from django.template.loader import render_to_string



User = get_user_model()

def home(request):
    return render(request, 'home.html')

@login_required # บังคับว่าต้องล็อกอินก่อนถึงจะเข้าหน้านี้ได้
def dashboard(request):
    """หน้าจัดการข้อมูลส่วนตัวและผลงาน"""
    
    # ดึงผลงานทั้งหมดของ user คนนี้มาแสดง
    my_portfolios = PortfolioItem.objects.filter(owner=request.user)

    return render(request, 'portfolios/dashboard.html', {
        'portfolios': my_portfolios
    })

@login_required
def edit_profile(request):
    """หน้าแยกสำหรับแก้ไข Profile โดยเฉพาะ"""
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, 'อัปเดตข้อมูลสำเร็จ!')
            return redirect('dashboard')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    return render(request, 'users/edit_profile.html', {
        'u_form': u_form,
        'p_form': p_form
    })


@login_required
def create_portfolio(request):
    # สร้าง Formset: บอกว่าให้มีรูปเพิ่มได้สูงสุด 4 รูป (extra=4 คือโชว์ช่องว่าง 4 ช่องเลย)
    ImageFormSet = inlineformset_factory(
        PortfolioItem, PortfolioImage, 
        fields=('image',), 
        extra=4, max_num=4, can_delete=False
    )

    if request.method == 'POST':
        form = PortfolioItemForm(request.POST, request.FILES)
        # รับข้อมูลรูปภาพเพิ่มเติม
        formset = ImageFormSet(request.POST, request.FILES)
        
        if form.is_valid() and formset.is_valid():
            portfolio_item = form.save(commit=False)
            portfolio_item.owner = request.user
            portfolio_item.save()
            
            # ผูกรูปภาพเข้ากับผลงานชิ้นนี้
            formset.instance = portfolio_item
            formset.save()
            
            messages.success(request, 'เพิ่มผลงานและรูปภาพเรียบร้อยแล้ว!')
            return redirect('dashboard')
    else:
        form = PortfolioItemForm()
        formset = ImageFormSet() # สร้างฟอร์มเปล่าๆ

    return render(request, 'portfolios/create_portfolio.html', {
        'form': form,
        'formset': formset # ส่ง formset ไปที่ template ด้วย
    })


def portfolio_view(request, username):
    """หน้าแสดง Portfolio สาธารณะของ user นั้นๆ"""
    
    # 1. ค้นหา User จาก username (ถ้าไม่เจอให้เด้ง 404)
    portfolio_owner = get_object_or_404(User, username=username)
    
    # 2. ตรวจสอบสิทธิ์การเข้าชม (Privacy Check)
    # ถ้าเจ้าของปิด Public (is_public=False) และคนดูไม่ใช่เจ้าของเอง -> ห้ามดู
    if not portfolio_owner.profile.is_public:
        if request.user != portfolio_owner:
            return render(request, '404_private.html', status=404) # สร้างหน้าแจ้งเตือนว่าส่วนตัว (เดี๋ยวทำเพิ่ม)
            # หรือจะใช้บรรทัดล่างนี้เพื่อเด้งไปหน้าแรกเลยก็ได้
            # return redirect('home')

    # 3. ดึงผลงานทั้งหมดของคนนี้
    # แก้ไขตรงนี้: เรียงตาม 'หมวดหมู่' ก่อน แล้วค่อยเรียงตาม 'วันที่'
    # เพื่อให้ template ใช้คำสั่ง regroup ได้ถูกต้อง
    items = portfolio_owner.portfolio_items.all().order_by('category__name', '-event_date')

    context = {
        'owner': portfolio_owner,
        'items': items,
    }
    
    # สังเกตว่าเราจะเก็บไฟล์ไว้ในโฟลเดอร์ย่อย portfolios/
    return render(request, 'portfolios/public_portfolio.html', context)


@login_required
def edit_portfolio(request, pk):
    portfolio_item = get_object_or_404(PortfolioItem, pk=pk)
    if portfolio_item.owner != request.user:
        return HttpResponseForbidden("คุณไม่มีสิทธิ์แก้ไขผลงานนี้")

    # สำหรับหน้า Edit: extra=0 คือไม่ต้องเพิ่มช่องว่างถ้ารูปเต็มแล้ว, can_delete=True คือให้ลบรูปเก่าได้
    ImageFormSet = inlineformset_factory(
        PortfolioItem, PortfolioImage, 
        fields=('image',), 
        extra=1, max_num=4, can_delete=True
    )

    if request.method == 'POST':
        form = PortfolioItemForm(request.POST, request.FILES, instance=portfolio_item)
        formset = ImageFormSet(request.POST, request.FILES, instance=portfolio_item)
        
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            messages.success(request, 'แก้ไขผลงานเรียบร้อยแล้ว!')
            return redirect('dashboard')
    else:
        form = PortfolioItemForm(instance=portfolio_item)
        formset = ImageFormSet(instance=portfolio_item)

    return render(request, 'portfolios/edit_portfolio.html', {
        'form': form, 
        'item': portfolio_item,
        'formset': formset # ส่ง formset ไปด้วย
    })



@login_required
def delete_portfolio(request, pk):
    """ลบผลงาน"""
    portfolio_item = get_object_or_404(PortfolioItem, pk=pk)

    # Security Check
    if portfolio_item.owner != request.user:
        return HttpResponseForbidden("คุณไม่มีสิทธิ์ลบผลงานนี้")

    if request.method == 'POST':
        # ยืนยันการลบ
        portfolio_item.delete()
        messages.success(request, 'ลบผลงานเรียบร้อยแล้ว')
        return redirect('dashboard')
    
    # ถ้าเป็น GET ให้พาไปหน้ายืนยันก่อน (กันลบพลาด)
    return render(request, 'portfolios/delete_confirm.html', {'item': portfolio_item})


def portfolio_detail(request, username, pk):
    """หน้าแสดงรายละเอียดผลงานแบบเต็ม"""
    # ค้นหาผลงานจาก ID (pk) และต้องตรงกับเจ้าของ (username) ด้วย
    item = get_object_or_404(PortfolioItem, pk=pk, owner__username=username)
    
    # Check Privacy: ถ้าเจ้าของปิด Public และคนดูไม่ใช่เจ้าของ -> ห้ามดู
    if not item.owner.profile.is_public:
        if request.user != item.owner:
            return render(request, '404_private.html', status=404)

    return render(request, 'portfolios/portfolio_detail.html', {'item': item})



@login_required
def download_portfolio_pdf(request):
    """สร้างไฟล์ PDF Portfolio พร้อม QR Code"""
    user = request.user
    
    try:
        profile = user.profile  
    except:
        profile = None

    items = PortfolioItem.objects.filter(owner=user).order_by('-event_date')

    # ==========================================
    # ✅ 1. สร้าง QR Code
    # ==========================================
    
    # สร้าง URL ของหน้า Public Portfolio แบบเต็ม (รวม http://domain.com)
    public_url = request.build_absolute_uri(reverse('public_portfolio', args=[user.username]))
    
    # สร้างรูป QR Code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M, # M = กู้คืนข้อมูลได้ 15% (เผื่อปริ้นท์ไม่ชัด)
        box_size=10,
        border=2,
    )
    qr.add_data(public_url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    # บันทึกลง Buffer (Memory) แทนการลงไฟล์
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    
    # แปลงเป็น Base64 string เพื่อส่งไปแปะใน HTML ได้เลย
    qr_image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')


    # ==========================================
    # 2. เตรียม Context และ Render
    # ==========================================
    context = {
        'user': user,
        'profile': profile,
        'items': items,
        'request': request,
        'qr_code': qr_image_base64, # ✅ ส่ง QR Code ไปที่ Template
    }

    html_string = render_to_string('portfolios/pdf_template.html', context)
    base_url = request.build_absolute_uri('/')

    html = HTML(string=html_string, base_url=base_url)
    pdf_file = html.write_pdf()

    response = HttpResponse(pdf_file, content_type='application/pdf')
    filename = f"Portfolio_{user.username}.pdf"
    response['Content-Disposition'] = f'inline; filename="{filename}"'
    
    return response