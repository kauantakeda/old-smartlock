from django.http import HttpRequest
import smartlock.models
from django.contrib.auth.models import User
from django.test import TestCase
from django import urls
from django.utils import timezone

class DoorUnlockSimple(TestCase):

    invalid_lockid = -1

    def test_unlock_post_valid(self):
        validUser = User.objects.create_user(username='valid')
        validUserData = smartlock.models.UserData.objects.create(user=validUser, rfid='e9eb9e6d')
        tmzn = smartlock.models.TimeZone.objects.create(name='America/Sao_Paulo')
        doorLock = smartlock.models.Lock.objects.create(name='door', tmzn=tmzn)
        weekday = timezone.now().strftime('%A').lower()[:4]
        schedule = smartlock.models.Schedule.objects.create(userdata=validUserData, lock=doorLock, dt_strt='2019-05-06', dt_stop='2019-12-09')
        setattr(schedule, weekday, True)
        schedule.save()

        response = self.client.post(urls.reverse('smartlock:unlock'), dict(ruid=doorLock.ruid, rfid=validUserData.rfid))
        self.assertContains(response, 'request accepted, open')

    def test_unlock_post_invalid_lockid(self):
        validUser = User.objects.create_user(username='valid')
        validUserData = smartlock.models.UserData.objects.create(user=validUser, rfid='e9eb9e6d')
        tmzn = smartlock.models.TimeZone.objects.create(name='America/Sao_Paulo')
        doorLock = smartlock.models.Lock.objects.create(name='door', tmzn=tmzn)
        weekday = timezone.now().strftime('%A').lower()[:4]
        schedule = smartlock.models.Schedule.objects.create(userdata=validUserData, lock=doorLock, dt_strt='2019-05-06', dt_stop='2019-12-09')
        setattr(schedule, weekday, True)
        schedule.save()

        response = self.client.post(urls.reverse('smartlock:unlock'), dict(ruid=self.invalid_lockid, rfid=validUserData.rfid))
        self.assertContains(response, 'request denied')

    def test_unlock_post_invalid_rfid(self):
        invalidUser = User.objects.create_user(username='invalid')
        invalidUserData = smartlock.models.UserData.objects.create(user=invalidUser, rfid='abcderf')
        tmzn = smartlock.models.TimeZone.objects.create(name='America/Sao_Paulo')
        doorLock = smartlock.models.Lock.objects.create(name='door', tmzn=tmzn)
        #no permission created because the user is invalid
        
        response = self.client.post(urls.reverse('smartlock:unlock'), dict(ruid=doorLock.ruid, rfid=invalidUserData.rfid))
        self.assertContains(response, 'request denied')
