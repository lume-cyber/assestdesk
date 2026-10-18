from django.contrib import admin
from .models import AssetList, Membership, AssetEvent
class MembershipInline(admin.TabularInline):
    model = Membership
    extra = 1
    autocomplete_fields = ['user']
@admin.register(AssetList)
class AssetListAdmin(admin.ModelAdmin):
    list_display = ['name','description']
    search_fields = ['name']
    inlines = [MembershipInline]
@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = ['user','asset_list','role']
    list_filter = ['role','asset_list']
    autocomplete_fields = ['user','asset_list']
@admin.register(AssetEvent)
class AssetEventAdmin(admin.ModelAdmin):
    list_display = ['asset','actor','action','created_at']
    def has_add_permission(self,request): return False
    def has_change_permission(self,request,obj=None): return False
    def has_delete_permission(self,request,obj=None): return False
