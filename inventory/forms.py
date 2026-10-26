from django import forms
from django.contrib.auth import password_validation
from django.contrib.auth.models import User
from .models import Asset, AssetList, Membership, UserProfile
from .access import permitted_lists
class AssetForm(forms.ModelForm):
    class Meta:
        model = Asset
        fields = ['tag','name','asset_list','category','status','manufacturer','model','serial_number','assigned_to','location','purchase_date','purchase_value','purchase_currency','warranty_expires','notes']
        widgets = {'category':forms.TextInput(attrs={'list':'product-categories'}),'purchase_date':forms.DateInput(attrs={'type':'date'}),'warranty_expires':forms.DateInput(attrs={'type':'date'}),'notes':forms.Textarea(attrs={'rows':4})}
    def __init__(self,*args,user,**kwargs):
        super().__init__(*args,**kwargs)
        self.fields['asset_list'].queryset = permitted_lists(user,write=True)
    def validate_unique(self):
        # Never disclose which hidden list owns a duplicate asset tag.
        super().validate_unique()
        if 'tag' in self.errors:
            self.errors['tag'] = self.error_class(['This asset tag cannot be used. Choose another tag.'])
    def clean(self):
        data = super().clean()
        if data.get('status') == 'assigned' and not data.get('assigned_to'):
            self.add_error('assigned_to','Enter the employee holding this asset.')
        if data.get('purchase_date') and data.get('warranty_expires') and data['warranty_expires'] < data['purchase_date']:
            self.add_error('warranty_expires','Warranty must end on or after the purchase date.')
        if data.get('purchase_value') is not None and data['purchase_value'] < 0:
            self.add_error('purchase_value','Purchase value cannot be negative.')
        if data.get('purchase_value') is not None and not data.get('purchase_currency'):
            self.add_error('purchase_currency','Enter a currency code.')
        return data

class FinanceForm(forms.ModelForm):
    class Meta:
        model = Asset
        fields = ['purchase_date', 'purchase_value', 'purchase_currency']
        widgets = {'purchase_date': forms.DateInput(attrs={'type':'date'})}
    def clean(self):
        data = super().clean()
        if data.get('purchase_value') is not None and data['purchase_value'] < 0:
            self.add_error('purchase_value','Purchase value cannot be negative.')
        if data.get('purchase_value') is not None and not data.get('purchase_currency'):
            self.add_error('purchase_currency','Enter a currency code.')
        return data

class AssetListForm(forms.ModelForm):
    class Meta:
        model = AssetList
        fields = ['name','description']

class MembershipForm(forms.ModelForm):
    class Meta:
        model = Membership
        fields = ['user','role']
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.fields['user'].queryset = User.objects.filter(is_active=True,is_superuser=False).order_by('username')

class ManagedUserCreateForm(forms.Form):
    username = forms.CharField(max_length=150)
    first_name = forms.CharField(max_length=150, required=False)
    last_name = forms.CharField(max_length=150, required=False)
    email = forms.EmailField(required=False)
    role = forms.ChoiceField()
    password1 = forms.CharField(widget=forms.PasswordInput, label='Password')
    password2 = forms.CharField(widget=forms.PasswordInput, label='Confirm password')
    def __init__(self,*args,manager,**kwargs):
        super().__init__(*args,**kwargs)
        choices = list(UserProfile.ROLES)
        if manager.is_superuser: choices.insert(0,('super_admin','Super admin'))
        self.fields['role'].choices = choices
    def clean_username(self):
        value = self.cleaned_data['username'].strip()
        if User.objects.filter(username__iexact=value).exists(): raise forms.ValidationError('This username is already in use.')
        return value
    def clean(self):
        data = super().clean()
        if data.get('password1') != data.get('password2'): self.add_error('password2','Passwords do not match.')
        if data.get('password1'):
            candidate = User(username=data.get('username',''),first_name=data.get('first_name',''),last_name=data.get('last_name',''),email=data.get('email',''))
            try: password_validation.validate_password(data['password1'], candidate)
            except forms.ValidationError as exc: self.add_error('password1', exc)
        return data
    def save(self):
        role = self.cleaned_data['role']
        user = User(username=self.cleaned_data['username'], first_name=self.cleaned_data['first_name'], last_name=self.cleaned_data['last_name'], email=self.cleaned_data['email'], is_superuser=role=='super_admin', is_staff=role=='super_admin')
        user.set_password(self.cleaned_data['password1']); user.save()
        UserProfile.objects.create(user=user,role=UserProfile.GENERAL_ADMIN if role=='super_admin' else role)
        return user

class ManagedUserEditForm(forms.Form):
    first_name = forms.CharField(max_length=150, required=False)
    last_name = forms.CharField(max_length=150, required=False)
    email = forms.EmailField(required=False)
    role = forms.ChoiceField()
    is_active = forms.BooleanField(required=False)
    new_password1 = forms.CharField(widget=forms.PasswordInput, required=False, label='New password')
    new_password2 = forms.CharField(widget=forms.PasswordInput, required=False, label='Confirm new password')
    def __init__(self,*args,manager,target,**kwargs):
        self.manager,self.target=manager,target
        profile,_=UserProfile.objects.get_or_create(user=target)
        initial=kwargs.setdefault('initial',{})
        initial.update(first_name=target.first_name,last_name=target.last_name,email=target.email,is_active=target.is_active,role='super_admin' if target.is_superuser else profile.role)
        super().__init__(*args,**kwargs)
        choices=list(UserProfile.ROLES)
        if manager.is_superuser: choices.insert(0,('super_admin','Super admin'))
        self.fields['role'].choices=choices
    def clean(self):
        data=super().clean()
        if data.get('new_password1') != data.get('new_password2'): self.add_error('new_password2','Passwords do not match.')
        if data.get('new_password1'):
            try: password_validation.validate_password(data['new_password1'],self.target)
            except forms.ValidationError as exc: self.add_error('new_password1',exc)
        if self.target == self.manager and not self.manager.is_superuser and (data.get('role') != UserProfile.GENERAL_ADMIN or not data.get('is_active')):
            raise forms.ValidationError('A general admin cannot disable or remove their own administrator role.')
        if self.target.is_superuser and (data.get('role')!='super_admin' or not data.get('is_active')) and User.objects.filter(is_superuser=True,is_active=True).count() <= 1:
            raise forms.ValidationError('The last active super admin cannot be removed or disabled.')
        return data
    def save(self):
        user=self.target; role=self.cleaned_data['role']
        user.first_name=self.cleaned_data['first_name']; user.last_name=self.cleaned_data['last_name']; user.email=self.cleaned_data['email']; user.is_active=self.cleaned_data['is_active']; user.is_superuser=role=='super_admin'; user.is_staff=role=='super_admin'
        if self.cleaned_data.get('new_password1'): user.set_password(self.cleaned_data['new_password1'])
        user.save(); profile,_=UserProfile.objects.get_or_create(user=user); profile.role=UserProfile.GENERAL_ADMIN if role=='super_admin' else role; profile.save()
        return user

class PhotoForm(forms.Form):
    photo = forms.ImageField(required=False, help_text='JPEG, PNG or WebP, up to 5 MB.')
    remove = forms.BooleanField(required=False, label='Remove current picture')
    def clean_photo(self):
        photo = self.cleaned_data.get('photo')
        if photo:
            if photo.size > 5 * 1024 * 1024: raise forms.ValidationError('Picture must be 5 MB or smaller.')
            if photo.image.format not in ('JPEG', 'PNG', 'WEBP'): raise forms.ValidationError('Choose a JPEG, PNG or WebP picture.')
            if photo.image.width * photo.image.height > 20000000: raise forms.ValidationError('Picture must be under 20 megapixels.')
        return photo
    def clean(self):
        data = super().clean()
        if bool(data.get('photo')) == bool(data.get('remove')):
            raise forms.ValidationError('Choose a picture or select remove.')
        return data

from .models import ServiceRecord, AssignmentRecord
class ServiceForm(forms.ModelForm):
    class Meta:
        model = ServiceRecord
        fields = ['service_date','issue','work_performed','provider','cost','currency','next_service_date']
        widgets = {f: forms.DateInput(attrs={'type':'date'}) for f in ('service_date','next_service_date')}
    def clean(self):
        data = super().clean()
        if data.get('cost') is not None and data['cost'] < 0: self.add_error('cost','Cost cannot be negative.')
        if data.get('cost') is not None and not data.get('currency'): self.add_error('currency','Enter a currency code.')
        if data.get('next_service_date') and data.get('service_date') and data['next_service_date'] < data['service_date']:
            self.add_error('next_service_date','Next service cannot precede this service.')
        return data

class AssignmentForm(forms.ModelForm):
    class Meta:
        model = AssignmentRecord
        fields = ['employee','assigned_date','returned_date','notes']
        widgets = {f: forms.DateInput(attrs={'type':'date'}) for f in ('assigned_date','returned_date')}
    def clean(self):
        data = super().clean()
        if data.get('returned_date') and data.get('assigned_date') and data['returned_date'] < data['assigned_date']:
            self.add_error('returned_date','Return cannot precede assignment.')
        return data
