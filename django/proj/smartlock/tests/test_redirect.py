from django.contrib.auth.models import User
import smartlock.models
from django.test import TestCase
from django.test import Client

class RedirectURL(TestCase):

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

    def test_user_redirect_home(self):
        self.c.login(username='test', password='test')
        response = self.client.get('/')
        self.assertRedirects(response, '/smartlock/', target_status_code=302)

    def test_adm_redirect_home(self):
        self.c.login(username='testAdm', password='testAdm')
        response = self.client.get('/')
        self.assertRedirects(response, '/smartlock/', target_status_code=302)

    def test_notuser_redirect_home(self):
        response = self.client.get('/')
        self.assertRedirects(response, '/smartlock/', target_status_code=302)

    def test_user_redirect_manage(self):
        self.c.login(username='test', password='test')
        response = self.client.get('/smartlock/manage/')
        self.assertRedirects(response, '/smartlock/manage/users/', target_status_code=302)

    def test_adm_redirect_manage(self):
        self.c.login(username='testAdm', password='testAdm')
        response = self.client.get('/smartlock/manage/')
        self.assertRedirects(response, '/smartlock/manage/users/', target_status_code=302)

    def test_notuser_redirect_manage(self):
        response = self.client.get('/smartlock/manage/')
        self.assertRedirects(response, '/smartlock/manage/users/', target_status_code=302)

    def test_notuser_redirect_nexts(self):
        urls = ["/smartlock/", "/smartlock/account/", "/smartlock/manage/lock_groups/", "/smartlock/manage/users/",                
                "/smartlock/manage/users/new_user/", "/smartlock/manage/user_groups/", "/smartlock/manage/locks/",
                "/smartlock/manage/user_groups/new_user_group/",  "/smartlock/manage/locks/new_lock/", 
                "/smartlock/manage/lock_groups/new_lock_group/", "/smartlock/manage/unlockattemptlog/"]
        for url in urls:
            response = self.client.get(url)
            self.assertRedirects(response, '/accounts/login/?next=' + url)