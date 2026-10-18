import io
from PIL import Image
from django.test import TestCase, override_settings
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import Asset, AssetList, Membership, AssignmentRecord

@override_settings(SECURE_SSL_REDIRECT=False, STORAGES={'default':{'BACKEND':'django.core.files.storage.FileSystemStorage'},'staticfiles':{'BACKEND':'django.contrib.staticfiles.storage.StaticFilesStorage'}})
class RecordsTest(TestCase):
    def setUp(self):
        self.editor = User.objects.create_user('editor')
        self.viewer = User.objects.create_user('viewer')
        self.list = AssetList.objects.create(name='IT')
        self.asset = Asset.objects.create(asset_list=self.list, tag='A1', name='Laptop')
        Membership.objects.create(user=self.editor, asset_list=self.list, role='editor')
        Membership.objects.create(user=self.viewer, asset_list=self.list, role='viewer')
        self.client.force_login(self.editor)
    def test_photo_private_and_viewer_cannot_write(self):
        out=io.BytesIO(); Image.new('RGB',(10,10)).save(out,format='PNG')
        url=f'/assets/{self.asset.pk}/records/photo/'
        self.assertEqual(self.client.post(url,{'photo':SimpleUploadedFile('photo.png',out.getvalue(),content_type='image/png')}).status_code,302)
        photo=f'/assets/{self.asset.pk}/photo/'
        self.client.force_login(self.viewer)
        self.assertEqual(self.client.get(photo).status_code,200)
        self.assertEqual(self.client.post(url,{'remove':'on'}).status_code,404)
        Membership.objects.filter(user=self.viewer).delete()
        self.assertEqual(self.client.get(photo).status_code,404)
        self.client.force_login(self.editor)
        self.client.post(url,{'remove':'on'})
        self.assertEqual(self.client.get(photo).status_code,404)
    def test_service_validation(self):
        url=f'/assets/{self.asset.pk}/records/service/'
        data={'service_date':'2026-09-08','issue':'Fan','work_performed':'Replaced fan','cost':'-5','currency':'BDT'}
        self.assertEqual(self.client.post(url,data).status_code,200)
        self.assertEqual(self.asset.services.count(),0)
        data['cost']='50'
        self.assertEqual(self.client.post(url,data).status_code,302)
        self.assertEqual(self.asset.services.count(),1)
        self.client.force_login(self.viewer)
        self.assertEqual(self.client.post(url,data).status_code,404)
        self.assertContains(self.client.get(f'/assets/{self.asset.pk}/'),'Replaced fan')
    def test_assignment_return_and_duplicate(self):
        url=f'/assets/{self.asset.pk}/records/assignment/'
        data={'employee':'Alex','assigned_date':'2026-09-08'}
        self.assertEqual(self.client.post(url,data).status_code,302)
        self.asset.refresh_from_db(); self.assertEqual(self.asset.assigned_to,'Alex')
        self.assertEqual(self.client.post(url, data).status_code,200)
        record=self.asset.assignments.get()
        data['returned_date']='2026-09-07'
        edit=f'{url}{record.pk}/'
        self.assertEqual(self.client.post(edit,data).status_code,200)
        data['returned_date']='2026-09-09'
        self.assertEqual(self.client.post(edit,data).status_code,302)
        self.asset.refresh_from_db(); self.assertEqual(self.asset.assigned_to,'')
    def test_multiple_admins(self):
        for name in ['admin1','admin2']:
            admin=User.objects.create_superuser(name,password='test-administrator-password')
            self.client.force_login(admin)
            self.assertEqual(self.client.get('/admin/auth/user/').status_code,200)
