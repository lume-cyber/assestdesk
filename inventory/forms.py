from django import forms
from .models import Asset
from .access import permitted_lists
class AssetForm(forms.ModelForm):
    class Meta:
        model = Asset
        fields = ['tag','name','asset_list','category','status','manufacturer','model','serial_number','assigned_to','location','purchase_date','warranty_expires','notes']
        widgets = {'purchase_date':forms.DateInput(attrs={'type':'date'}),'warranty_expires':forms.DateInput(attrs={'type':'date'}),'notes':forms.Textarea(attrs={'rows':4})}
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
        return data

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
