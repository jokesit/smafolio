from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from portfolios.views import ( home, dashboard, edit_profile, create_portfolio,
                              portfolio_view, edit_portfolio, delete_portfolio,
                              portfolio_detail, download_portfolio_pdf )



urlpatterns = [
    path('admin/', admin.site.urls),

    # ระบบสมาชิก (Login/Register/Logout)
    path('accounts/', include('allauth.urls')),

    # Theme (Tailwind)
    path("__reload__/", include("django_browser_reload.urls")),

    path('', home, name='home'),
    path('dashboard/', dashboard, name='dashboard'),
    path('dashboard/download-pdf/', download_portfolio_pdf, name='download_portfolio_pdf'),
    path('profile/edit/', edit_profile, name='edit_profile'),
    path('portfolio/create/', create_portfolio, name='create_portfolio'),
    path('portfolio/edit/<int:pk>/', edit_portfolio, name='edit_portfolio'),
    path('portfolio/delete/<int:pk>/', delete_portfolio, name='delete_portfolio'),
    path('<str:username>/item/<int:pk>/', portfolio_detail, name='portfolio_detail'),




    # --- วางไว้ล่างสุดเสมอ ---
    path('<str:username>/', portfolio_view, name='public_portfolio'),
]

# สำหรับแสดงรูปภาพในโหมด Debug (Dev mode)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)