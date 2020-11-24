from django.http import HttpRequest
import smartlock.models
from django.contrib.auth.models import User
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db import utils
from django.utils import crypto
import string
import random

class UserTester(TestCase):

    def setUp(self):
        User.objects.create_user(username='valid')
        User.objects.create_user(username='valid2')

    def test_valid_user(self):
        validUser = User.objects.get(id=1)
        expected_username = f'{validUser.username}'
        self.assertEquals(expected_username, 'valid')

        validUserData = smartlock.models.UserData.objects.create(user=validUser, rfid='e9eb9e6d')
        expected_userdata_user = f'{validUserData.user.username}'
        self.assertEquals(expected_userdata_user, 'valid')
        expected_userdata_rfid = f'{validUserData.rfid}'
        self.assertEquals(expected_userdata_rfid, "e9eb9e6d")

    def test_invalid_userdata_no_user(self):
        fail = False
        try:
            userdata_invalid = smartlock.models.UserData.objects.create(user=None)
        except utils.IntegrityError:
            fail = True
        self.assertEquals(fail, True)

    def test_invalid_userdata_same_user(self):
        validUser = User.objects.get(id=1)
        fail = False
        try:
            userdata_invalid = smartlock.models.UserData.objects.create(user=validUser)
            userdata_invalid = smartlock.models.UserData.objects.create(user=validUser)
        except utils.IntegrityError:
            fail = True
        self.assertEquals(fail, True)

    def test_invalid_userdata_same_rfid(self):
        validUser = User.objects.get(id=1)
        validUser2 = User.objects.get(id=2)
        fail = False
        try:
            userdata_invalid = smartlock.models.UserData.objects.create(user=validUser, rfid="1234")
            userdata_invalid = smartlock.models.UserData.objects.create(user=validUser2, rfid='1234')
        except utils.IntegrityError:
            fail = True
        self.assertEquals(fail, True)

    def test_huge_rfid(self):
        rfid = ''.join(random.choices(string.ascii_lowercase + string.digits, k=500))
        validUser = User.objects.get(id=1)
        fail = False
        try:
            userdata_invalid = smartlock.models.UserData.objects.create(user=validUser, rfid=rfid)
            userdata_invalid.full_clean()
        except ValidationError:
            fail = True
        self.assertEquals(fail, True)

class UserDataGroupTester(TestCase):

    def setUp(self):
        User.objects.create_user(username='valid')
        User.objects.create_user(username='valid2')
        smartlock.models.UserDataGroup.objects.create(name="valid")

    def test_valid_userdatagroup(self):
        usergroup = smartlock.models.UserDataGroup.objects.get(id=1)
        validUser = User.objects.get(id=1)
        validUser2 = User.objects.get(id=2)
        validUserData = smartlock.models.UserData.objects.create(user=validUser)
        validUserData2 = smartlock.models.UserData.objects.create(user=validUser2)

        expected_userdatagroup_name = f'{usergroup.name}'
        self.assertEquals(expected_userdatagroup_name, 'valid')

        usergroup.grup.add(validUserData)
        usergroup.grup.add(validUserData2)

        expected_usergroup_username = usergroup.grup.get(id=1).user.username
        expected_usergroup_username2 = usergroup.grup.get(id=2).user.username
        self.assertEquals(expected_usergroup_username, 'valid')
        self.assertEquals(expected_usergroup_username2, 'valid2')

    def test_usergroup_same_name(self):
        fail = False
        try:
            usergroup_invalid = smartlock.models.UserDataGroup.objects.create(name="valid")
        except utils.IntegrityError:
            fail = True
        self.assertEquals(fail, True)

    def test_huge_name(self):
        name = ''.join(random.choices(string.ascii_lowercase + string.digits, k=151))
        fail = False
        try:
            usergroup_invalid = smartlock.models.UserDataGroup.objects.create(name=name)
            usergroup_invalid.full_clean()
        except ValidationError:
            fail = True
        self.assertEquals(fail, True)

    
class LockTester(TestCase):

    def setUp(self):
        tmzn = smartlock.models.TimeZone.objects.create(name='America/Sao_Paulo')
        smartlock.models.Lock.objects.create(name='test1', tmzn=tmzn)
        smartlock.models.Lock.objects.create(name='test2', tmzn=tmzn)

    def test_valid_lock(self):
        lock_instance = smartlock.models.Lock.objects.get(id=1)
        expected_lock_name = f'{lock_instance.name}'
        self.assertEquals(expected_lock_name, 'test1')
        lock_instance = smartlock.models.Lock.objects.get(id=2)
        expected_lock_name = f'{lock_instance.name}'
        self.assertEquals(expected_lock_name, 'test2')
        expected_tmzn = f'{lock_instance.tmzn}'
        self.assertEquals(expected_tmzn, 'America/Sao_Paulo')


    def test_invalid_lock_same_name(self):
        fail = False
        try:
            lock_invalid = smartlock.models.Lock.objects.create(name="invalid")
            lock_invalid = smartlock.models.Lock.objects.create(name="invalid")
        except utils.IntegrityError:
            fail = True
        self.assertEquals(fail, True)

    def test_invalid_lock_same_ruid(self):
        fail = False
        try:
            lock_invalid0 = smartlock.models.Lock.objects.create(name="invalid0")
            lock_invalid1 = smartlock.models.Lock.objects.create(name="invalid1", ruid=lock_invalid0.ruid)
        except utils.IntegrityError:
            fail = True
        self.assertEquals(fail, True)

    def test_invalid_lock_no_name(self):
        tmzn = smartlock.models.TimeZone.objects.get(id=1)
        fail = False
        try:
            lock_invalid = smartlock.models.Lock.objects.create(name=None, tmzn=tmzn)
        except utils.IntegrityError:
            fail = True
        self.assertEquals(fail, True)

    def test_invalid_lock_no_tmzn(self):
        fail = False
        try:
            lock_invalid = smartlock.models.Lock.objects.create(name='Any')
        except utils.IntegrityError:
            fail = True
        self.assertEquals(fail, True)

class LockGroupTester(TestCase):

    def setUp(self):
        validUser = User.objects.create_user(username='valid')
        smartlock.models.UserData.objects.create(user=validUser, rfid='e9eb9e6d')
        tmzn = smartlock.models.TimeZone.objects.create(name='America/Sao_Paulo')
        smartlock.models.Lock.objects.create(name='doorValid', tmzn=tmzn)
        smartlock.models.Lock.objects.create(name='doorValid2', tmzn=tmzn)
        smartlock.models.LockGroup.objects.create(name='doorGroup')

    def test_valid_lockgroup(self):
        validUser = User.objects.get(id=1)
        validUserData = smartlock.models.UserData.objects.get(id=1)
        validLock = smartlock.models.Lock.objects.get(id=1)
        validLock2 = smartlock.models.Lock.objects.get(id=2)
        lockgroup = smartlock.models.LockGroup.objects.get(id=1)

        expected_lockgroup_name = f'{lockgroup.name}'
        self.assertEquals(expected_lockgroup_name, 'doorGroup')

        lockgroup.grup.add(validLock)
        lockgroup.grup.add(validLock2)

        expected_lockgroup_name = lockgroup.grup.get(id=1).name
        expected_lockgroup_name2 = lockgroup.grup.get(id=2).name
        self.assertEquals(expected_lockgroup_name, 'doorValid')
        self.assertEquals(expected_lockgroup_name2, 'doorValid2')

    def test_lockgroup_same_name(self):
        fail = False
        try:
            lockgroup_invalid = smartlock.models.LockGroup.objects.create(name="doorGroup")
        except utils.IntegrityError:
            fail = True
        self.assertEquals(fail, True)

    def test_huge_name(self):
        name = ''.join(random.choices(string.ascii_lowercase + string.digits, k=151))
        fail = False
        try:
            lockgroup_invalid = smartlock.models.LockGroup.objects.create(name=name)
            lockgroup_invalid.full_clean()
        except ValidationError:
            fail = True
        self.assertEquals(fail, True)


class ScheduleTester(TestCase):

    def setUp(self):
        usergroup = smartlock.models.UserDataGroup.objects.create(name="usergroup")
        validUser = User.objects.create_user(username='valid')
        validUser2 = User.objects.create_user(username='valid2')
        validUserData = smartlock.models.UserData.objects.create(user=validUser)
        validUserData2 = smartlock.models.UserData.objects.create(user=validUser2)
        usergroup.grup.add(validUserData)
        usergroup.grup.add(validUserData2)

        tmzn = smartlock.models.TimeZone.objects.create(name='America/Sao_Paulo')
        validLock = smartlock.models.Lock.objects.create(name='doorValid', tmzn=tmzn)
        validLock2 = smartlock.models.Lock.objects.create(name='doorValid2', tmzn=tmzn)
        lockgroup = smartlock.models.LockGroup.objects.create(name='doorGroup')
        lockgroup.grup.add(validLock)
        lockgroup.grup.add(validLock2)

    def test_unique_values_userData_usergroup(self):
        validUserData = smartlock.models.UserData.objects.get(id=1)
        usergroup = smartlock.models.UserDataGroup.objects.get(id=1)
        fail = False
        try:
            schedule = smartlock.models.Schedule.objects.create(userdata=validUserData, userdatagrup=usergroup, dt_strt='2011-05-06', dt_stop='2012-08-09', tues=True)
            schedule.clean()
        except ValidationError:
            fail = True
        self.assertEquals(fail, True)

    def test_unique_values_lockData_lockgroup(self):
        validLock = smartlock.models.Lock.objects.get(id=1)
        lockgroup = smartlock.models.LockGroup.objects.get(id=1)
        fail = False
        try:
            schedule = smartlock.models.Schedule.objects.create(lock=validLock, lockgrup=lockgroup, dt_strt='2011-05-06', dt_stop='2012-08-09', tues=True)
            schedule.clean()
        except ValidationError:
            fail = True
        self.assertEquals(fail, True)

    def test_valid_schedule_userdata_lock(self):
        validUserData = smartlock.models.UserData.objects.get(id=1)
        validLock = smartlock.models.Lock.objects.get(id=1)

        schedule = smartlock.models.Schedule.objects.create(userdata=validUserData, lock=validLock, dt_strt='2011-05-06', dt_stop='2012-08-09', tues=True)
        expected_userdata_username = validUserData.user.username
        expected_lock_name = validLock.name
        self.assertEquals(expected_userdata_username, 'valid')
        self.assertEquals(expected_lock_name, 'doorValid')
    
    def test_valid_schedule_userdata_lockgroup(self):
        validUserData = smartlock.models.UserData.objects.get(id=1)
        lockgroup = smartlock.models.LockGroup.objects.get(id=1)

        schedule = smartlock.models.Schedule.objects.create(userdata=validUserData, lockgrup=lockgroup, dt_strt='2011-05-06', dt_stop='2012-08-09', tues=True)
        expected_userdata_username = validUserData.user.username
        expected_lockgrup_name = lockgroup.name
        self.assertEquals(expected_userdata_username, 'valid')
        self.assertEquals(expected_lockgrup_name, 'doorGroup')
    
    def test_valid_schedule_userdatagrup_lock(self):
        usergroup = smartlock.models.UserDataGroup.objects.get(id=1)
        validLock = smartlock.models.Lock.objects.get(id=1)

        schedule = smartlock.models.Schedule.objects.create(userdatagrup=usergroup, lock=validLock, dt_strt='2011-05-06', dt_stop='2012-08-09', tues=True)
        expected_usergrup_username = usergroup.name
        expected_lock_name = validLock.name
        self.assertEquals(expected_usergrup_username, 'usergroup')
        self.assertEquals(expected_lock_name, 'doorValid')
    
    def test_valid_schedule_userdatagrup_lockgrup(self):
        usergroup = smartlock.models.UserDataGroup.objects.get(id=1)
        lockgroup = smartlock.models.LockGroup.objects.get(id=1)

        schedule = smartlock.models.Schedule.objects.create(userdatagrup=usergroup, lockgrup=lockgroup, dt_strt='2011-05-06', dt_stop='2012-08-09', tues=True)
        expected_usergrup_username = usergroup.name
        expected_lockgrup_name = lockgroup.name
        self.assertEquals(expected_usergrup_username, 'usergroup')
        self.assertEquals(expected_lockgrup_name, 'doorGroup')

    def test_same_schedule_userdata_lock(self):
        validUserData = smartlock.models.UserData.objects.get(id=1)
        validLock = smartlock.models.Lock.objects.get(id=1)
        fail = False
        try:
            schedule = smartlock.models.Schedule.objects.create(userdata=validUserData, lock=validLock, dt_strt='2011-05-06', dt_stop='2012-08-09', tues=True)
            schedule2 = smartlock.models.Schedule.objects.create(userdata=validUserData, lock=validLock, dt_strt='2011-05-07', dt_stop='2012-08-11', tues=True)
        except utils.IntegrityError:
            fail = True
        self.assertEquals(fail, True)
    
    def test_same_schedule_userdata_lockgroup(self):
        validUserData = smartlock.models.UserData.objects.get(id=1)
        lockgroup = smartlock.models.LockGroup.objects.get(id=1)
        fail = False
        try:
            schedule = smartlock.models.Schedule.objects.create(userdata=validUserData, lockgrup=lockgroup, dt_strt='2011-05-06', dt_stop='2012-08-09', tues=True)
            schedule2 = smartlock.models.Schedule.objects.create(userdata=validUserData, lockgrup=lockgroup, dt_strt='2011-05-07', dt_stop='2012-08-11', tues=True)
        except utils.IntegrityError:
            fail = True
        self.assertEquals(fail, True)
    
    def test_same_schedule_userdatagrup_lock(self):
        usergroup = smartlock.models.UserDataGroup.objects.get(id=1)
        validLock = smartlock.models.Lock.objects.get(id=1)
        fail = False
        try:
            schedule = smartlock.models.Schedule.objects.create(userdatagrup=usergroup, lock=validLock, dt_strt='2011-05-06', dt_stop='2012-08-09', tues=True)
            schedule2 = smartlock.models.Schedule.objects.create(userdatagrup=usergroup, lock=validLock, dt_strt='2011-05-07', dt_stop='2012-08-11', tues=True)
        except utils.IntegrityError:
            fail = True
        self.assertEquals(fail, True)

    def test_same_schedule_userdatagrup_lockgroup(self):
        usergroup = smartlock.models.UserDataGroup.objects.get(id=1)
        lockgroup = smartlock.models.LockGroup.objects.get(id=1)
        fail = False
        try:
            schedule = smartlock.models.Schedule.objects.create(userdatagrup=usergroup, lockgrup=lockgroup, dt_strt='2011-05-06', dt_stop='2012-08-09', tues=True)
            schedule2 = smartlock.models.Schedule.objects.create(userdatagrup=usergroup, lockgrup=lockgroup, dt_strt='2011-05-07', dt_stop='2012-08-11', tues=True)
        except utils.IntegrityError:
            fail = True
        self.assertEquals(fail, True)

    def test_schedule_without_start(self):
        usergroup = smartlock.models.UserDataGroup.objects.get(id=1)
        lockgroup = smartlock.models.LockGroup.objects.get(id=1)
        fail = False
        try:
            schedule = smartlock.models.Schedule.objects.create(userdatagrup=usergroup, lockgrup=lockgroup, dt_stop='2012-08-09', tues=True)
        except utils.IntegrityError:
            fail = True
        self.assertEquals(fail, True)

    def test_schedule_without_end(self):
        usergroup = smartlock.models.UserDataGroup.objects.get(id=1)
        lockgroup = smartlock.models.LockGroup.objects.get(id=1)
        fail = False
        try:
            schedule = smartlock.models.Schedule.objects.create(userdatagrup=usergroup, lockgrup=lockgroup, dt_strt='2012-08-09', tues=True)
        except utils.IntegrityError:
            fail = True
        self.assertEquals(fail, True)

    def test_schedule_begin_after_end(self):
        validLock = smartlock.models.Lock.objects.get(id=1)
        lockgroup = smartlock.models.LockGroup.objects.get(id=1)
        fail = False
        try:
            schedule = smartlock.models.Schedule.objects.create(lock=validLock, lockgrup=lockgroup, dt_strt='2011-05-06', dt_stop='2010-08-09', tues=True)
            schedule.clean()
        except ValidationError:
            fail = True
        self.assertEquals(fail, True)

    def test_schedule_no_weekday(self):
        validLock = smartlock.models.Lock.objects.get(id=1)
        lockgroup = smartlock.models.LockGroup.objects.get(id=1)
        fail = False
        try:
            schedule = smartlock.models.Schedule.objects.create(lock=validLock, lockgrup=lockgroup, dt_strt='2011-05-06', dt_stop='2010-08-09')
            schedule.clean()
        except ValidationError:
            fail = True
        self.assertEquals(fail, True)

class UnlockAttemptLogTester(TestCase):

    def setUp(self):
        tmzn = smartlock.models.TimeZone.objects.create(name='America/Sao_Paulo')
        validLock = smartlock.models.Lock.objects.create(name='doorValid', tmzn=tmzn)
        validUser = User.objects.create_user(username='valid')
        validUserData = smartlock.models.UserData.objects.create(user=validUser)
    
    def test_valid_log(self):
        ruid = crypto.get_random_string(32)
        rfid = "123"
        lock = smartlock.models.Lock.objects.get(id=1)
        userdata = smartlock.models.UserData.objects.get(id=1)
        log = smartlock.models.UnlockAttemptLog.objects.create(ruid=ruid, rfid=rfid, lock=lock, userdata=userdata, succ=True)#Time is automatically generated
        
        expected_ruid = log.ruid
        expected_rfid = log.rfid
        expected_lock_name = log.lock.name
        expected_username = log.userdata.user.username
        self.assertEquals(expected_ruid, ruid)
        self.assertEquals(expected_rfid, '123')
        self.assertEquals(expected_lock_name, 'doorValid')
        self.assertEquals(expected_username, 'valid')
    
    def test_valid_log_false_succ(self):
        ruid = crypto.get_random_string(32)
        rfid = "123"
        lock = smartlock.models.Lock.objects.get(id=1)
        userdata = smartlock.models.UserData.objects.get(id=1)
        log = smartlock.models.UnlockAttemptLog.objects.create(ruid=ruid, rfid=rfid, lock=lock, userdata=userdata, succ=False)#Time is automatically generated
        
        expected_ruid = log.ruid
        expected_rfid = log.rfid
        expected_lock_name = log.lock.name
        expected_username = log.userdata.user.username
        self.assertEquals(expected_ruid, ruid)
        self.assertEquals(expected_rfid, '123')
        self.assertEquals(expected_lock_name, 'doorValid')
        self.assertEquals(expected_username, 'valid')

    def test_huge_ruid(self):
        ruid = crypto.get_random_string(257)
        fail = False
        try:
            log = smartlock.models.UnlockAttemptLog.objects.create(ruid=ruid, succ=True)
            log.full_clean()
        except ValidationError:
            fail = True
        self.assertEquals(fail, True)
    
    def test_huge_rfid(self):
        rfid = ''.join(random.choices(string.ascii_lowercase + string.digits, k=257))
        fail = False
        try:
            log = smartlock.models.UnlockAttemptLog.objects.create(rfid=rfid, succ=True)
            log.full_clean()
        except ValidationError:
            fail = True
        self.assertEquals(fail, True)

    def test_log_without_succ_value(self):
        fail = False
        try:
            log = smartlock.models.UnlockAttemptLog.objects.create()
        except utils.IntegrityError:
            fail = True
        self.assertEquals(fail, True)
        