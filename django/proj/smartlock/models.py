from django.db import models
from django.db.models import Q, functions
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import crypto, timezone
import pytz

# from collections import OrderedDict


class TimeZone(models.Model):
    name = models.CharField(max_length=64, null=False, blank=False, unique=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def __repl__(self):
        return str(self)


class UserData(models.Model):
    user = models.OneToOneField(to=settings.AUTH_USER_MODEL,
                                on_delete=models.CASCADE,
                                null=False, blank=False, unique=True)
    rfid = models.CharField(max_length=256, default=None, null=True, blank=True, unique=True)
    admin = models.BooleanField(default=False)
    manager = models.BooleanField(default=False)

    class Meta:
        ordering = [functions.Lower('user__username')]

    def __str__(self):
        # st_rtrn = self.user.username
        # if self.admin and self.manager:
        #     st_rtrn += ' (admin, manager)'
        # elif self.admin:
        #     st_rtrn += ' (admin)'
        # elif self.manager:
        #     st_rtrn += ' (manager)'
        # else:
        #     st_rtrn += ' (standard)'
        return self.user.username

    def __repr__(self):
        return str(self)


class UserDataGroup(models.Model):
    name = models.CharField(max_length=150, null=False, blank=False, unique=True)
    grup = models.ManyToManyField(UserData, verbose_name='group')

    class Meta:
        ordering = [functions.Lower('name')]

    def __str__(self):
        # return '{:s}: ({:s})'.format(self.name, ', '.join([item.user.username
        #                                                    for item in self.grup.all()]))
        return self.name


lngt_ruid = 32
def get_ruid():
    return crypto.get_random_string(lngt_ruid)

class Lock(models.Model):
    name = models.CharField(max_length=150, null=False, blank=False, unique=True)
    tmzn = models.ForeignKey(to=TimeZone,
                             on_delete=models.PROTECT, verbose_name='timezone',
                             null=False, blank=False)
    ruid = models.CharField('RUID', max_length=32, help_text='Random unique identifier',
                            null=False, blank=False, unique=True,
                            default=get_ruid)

    class Meta:
        ordering = [functions.Lower('name')]

    def __str__(self):
        # return '{:s} ({:s})'.format(self.name, self.ruid)
        return self.name

    def __repr__(self):
        return str(self)

    def now(self):
        return timezone.now().astimezone(pytz.timezone(self.tmzn.name))


class LockGroup(models.Model):
    name = models.CharField(max_length=150, null=False, blank=False, unique=True)
    grup = models.ManyToManyField(Lock, verbose_name='group')

    class Meta:
        ordering = [functions.Lower('name')]

    def __str__(self):
        # return self.name + ': (' + ', '.join([item.name for item in self.grup.all()]) + ')'
        return self.name

    def __repr__(self):
        return str(self)


class UnlockAttemptLog(models.Model):
    time = models.DateTimeField(auto_now_add=True)
    ruid = models.CharField(max_length=256, null=True, blank=True)
    rfid = models.CharField(max_length=256, null=True, blank=True)
    lock = models.ForeignKey(to=Lock,
                             on_delete=models.PROTECT,
                             null=True, blank=True)
    userdata = models.ForeignKey(to=UserData,
                                 on_delete=models.PROTECT,
                                 null=True, blank=True)
    succ = models.BooleanField()

    class Meta:
        ordering = ('-time',)

    def __str__(self):
        if self.lock is None:
            st_lock = 'None'
        else:
            st_lock = self.lock.name
        if self.userdata is None:
            st_user = 'None'
        else:
            st_user = self.userdata.user.username
        return ('{:s}(time: {}, ruid: "{:s}", rfid: "{:s}", ' +
                'lock: "{:s}", user: "{:s}", succ: {})').format(
                    type(self).__name__, self.time, self.ruid, self.rfid,
                    st_lock, st_user, self.succ)


class Schedule(models.Model):
    userdata = models.ForeignKey(to=UserData,
                             on_delete=models.PROTECT,
                             null=True, blank=True)
    userdatagrup = models.ForeignKey(to=UserDataGroup,
                                 on_delete=models.PROTECT,
                                 null=True, blank=True,
                                 verbose_name='user data group')
    lock = models.ForeignKey(to=Lock,
                             on_delete=models.PROTECT,
                             null=True, blank=True)
    lockgrup = models.ForeignKey(to=LockGroup,
                                 on_delete=models.PROTECT,
                                 null=True, blank=True,
                                 verbose_name='lock group')
    dt_strt = models.DateField('starting date', null=False, blank=False)
    dt_stop = models.DateField('ending date', null=False, blank=False)
    tm_strt = models.TimeField('starting time', null=True, blank=True)
    tm_stop = models.TimeField('ending time', null=True, blank=True)
    mond = models.BooleanField('monday', default=False)
    tues = models.BooleanField('tuesday', default=False)
    wedn = models.BooleanField('wednesday', default=False)
    thur = models.BooleanField('thursday', default=False)
    frid = models.BooleanField('friday', default=False)
    satu = models.BooleanField('saturday', default=False)
    sund = models.BooleanField('sunday', default=False)

    ls_week_keyw = ['mond', 'tues', 'wedn', 'thur', 'frid', 'satu', 'sund']

    def __str__(self):
        if self.userdata is None and self.userdatagrup is None:
            st_user = 'User: any'
        elif self.userdata is not None:
            st_user = 'User: {:s}'.format(self.userdata.user.username)
        else:
            st_user = 'User group: {:s}'.format(str(self.userdatagrup))
        if self.lock is not None:
            st_lock = 'Lock: {:s}'.format(self.lock.name)
        else:
            st_lock = 'Lock group: {:s}'.format(str(self.lockgrup))
        st_date = '({:s} - {:s})'.format(self.dt_strt.strftime('%Y-%m-%d') if self.dt_strt else '',
                                         self.dt_stop.strftime('%Y-%m-%d') if self.dt_stop else '')
        st_time = '(all day)'
        if self.tm_strt is not None or self.tm_stop is not None:
            st_time = '({:s} - {:s})'.format(str(self.tm_strt),
                                               str(self.tm_stop))
        ls_week = list()
        for keyw in self.ls_week_keyw:
            if getattr(self, self._meta.get_field(keyw).name):
                ls_week.append(self._meta.get_field(keyw).verbose_name)
        st_week = '(no weekdays)'
        if 0 < len(ls_week):
            st_week = '({:s})'.format(', '.join(ls_week))
        return '{}; {}; {}; {}; {}'.format(st_user, st_lock, st_date, st_time, st_week)

    def __repr__(self):
        return str(self)

    def clean(self):
        if (#(self.userdata is None and self.userdatagrup is None) or
            (self.userdata is not None and self.userdatagrup is not None)):
            raise ValidationError("The field 'user' and 'user group' may not both be non empty.")
        if ((self.lock is None and self.lockgrup is None)
            or
            (self.lock is not None and self.lockgrup is not None)):
            raise ValidationError("Either the field 'lock' or 'lock group' must be non empty.")
        if self.dt_strt is None or self.dt_stop is None or self.dt_stop < self.dt_strt:
            raise ValidationError("The ending date must be the same or after the starting date.")
        if any([getattr(self, keyw) for keyw in self.ls_week_keyw]) is False:
            raise ValidationError("At least a weekday must be scheduled.")

    @property
    def userdatacomp(self):
        if self.userdata is None and self.userdatagrup is None:
            return 'Any user'
        elif self.userdatagrup is None:
            return dict(pk=self.userdata.pk, name='single: {:s}'.format(self.userdata.user.username), grup=False, comp='userdata')
        else:
            return dict(pk=self.userdatagrup.pk, name='group: {:s}'.format(self.userdatagrup.name), grup=True, comp='userdata')

    @property
    def lockcomp(self):
        if self.lock is None and self.lockgrup is None:
            return dict(pk=None, name=None, grup=False, comp='lock')
        elif self.lockgrup is None:
            return dict(pk=self.lock.pk, name='single: {:s}'.format(self.lock.name), grup=False, comp='lock')
        else:
            return dict(pk=self.lockgrup.pk, name='group: {:s}'.format(self.lockgrup.name), grup=True, comp='lock')

    @classmethod
    def get_schedule_fields(clss, *args, **kwargs):
        ls_name = [field.name for field in clss._meta.fields
                   if field.name not in ('id', 'userdata', 'userdatagrup', 'lock', 'lockgrup')]
        ls_verb = [clss._meta.get_field(name).verbose_name for name in ls_name]

        ls_name = ['userdatacomp', 'lockcomp'] + ls_name
        ls_verb = ['user', 'lock'] + ls_verb

        ls_entr = list()
        for object in clss.objects.filter(*args, **kwargs):
            ls_entr.append([getattr(object, name) for name in ls_name])
        return dict(names=ls_name, verbose_names=ls_verb, entries=ls_entr)

    class Meta:
        unique_together = (('userdata', 'lock'),
                           ('userdata', 'lockgrup'),
                           ('userdatagrup', 'lock'),
                           ('userdatagrup', 'lockgrup'),)

    @classmethod
    def validate_lock_rfid_pair(clss, st_ruid, st_rfid):
        lock = Lock.objects.get(ruid=st_ruid)
        now = lock.now()
        date, time = now.date(), now.time()

        if st_rfid is None:
            crit_user = Q(userdata=None, userdatagrup__grup=None)
        else:
            crit_user = Q(userdata__rfid=st_rfid) | Q(userdatagrup__grup__rfid=st_rfid)
        crit_lock = Q(lock=lock) | Q(lockgrup__grup=lock)
        crit_date = Q(dt_strt__lte=date, dt_stop__gte=date)
        crit_time = Q(Q(tm_strt=None) | Q(tm_strt__lte=time), Q(tm_stop=None) | Q(tm_stop__gte=time))
        dc_crit_week = {'{}'.format(timezone.now().strftime('%A').lower()[:4]): True}

        qury = Schedule.objects.filter(crit_user, crit_lock, crit_date, crit_time, **dc_crit_week)
        return 0 < len(qury)
