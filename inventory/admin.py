from django.contrib import admin
from .models import AssetEvent
@admin.register(AssetEvent)
class AssetEventAdmin(admin.ModelAdmin):
    list_display = ['asset','actor','action','created_at']
    def has_add_permission(self,request): return False
    def has_change_permission(self,request,obj=None): return False
    def has_delete_permission(self,request,obj=None): return False
