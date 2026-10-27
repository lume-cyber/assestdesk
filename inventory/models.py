from django.conf import settings
from django.db import models

class UserProfile(models.Model):
    GENERAL_ADMIN = 'general_admin'
    GENERAL_USER = 'general_user'
    AUDITOR = 'auditor'
    ACCOUNTS = 'accounts'
    ROLES = [
        (GENERAL_ADMIN, 'General admin'),
        (GENERAL_USER, 'General user'),
        (AUDITOR, 'Auditor'),
        (ACCOUNTS, 'Accounts'),
    ]
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLES, default=GENERAL_USER)
    def __str__(self): return f'{self.user} · {self.get_role_display()}'

class AssetList(models.Model):
    name = models.CharField(max_length=100,unique=True)
    description = models.CharField(max_length=240,blank=True)
    is_default = models.BooleanField(default=False, help_text='Default access group for unrestricted assets.')
    class Meta: ordering = ['name']
    def __str__(self): return self.name

class ProductCategory(models.Model):
    SHOPIFY, INTERNAL = 'shopify', 'internal'
    SOURCES = [(SHOPIFY, 'Shopify Product Taxonomy'), (INTERNAL, 'Factory taxonomy')]
    name = models.CharField(max_length=150)
    path = models.CharField(max_length=500, unique=True)
    source = models.CharField(max_length=20, choices=SOURCES, default=INTERNAL)
    external_id = models.CharField(max_length=80, blank=True)
    active = models.BooleanField(default=True)
    class Meta: ordering = ['path']
    def __str__(self): return self.path
class Membership(models.Model):
    VIEWER, EDITOR = 'viewer', 'editor'
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    asset_list = models.ForeignKey(AssetList,on_delete=models.CASCADE,related_name='memberships')
    role = models.CharField(max_length=10,choices=[(VIEWER,'Viewer'),(EDITOR,'Editor')],default=VIEWER)
    class Meta:
        constraints = [models.UniqueConstraint(fields=['user','asset_list'],name='unique_list_member')]
    def __str__(self): return f'{self.user} · {self.asset_list} · {self.role}'
class Asset(models.Model):
    CATEGORY_SUGGESTIONS = ['Apparel & Accessories','Arts & Entertainment','Baby & Toddler','Business & Industrial','Cameras & Optics','Electronics','Food, Beverages & Tobacco','Furniture','Hardware','Health & Beauty','Home & Garden','Luggage & Bags','Office Supplies','Software','Sporting Goods','Toys & Games','Vehicles & Parts','Other']
    STATUSES = [('available','Available'),('assigned','Assigned'),('repair','In repair'),('retired','Retired')]
    asset_list = models.ForeignKey(AssetList,on_delete=models.PROTECT,related_name='assets')
    tag = models.CharField(max_length=50,unique=True)
    name = models.CharField(max_length=150)
    category = models.CharField(max_length=150, default='General products')
    status = models.CharField(max_length=15,choices=STATUSES,default='available')
    manufacturer = models.CharField(max_length=100,blank=True)
    model = models.CharField(max_length=100,blank=True)
    serial_number = models.CharField(max_length=100,blank=True)
    assigned_to = models.CharField(max_length=150,blank=True,help_text='Employee name or email; this does not grant access.')
    location = models.CharField(max_length=150,blank=True)
    factory = models.CharField(max_length=150,blank=True)
    department = models.CharField(max_length=150,blank=True)
    purchase_date = models.DateField(null=True,blank=True)
    purchase_value = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    purchase_currency = models.CharField(max_length=3, blank=True, help_text='Currency code, e.g. CAD, USD or BDT')
    warranty_expires = models.DateField(null=True,blank=True)
    notes = models.TextField(blank=True,max_length=5000)
    photo_data = models.BinaryField(blank=True, default=bytes)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta: ordering = ['-updated_at']
    def __str__(self): return f'{self.tag} · {self.name}'
class AssetEvent(models.Model):
    asset = models.ForeignKey(Asset,on_delete=models.CASCADE,related_name='events')
    actor = models.ForeignKey(settings.AUTH_USER_MODEL,null=True,on_delete=models.SET_NULL)
    action = models.CharField(max_length=250)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta: ordering = ['-created_at']

class ServiceRecord(models.Model):
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='services')
    service_date = models.DateField()
    issue = models.CharField(max_length=240)
    work_performed = models.TextField(max_length=5000)
    provider = models.CharField(max_length=150, blank=True)
    cost = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    currency = models.CharField(max_length=3, blank=True, help_text='Currency code, e.g. BDT or USD')
    next_service_date = models.DateField(null=True, blank=True)
    class Meta: ordering = ['-service_date', '-pk']

class AssignmentRecord(models.Model):
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='assignments')
    employee = models.CharField(max_length=150)
    assigned_date = models.DateField(null=True, blank=True)
    returned_date = models.DateField(null=True, blank=True)
    notes = models.TextField(max_length=5000, blank=True)
    class Meta: ordering = ['-pk']
