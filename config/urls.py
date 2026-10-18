from django.contrib import admin
from django.contrib.auth import views as auth
from django.urls import path
from inventory import views
admin.site.site_header = 'Assetdesk administration'
admin.site.site_title = 'Assetdesk'
admin.site.index_title = 'Accounts, lists and permissions'
admin.site.has_permission = lambda request: request.user.is_active and request.user.is_superuser
urlpatterns = [
 path('admin/',admin.site.urls),
 path('accounts/login/',auth.LoginView.as_view(),name='login'),
 path('accounts/logout/',auth.LogoutView.as_view(),name='logout'),
 path('accounts/password/',auth.PasswordChangeView.as_view(template_name='registration/password_change.html',success_url='/'),name='password_change'),
 path('',views.home,name='home'),
 path('assets/new/',views.asset_edit,name='asset_new'),
 path('assets/import/',views.import_assets,name='import_assets'),
 path('assets/export/',views.export_assets,name='export'),
 path('assets/<int:pk>/photo/',views.asset_photo,name='asset_photo'),
 path('assets/<int:pk>/records/<str:kind>/',views.asset_record,name='asset_record'),
 path('assets/<int:pk>/records/<str:kind>/<int:record_pk>/',views.asset_record,name='record_edit'),
 path('assets/<int:pk>/',views.detail,name='detail'),
 path('assets/<int:pk>/edit/',views.asset_edit,name='asset_edit'),
]
