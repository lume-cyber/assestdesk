from .models import AssetList, Asset, UserProfile

SUPER_ADMIN = 'super_admin'

def account_role(user):
    if not user.is_authenticated or not user.is_active: return None
    if user.is_superuser: return SUPER_ADMIN
    try: return user.profile.role
    except UserProfile.DoesNotExist: return UserProfile.GENERAL_USER

def can_manage_users(user):
    return account_role(user) in (SUPER_ADMIN, UserProfile.GENERAL_ADMIN)

def can_manage_lists(user):
    return can_manage_users(user)

def can_edit_finance(user):
    return account_role(user) in (SUPER_ADMIN, UserProfile.GENERAL_ADMIN, UserProfile.ACCOUNTS)

def permitted_lists(user,write=False):
    if not user.is_authenticated or not user.is_active: return AssetList.objects.none()
    role = account_role(user)
    if role in (SUPER_ADMIN, UserProfile.GENERAL_ADMIN): return AssetList.objects.all()
    if not write and role in (UserProfile.AUDITOR, UserProfile.ACCOUNTS): return AssetList.objects.all()
    filters = {'memberships__user':user}
    if write: filters['memberships__role'] = 'editor'
    query = AssetList.objects.filter(**filters)
    return query.distinct()

def permitted_assets(user,write=False):
    return Asset.objects.filter(asset_list__in=permitted_lists(user,write)).select_related('asset_list')
