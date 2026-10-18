from .models import AssetList, Asset

def permitted_lists(user,write=False):
    if not user.is_authenticated or not user.is_active: return AssetList.objects.none()
    if user.is_superuser: return AssetList.objects.all()
    filters = {'memberships__user':user}
    if write: filters['memberships__role'] = 'editor'
    query = AssetList.objects.filter(**filters)
    return query.distinct()

def permitted_assets(user,write=False):
    return Asset.objects.filter(asset_list__in=permitted_lists(user,write)).select_related('asset_list')
