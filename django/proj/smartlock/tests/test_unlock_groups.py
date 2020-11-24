from django.http import HttpRequest
import smartlock.models
from django.contrib.auth.models import User
from django.test import TestCase
from django import urls
from django.utils import timezone

class DoorUnlockGroups(TestCase):# tests for user groups and lock groups

    invalid_lockid = -1

    def test_unlock_post_valid(self):
        validUser1 = User.objects.create_user(username='valid1')
        validUserData1 = smartlock.models.UserData.objects.create(user=validUser1, rfid='e9eb9e6d')
        validUser2 = User.objects.create_user(username='valid2')
        validUserData2 = smartlock.models.UserData.objects.create(user=validUser2, rfid='abcderf')

        doorUserGroup = smartlock.models.UserDataGroup.objects.create(name='userGroup')
        doorUserGroup.grup.add(validUserData1)
        doorUserGroup.grup.add(validUserData2)

        tmzn = smartlock.models.TimeZone.objects.create(name='America/Sao_Paulo')

        doorLockValid1 = smartlock.models.Lock.objects.create(name='doorValid1', tmzn=tmzn)
        doorLockValid2 = smartlock.models.Lock.objects.create(name='doorValid2', tmzn=tmzn)

        doorLockGroup = smartlock.models.LockGroup.objects.create(name='doorGroup')
        doorLockGroup.grup.add(doorLockValid1)
        doorLockGroup.grup.add(doorLockValid2)

        weekday = timezone.now().strftime('%A').lower()[:4]
        schedule = smartlock.models.Schedule.objects.create(userdatagrup=doorUserGroup, lockgrup=doorLockGroup, dt_strt='2019-05-06', dt_stop='2019-12-09')
        setattr(schedule, weekday, True)
        schedule.save()

        response = self.client.post(urls.reverse('smartlock:unlock'), dict(ruid=doorLockValid2.ruid, rfid=validUserData2.rfid))
        self.assertContains(response, 'request accepted, open')

    def test_unlock_post_invalid_lockid(self):
        validUser1 = User.objects.create_user(username='valid1')
        validUserData1 = smartlock.models.UserData.objects.create(user=validUser1, rfid='e9eb9e6d')
        validUser2 = User.objects.create_user(username='valid2')
        validUserData2 = smartlock.models.UserData.objects.create(user=validUser2, rfid='abcderf')

        doorUserGroup = smartlock.models.UserDataGroup.objects.create(name='userGroup')
        doorUserGroup.grup.add(validUserData1)
        doorUserGroup.grup.add(validUserData2)

        tmzn = smartlock.models.TimeZone.objects.create(name='America/Sao_Paulo')

        doorLockInvalid1 = smartlock.models.Lock.objects.create(name='doorInvalid1', tmzn=tmzn)
        doorLockInvalid2 = smartlock.models.Lock.objects.create(name='doorInvalid2', tmzn=tmzn)

        doorLockGroup = smartlock.models.LockGroup.objects.create(name='doorGroup')
        doorLockGroup.grup.add(doorLockInvalid1)
        doorLockGroup.grup.add(doorLockInvalid2)

        weekday = timezone.now().strftime('%A').lower()[:4]
        schedule = smartlock.models.Schedule.objects.create(userdatagrup=doorUserGroup, lockgrup=doorLockGroup, dt_strt='2019-05-06', dt_stop='2019-12-09')
        setattr(schedule, weekday, True)
        schedule.save()

        response = self.client.post(urls.reverse('smartlock:unlock'), dict(ruid=self.invalid_lockid, rfid=validUserData2.rfid))
        self.assertContains(response, 'request denied')

    def test_unlock_post_invalid_rfid(self):
        validUser1 = User.objects.create_user(username='valid1')
        validUserData1 = smartlock.models.UserData.objects.create(user=validUser1, rfid='e9eb9e6d')
        validUser2 = User.objects.create_user(username='valid2')
        validUserData2 = smartlock.models.UserData.objects.create(user=validUser2, rfid='abcderf')
        invalidUser = User.objects.create_user(username='invalid')
        invalidUserData = smartlock.models.UserData.objects.create(user=invalidUser, rfid='abcderf2')

        doorUserGroup = smartlock.models.UserDataGroup.objects.create(name='userGroup')
        doorUserGroup.grup.add(validUserData1)
        doorUserGroup.grup.add(validUserData2)

        tmzn = smartlock.models.TimeZone.objects.create(name='America/Sao_Paulo')

        doorLockValid1 = smartlock.models.Lock.objects.create(name='doorValid1', tmzn=tmzn)
        doorLockValid2 = smartlock.models.Lock.objects.create(name='doorValid2', tmzn=tmzn)

        doorLockGroup = smartlock.models.LockGroup.objects.create(name='doorGroup')

        doorLockGroup.grup.add(doorLockValid1)
        doorLockGroup.grup.add(doorLockValid2)

        weekday = timezone.now().strftime('%A').lower()[:4]
        schedule = smartlock.models.Schedule.objects.create(userdatagrup=doorUserGroup, lockgrup=doorLockGroup, dt_strt='2019-05-06', dt_stop='2019-12-09')
        setattr(schedule, weekday, True)
        schedule.save()

        response = self.client.post(urls.reverse('smartlock:unlock'), dict(ruid=doorLockValid2.ruid, rfid=invalidUserData.rfid))
        self.assertContains(response, 'request denied')
