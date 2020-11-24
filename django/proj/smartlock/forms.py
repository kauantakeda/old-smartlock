from django.contrib import auth

from django.conf import settings

from django import forms
from django.forms import widgets as forms_widgets
from django.contrib.admin import widgets as admin_widgets
from . import models
from .models import Lock, Schedule


class UserUpdateForm(forms.ModelForm):
    password = forms.CharField(required=False, widget=forms.PasswordInput)

    class Meta:
        model = auth.get_user_model()
        fields = ('username', 'password')

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data['password']
        if password:
            user.set_password(password)
        if commit:
            user.save()
        return user


class UserDataGroupForm(forms.ModelForm):
    class Media:
        css = {
             'all': ('django/proj/static/css/styles.css',)
        }
    class Meta:
        model = models.UserDataGroup
        exclude = tuple()
        # widgets = dict(grup=forms_widgets.CheckboxSelectMultiple)
        widgets = dict(grup=admin_widgets.FilteredSelectMultiple('', is_stacked=False))


class LockForm(forms.ModelForm):
    class Meta:
        model = Lock
        exclude = tuple()
        help_texts = dict(ruid='Random unique identifier code')
    ruid = forms.CharField(widget=forms.TextInput(attrs=dict(readonly='readonly')),
                           label=Lock._meta.get_field('ruid').verbose_name)


class LockGroupForm(forms.ModelForm):
    class Meta:
        model = models.LockGroup
        exclude = tuple()
        # widgets = dict(grup=forms_widgets.CheckboxSelectMultiple)
        widgets = dict(grup=admin_widgets.FilteredSelectMultiple('', is_stacked=False))


class ScheduleForm(forms.ModelForm):
    userdatacomposite = forms.ChoiceField(label='User', required=False)
    lockcomposite = forms.ChoiceField(label='Lock', required=False)

    class Meta:
        model = Schedule
        exclude = tuple()
        widgets = dict(userdata=forms_widgets.HiddenInput,
                       userdatagrup=forms_widgets.HiddenInput,
                       lock=forms_widgets.HiddenInput,
                       lockgrup=forms_widgets.HiddenInput,
                       dt_strt=admin_widgets.AdminDateWidget,
                       dt_stop=admin_widgets.AdminDateWidget,
                       tm_strt=admin_widgets.AdminTimeWidget,
                       tm_stop=admin_widgets.AdminTimeWidget)
        fields = ['userdatacomposite', 'lockcomposite',
                  'userdata', 'userdatagrup', 'lock', 'lockgrup',
                  'dt_strt', 'dt_stop', 'tm_strt', 'tm_stop',
                  'mond', 'tues', 'wedn', 'thur', 'frid', 'satu', 'sund']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['tm_strt'].widget.attrs['placeholder'] = '00:00:00'
        self.fields['tm_stop'].widget.attrs['placeholder'] = '23:59:59.9'

        ls_userdata = [('s{:d}'.format(object.pk), 'single: ' + object.user.username) for object in models.UserData.objects.all()]
        ls_userdatagrup = [('g{:d}'.format(object.pk), 'group: ' + object.name) for object in models.UserDataGroup.objects.all()]
        tp_userdatacomposite = (('', [('', '---------')]),
                                ('UserData', ls_userdata),
                                ('UserDataGroup', ls_userdatagrup))
        self.fields['userdatacomposite'].choices = tp_userdatacomposite
        if self.instance and self.instance.userdata:
            self.initial['userdatacomposite'] = 's{:d}'.format(self.instance.userdata.pk)
        elif self.instance and self.instance.userdatagrup:
            self.initial['userdatacomposite'] = 'g{:d}'.format(self.instance.userdatagrup.pk)
        else:
            self.initial['userdatacomposite'] = ''

        ls_lock = [('s{:d}'.format(object.pk), 'single: ' + object.name) for object in models.Lock.objects.all()]
        ls_lockgrup = [('g{:d}'.format(object.pk), 'group: ' + object.name) for object in models.LockGroup.objects.all()]
        tp_lockcomposite = (('', [('', '---------')]),
                            ('Lock', ls_lock),
                            ('LockGroup', ls_lockgrup))
        self.fields['lockcomposite'].choices = tp_lockcomposite
        if self.instance and self.instance.lock:
            self.initial['lockcomposite'] = 's{:d}'.format(self.instance.lock.pk)
        elif self.instance and self.instance.lockgrup:
            self.initial['lockcomposite'] = 'g{:d}'.format(self.instance.lockgrup.pk)
        else:
            self.initial['lockcomposite'] = ''

        # self.fields['lock'].hidden_widget = forms_widgets.HiddenInput()
    # def save(self, commit=True):
    #     schd = super().save(commit=False)
    #     print(schd)
    #     # password = self.cleaned_data['password']
    #     # if password:
    #     #     user.set_password(password)
    #     # if commit:
    #     #     user.save()
    #     return schd

    # def is_valid(self):
    #     # for st_field in ['userdata', 'lock']:
    #     #     st_comp = st_field + 'composite'
    #     #     for keyw in self.data.keys():
    #     #         if keyw.endswith(st_comp) and self.data[keyw] != '':
    #     #             print(keyw, self.data[keyw])
    #     #             if self.data[keyw][0] == 's':
    #     #                 st_parm = keyw[:-len(st_comp)] + st_field
    #     #             elif self.data[keyw][0] == 'g':
    #     #                 st_parm = keyw[:-len(st_comp)] + st_field + 'grup'
    #     #             else:
    #     #                 continue
    #     #             self.data[st_parm] = self.data[keyw][1:]
    #     #             print('→', st_parm, self.data[st_parm])


    #     # print('self.data:', self.data)
    #     # if self.cleaned_data['lockcomposite'][0] == 's':
    #     #     self.cleaned_data['lock'] = self.cleaned_data['lockcomposite'][1:]
    #     # elif self.cleaned_data['lockcomposite'][0] == 'g':
    #     #     self.cleaned_data['lockgrup'] = self.cleaned_data['lockcomposite'][1:]
    #     # print('→ is_valid()', self.cleaned_data['lock'], self.cleaned_data['lockgrup'], self.cleaned_data['lockcomposite'])
    #     return super().is_valid()
