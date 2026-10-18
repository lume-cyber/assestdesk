from django.contrib.auth.models import User
from django.test import TestCase, Client, override_settings
from .models import AssetList, Asset, Membership, AssetEvent
from .access import permitted_lists

@override_settings(SECURE_SSL_REDIRECT=False,STORAGES={'default':{'BACKEND':'django.core.files.storage.FileSystemStorage'},'staticfiles':{'BACKEND':'django.contrib.staticfiles.storage.StaticFilesStorage'}})
class AccessTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser('admin','admin@example.test','StrongPassword!982')
        self.viewer = User.objects.create_user('viewer',password='StrongPassword!982')
        self.editor = User.objects.create_user('editor',password='StrongPassword!982')
        self.outsider = User.objects.create_user('outsider',password='StrongPassword!982')
        self.public = AssetList.objects.create(name='Office IT')
        self.secret = AssetList.objects.create(name='Restricted finance')
        Membership.objects.create(user=self.viewer,asset_list=self.public,role='viewer')
        Membership.objects.create(user=self.editor,asset_list=self.public,role='editor')
        self.a = Asset.objects.create(asset_list=self.public,tag='IT-001',name='Office laptop')
        self.b = Asset.objects.create(asset_list=self.secret,tag='FIN-001',name='Secret laptop')
    def payload(self,**kwargs):
        return dict(tag='IT-002',name='New laptop',asset_list=self.public.pk,category='Laptop',status='available',**kwargs)
    def test_anonymous_is_redirected(self):
        for path in ['/',f'/assets/{self.a.pk}/','/assets/export/','/assets/new/']:
            self.assertEqual(self.client.get(path).status_code,302)
    def test_viewer_scope_and_metrics(self):
        self.client.force_login(self.viewer)
        r=self.client.get('/')
        self.assertContains(r,'Office laptop'); self.assertNotContains(r,'Secret laptop'); self.assertNotContains(r,'Restricted finance')
        self.assertEqual(r.context['total'],1)
        self.assertEqual(self.client.get(f'/assets/{self.b.pk}/').status_code,404)
        self.assertEqual(self.client.get(f'/?list={self.secret.pk}').context['page'].paginator.count,0)
        self.assertEqual(self.client.get('/?q=Secret').context['page'].paginator.count,0)
    def test_viewer_cannot_inherit_another_members_editor_role(self):
        self.assertFalse(permitted_lists(self.viewer,True).exists())
        self.client.force_login(self.viewer)
        self.assertEqual(self.client.get(f'/assets/{self.a.pk}/edit/').status_code,404)
        self.assertEqual(self.client.post('/assets/new/',self.payload()).status_code,403)
        self.assertEqual(self.client.post(f'/assets/{self.a.pk}/edit/',self.payload()).status_code,404)
    def test_editor_can_create_and_update_with_history(self):
        self.client.force_login(self.editor)
        self.assertEqual(self.client.post('/assets/new/',self.payload()).status_code,302)
        asset=Asset.objects.get(tag='IT-002')
        self.assertEqual(AssetEvent.objects.get(asset=asset).actor,self.editor)
        data=self.payload(); data['name']='Updated laptop'
        self.assertEqual(self.client.post(f'/assets/{asset.pk}/edit/',data).status_code,302)
        asset.refresh_from_db(); self.assertEqual(asset.name,'Updated laptop')
        self.assertEqual(asset.events.count(),2)
        self.assertContains(self.client.get(f'/assets/{asset.pk}/'),'Updated laptop')
    def test_editor_cannot_move_or_create_in_hidden_list(self):
        self.client.force_login(self.editor)
        data=self.payload(); data['asset_list']=self.secret.pk
        self.assertEqual(self.client.post('/assets/new/',data).status_code,200)
        self.assertFalse(Asset.objects.filter(tag='IT-002').exists())
        data['tag']=self.a.tag
        self.assertEqual(self.client.post(f'/assets/{self.a.pk}/edit/',data).status_code,200)
        self.a.refresh_from_db(); self.assertEqual(self.a.asset_list,self.public)
        self.assertEqual(self.client.post(f'/assets/{self.b.pk}/edit/',data).status_code,404)
    def test_no_memberships_means_no_access(self):
        self.client.force_login(self.outsider)
        self.assertEqual(self.client.get('/').context['total'],0)
        self.assertEqual(self.client.get(f'/assets/{self.a.pk}/').status_code,404)
    def test_revoked_access_applies_immediately(self):
        self.client.force_login(self.viewer)
        Membership.objects.filter(user=self.viewer).delete()
        self.assertEqual(self.client.get(f'/assets/{self.a.pk}/').status_code,404)
    def test_exports_obey_permissions_and_neutralize_formulas(self):
        self.a.name='=HYPERLINK("https://example.test")'; self.a.save()
        self.client.force_login(self.viewer)
        r=self.client.get('/assets/export/')
        self.assertContains(r,"'=HYPERLINK"); self.assertNotContains(r,'FIN-001')
        self.assertNotContains(self.client.get(f'/assets/export/?list={self.secret.pk}'),'IT-001')
    def test_admin_and_nonadmin_access(self):
        self.client.force_login(self.admin)
        self.assertEqual(self.client.get('/').context['total'],2)
        for path in ['/admin/','/admin/auth/user/','/admin/inventory/assetlist/','/assets/new/']:
            self.assertEqual(self.client.get(path).status_code,200)
        self.viewer.is_staff=True; self.viewer.save()
        self.client.force_login(self.viewer)
        self.assertEqual(self.client.get('/admin/').status_code,302)
    def test_csrf_required(self):
        client=Client(enforce_csrf_checks=True); client.force_login(self.editor)
        self.assertEqual(client.post('/assets/new/',self.payload()).status_code,403)
    def test_assigned_requires_employee(self):
        self.client.force_login(self.editor)
        data=self.payload(); data['status']='assigned'
        self.assertContains(self.client.post('/assets/new/',data),'Enter the employee')
        self.assertFalse(Asset.objects.filter(tag='IT-002').exists())
    def test_login_and_inactive_account(self):
        self.assertEqual(self.client.post('/accounts/login/',{'username':'editor','password':'StrongPassword!982'}).status_code,302)
        self.client.logout(); self.editor.is_active=False; self.editor.save()
        self.assertEqual(self.client.post('/accounts/login/',{'username':'editor','password':'StrongPassword!982'}).status_code,200)
    def test_brute_force_lockout(self):
        for _ in range(5):
            self.client.post('/accounts/login/',{'username':'viewer','password':'wrong'})
        self.assertEqual(self.client.post('/accounts/login/',{'username':'viewer','password':'StrongPassword!982'}).status_code,429)
    def test_account_password_change(self):
        self.client.force_login(self.editor)
        self.assertEqual(self.client.get('/accounts/password/').status_code,200)
        r=self.client.post('/accounts/password/',{'old_password':'StrongPassword!982','new_password1':'AnotherSecurePassword!892','new_password2':'AnotherSecurePassword!892'})
        self.assertEqual(r.status_code,302)
        self.editor.refresh_from_db(); self.assertTrue(self.editor.check_password('AnotherSecurePassword!892'))
    def test_asset_pages_are_not_cached(self):
        self.client.force_login(self.viewer)
        for url in ['/',f'/assets/{self.a.pk}/','/assets/export/']:
            self.assertIn('no-store',self.client.get(url)['Cache-Control'])


class ProxyTests(TestCase):
    def test_untrusted_forwarding_is_ignored(self):
        from unittest.mock import patch
        from django.test import RequestFactory
        from .security import client_ip
        request=RequestFactory().get('/',REMOTE_ADDR='192.0.2.1',HTTP_X_FORWARDED_FOR='198.51.100.2')
        with patch.dict('os.environ',{'TRUST_PROXY':'0'}):
            self.assertEqual(client_ip(request),'192.0.2.1')
        with patch.dict('os.environ',{'TRUST_PROXY':'1'}):
            self.assertEqual(client_ip(request),'198.51.100.2')
