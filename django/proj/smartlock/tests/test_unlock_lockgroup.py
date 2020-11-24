from django.http import HttpRequest
import smartlock.models
from django.contrib.auth.models import User
from django.test import TestCase
from django import urls
from django.utils import timezone

class DoorUnlockLockGroup(TestCase):# tests for lock groups

    invalid_lockid = -1

    def test_unlock_post_valid(self):
        validUser = User.objects.create_user(username='valid')
        validUserData = smartlock.models.UserData.objects.create(user=validUser, rfid='e9eb9e6d')
        tmzn = smartlock.models.TimeZone.objects.create(name='America/Sao_Paulo')
        doorLockValid1 = smartlock.models.Lock.objects.create(name='doorValid1', tmzn=tmzn)
        doorLockValid2 = smartlock.models.Lock.objects.create(name='doorValid2', tmzn=tmzn)

        doorLockGroup = smartlock.models.LockGroup.objects.create(name='doorGroup')
        doorLockGroup.grup.add(doorLockValid1)
        doorLockGroup.grup.add(doorLockValid2)
        weekday = timezone.now().strftime('%A').lower()[:4]
        schedule1 = smartlock.models.Schedule.objects.create(userdata=validUserData, lock=doorLockValid1, dt_strt='2019-05-06', dt_stop='2019-12-09')
        setattr(schedule1, weekday, True)
        schedule1.save()
        schedule2 = smartlock.models.Schedule.objects.create(userdata=validUserData, lock=doorLockValid2, dt_strt='2019-05-06', dt_stop='2019-12-09')
        setattr(schedule2, weekday, True)
        schedule2.save()

        response = self.client.post(urls.reverse('smartlock:unlock'), dict(ruid=doorLockValid1.ruid, rfid=validUserData.rfid))
        self.assertContains(response, 'request accepted, open')
        response = self.client.post(urls.reverse('smartlock:unlock'), dict(ruid=doorLockValid2.ruid, rfid=validUserData.rfid))
        self.assertContains(response, 'request accepted, open')

    def test_unlock_post_invalid_lockid(self):
        validUser = User.objects.create_user(username='valid')
        validUserData = smartlock.models.UserData.objects.create(user=validUser, rfid='e9eb9e6d')
        tmzn = smartlock.models.TimeZone.objects.create(name='America/Sao_Paulo')
        doorLockInvalid1 = smartlock.models.Lock.objects.create(name='doorInvalid1', tmzn=tmzn)
        doorLockInvalid2 = smartlock.models.Lock.objects.create(name='doorInvalid2', tmzn=tmzn)

        doorLockGroup = smartlock.models.LockGroup.objects.create(name='doorGroup')
        doorLockGroup.grup.add(doorLockInvalid1)
        doorLockGroup.grup.add(doorLockInvalid2)

        weekday = timezone.now().strftime('%A').lower()[:4]
        schedule = smartlock.models.Schedule.objects.create(userdata=validUserData, lock=doorLockInvalid1, dt_strt='2019-05-06', dt_stop='2019-12-09')
        setattr(schedule, weekday, True)
        schedule.save()

        response = self.client.post(urls.reverse('smartlock:unlock'), dict(ruid=self.invalid_lockid, rfid=validUserData.rfid))
        self.assertContains(response, 'request denied')

    def test_unlock_post_invalid_rfid(self):
        invalidUser = User.objects.create_user(username='invalid')
        invalidUserData = smartlock.models.UserData.objects.create(user=invalidUser, rfid='abcderf')
        tmzn = smartlock.models.TimeZone.objects.create(name='America/Sao_Paulo')
        doorLockValid1 = smartlock.models.Lock.objects.create(name='doorValid1', tmzn=tmzn)
        doorLockValid2 = smartlock.models.Lock.objects.create(name='doorValid2', tmzn=tmzn)

        doorLockGroup = smartlock.models.LockGroup.objects.create(name='doorGroup')

        doorLockGroup.grup.add(doorLockValid1)
        doorLockGroup.grup.add(doorLockValid2)
        #no permission created because the user is invalid
        
        response = self.client.post(urls.reverse('smartlock:unlock'), dict(ruid=doorLockValid1.ruid, rfid=invalidUserData.rfid))
        self.assertContains(response, 'request denied')
        response = self.client.post(urls.reverse('smartlock:unlock'), dict(ruid=doorLockValid2.ruid, rfid=invalidUserData.rfid))
        self.assertContains(response, 'request denied')
