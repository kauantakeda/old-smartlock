from django.contrib.auth.models import User
from django import urls
from django.test import TestCase
from django.test import Client
from django import urls

import smartlock.models

class ViewPermissions(TestCase):

    def setUp(self):
        self.c = Client()
        self.user = User.objects.create_user(username='test', password='test')
        self.userData = smartlock.models.UserData.objects.create(user=self.user, rfid='e9eb9e6h')
        self.userAdm = User.objects.create_user(username='testAdm', password='testAdm')
        self.userDataAdm = smartlock.models.UserData.objects.create(user=self.userAdm, rfid='e9eb9e6t', admin=True)

    def tearDown(self):
        self.userData.delete()
        self.user.delete()
        self.userDataAdm.delete()
        self.userAdm.delete()

    def test_user_view_home(self):
        self.c.login(username='test', password='test')
        response = self.c.get(urls.reverse('smartlock:index'))
        self.assertEqual(response.status_code, 200, u'user should have access')

    def test_adm_view_home(self):
        self.c.login(username='testAdm', password='testAdm')
        response = self.c.get(urls.reverse('smartlock:index'))
        self.assertEqual(response.status_code, 200, u'adm should have access')

    def test_notuser_view_home(self):
        response = self.c.get(urls.reverse('smartlock:index'))
        self.assertEqual(response.status_code, 302, u'Not logged user should not have access')

    def test_user_view_account(self):
        self.c.login(username='test', password='test')
        response = self.c.get(urls.reverse('smartlock:account'))
        self.assertEqual(response.status_code, 200, u'user should have access')

    def test_adm_view_account(self):
        self.c.login(username='testAdm', password='testAdm')
        response = self.c.get(urls.reverse('smartlock:account'))
        self.assertEqual(response.status_code, 200, u'adm should have access')

    def test_notuser_view_account(self):
        response = self.c.get(urls.reverse('smartlock:account'))
        self.assertEqual(response.status_code, 302, u'Not logged user should not have access')

    # def test_user_view_users(self):
    #     self.c.login(username='test', password='test')
    #     response = self.c.get(urls.reverse('smartlock:users'))
    #     self.assertEqual(response.status_code, 302, u'user should not have access')

    def test_adm_view_users(self):
        self.c.login(username='testAdm', password='testAdm')
        response = self.c.get(urls.reverse('smartlock:users'))
        self.assertEqual(response.status_code, 200, u'adm should have access')

    def test_notuser_view_users(self):
        response = self.c.get(urls.reverse('smartlock:users'))
        self.assertEqual(response.status_code, 302, u'Not logged user should not have access')

    # def test_user_view_newuser(self):
    #     self.c.login(username='test', password='test')
    #     response = self.c.get(urls.reverse('smartlock:new_user'))
    #     self.assertEqual(response.status_code, 302, u'user should not have access')

    def test_adm_view_newuser(self):
        self.c.login(username='testAdm', password='testAdm')
        response = self.c.get(urls.reverse('smartlock:new_user'))
        self.assertEqual(response.status_code, 200, u'adm should have access')

    def test_notuser_view_newuser(self):
        response = self.c.get(urls.reverse('smartlock:new_user'))
        self.assertEqual(response.status_code, 302, u'Not logged user should not have access')

    # def test_user_view_usergroups(self):
    #     self.c.login(username='test', password='test')
    #     response = self.c.get(urls.reverse('smartlock:user_groups'))
    #     self.assertEqual(response.status_code, 302, u'user should not have access')

    def test_adm_view_usergroups(self):
        self.c.login(username='testAdm', password='testAdm')
        response = self.c.get(urls.reverse('smartlock:user_groups'))
        self.assertEqual(response.status_code, 200, u'adm should have access')

    def test_notuser_view_usergroups(self):
        response = self.c.get(urls.reverse('smartlock:user_groups'))
        self.assertEqual(response.status_code, 302, u'Not logged user should not have access')

    # def test_user_view_newusergroup(self):
    #     self.c.login(username='test', password='test')
    #     response = self.c.get(urls.reverse('smartlock:new_user_group'))
    #     self.assertEqual(response.status_code, 302, u'user should not have access')

    def test_adm_view_newusergroup(self):
        self.c.login(username='testAdm', password='testAdm')
        response = self.c.get(urls.reverse('smartlock:new_user_group'))
        self.assertEqual(response.status_code, 200, u'adm should have access')

    def test_notuser_view_newusergroup(self):
        response = self.c.get(urls.reverse('smartlock:new_user_group'))
        self.assertEqual(response.status_code, 302, u'Not logged user should not have access')

    # def test_user_view_locks(self):
    #     self.c.login(username='test', password='test')
    #     response = self.c.get(urls.reverse('smartlock:locks'))
    #     self.assertEqual(response.status_code, 302, u'user should not have access')

    def test_adm_view_locks(self):
        self.c.login(username='testAdm', password='testAdm')
        response = self.c.get(urls.reverse('smartlock:locks'))
        self.assertEqual(response.status_code, 200, u'adm should have access')

    def test_notuser_view_locks(self):
        response = self.c.get(urls.reverse('smartlock:locks'))
        self.assertEqual(response.status_code, 302, u'Not logged user should not have access')

    # def test_user_view_newlock(self):
    #     self.c.login(username='test', password='test')
    #     response = self.c.get(urls.reverse('smartlock:new_lock'))
    #     self.assertEqual(response.status_code, 302, u'user should not have access')

    def test_adm_view_newlock(self):
        self.c.login(username='testAdm', password='testAdm')
        response = self.c.get(urls.reverse('smartlock:new_lock'))
        self.assertEqual(response.status_code, 200, u'adm should have access')

    def test_notuser_view_newlock(self):
        response = self.c.get(urls.reverse('smartlock:new_lock'))
        self.assertEqual(response.status_code, 302, u'Not logged user should not have access')

    # def test_user_view_lockgroups(self):
    #     self.c.login(username='test', password='test')
    #     response = self.c.get(urls.reverse('smartlock:lock_groups'))
    #     self.assertEqual(response.status_code, 302, u'user should not have access')

    def test_adm_view_lockgroups(self):
        self.c.login(username='testAdm', password='testAdm')
        response = self.c.get(urls.reverse('smartlock:lock_groups'))
        self.assertEqual(response.status_code, 200, u'adm should have access')

    def test_notuser_view_lockgroups(self):
        response = self.c.get(urls.reverse('smartlock:lock_groups'))
        self.assertEqual(response.status_code, 302, u'Not logged user should not have access')

    # def test_user_view_newlockgroup(self):
    #     self.c.login(username='test', password='test')
    #     response = self.c.get(urls.reverse('smartlock:new_lock_group'))
    #     self.assertEqual(response.status_code, 302, u'user should not have access')

    def test_adm_view_newlockgroup(self):
        self.c.login(username='testAdm', password='testAdm')
        response = self.c.get(urls.reverse('smartlock:new_lock_group'))
        self.assertEqual(response.status_code, 200, u'adm should have access')

    def test_notuser_view_newlockgroup(self):
        response = self.c.get(urls.reverse('smartlock:new_lock_group'))
        self.assertEqual(response.status_code, 302, u'Not logged user should not have access')

    # def test_user_view_unlocklog(self):
    #     self.c.login(username='test', password='test')
    #     response = self.c.get(urls.reverse('smartlock:logs'))
    #     self.assertEqual(response.status_code, 302, u'user should not have access')

    def test_adm_view_unlocklog(self):
        self.c.login(username='testAdm', password='testAdm')
        response = self.c.get(urls.reverse('smartlock:logs'))
        self.assertEqual(response.status_code, 200, u'adm should have access')

    def test_notuser_view_unlocklog(self):
        response = self.c.get(urls.reverse('smartlock:logs'))
        self.assertEqual(response.status_code, 302, u'Not logged user should not have access')

# /smartlock/manage/users/{id}
# /smartlock/manage/user_groups/{id}
# /smartlock/manage/locks/{id}
# /smartlock/manage/lock_groups/{id}
