import sys

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views import View, generic
from django import http
from django import urls
from django.contrib import auth, messages
import django.forms
from django.db.models import ProtectedError, Q

from .models import UserData, UserDataGroup
from .models import Lock, LockGroup
from .models import Schedule
from .models import UnlockAttemptLog
from . import models, forms

@login_required
def account(request):
    context = {"account_page": "active"}
    return render(request, 'smartlock/account.html', context)


class HomeView(generic.base.TemplateView):
    template_name = 'smartlock/home.html'

    def get(self, request, *args, **kwargs):
        self.user_id = int(request.user.id)
        resp = super().get(request, *args, **kwargs)
        return resp

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(extra_schedules=models.Schedule.get_schedule_fields(
            Q(userdata__user__id=self.user_id) | Q(userdatagrup__grup__user__id=self.user_id)))
        return context


class UserAndUserDataCreateView(generic.edit.CreateView):
    model = auth.get_user_model()
    fields = ['username', 'password']
    template_name = 'smartlock/userdata_form.html'
    success_url = urls.reverse_lazy('smartlock:users')
    form_userdata = django.forms.modelform_factory(UserData,
                                                   fields=('rfid', 'admin', 'manager'))
    extra_context = dict(users_page='active',
                         form_userdata=form_userdata)

    def get_form(self_class):
        form = super().get_form()
        form.fields['password'].widget = django.forms.PasswordInput()
        return form

    def post(self, request, *args, **kwargs):
        form_user = self.get_form().__class__(request.POST)
        form_userdata = self.form_userdata(request.POST)
        if form_user.is_valid() and form_userdata.is_valid():
            user = form_user.save(commit=False)
            user.set_password(user.password)
            userdata = form_userdata.save(commit=False)
            user.save()
            userdata.user = user
            userdata.save()
            return http.HttpResponseRedirect(redirect_to=self.__class__.success_url)
        else:
            return self.get(request)


class UserAndUserDataUpdateView(generic.edit.UpdateView):
    model = UserData
    template_name = 'smartlock/userdata_detail.html'
    success_url = urls.reverse_lazy('smartlock:users')
    fields = ('rfid', 'admin', 'manager')
    form_user = forms.UserUpdateForm
    formset_class = django.forms.inlineformset_factory(parent_model=UserData,
                                                       model=Schedule,
                                                       form=forms.ScheduleForm,
                                                       exclude=tuple(),
                                                       extra=1)
    extra_context = dict(users_page='active',)

    def get_user_object(self):
        return auth.get_user_model().objects.get(pk=self.object.user.pk)

    def get_context_data(self, **kwargs):
        self.object = self.get_object()
        context = super().get_context_data(**kwargs)
        if 'form' not in context.keys():
            context['form'] = self.get_form_class()(instance=self.get_object())
        if 'form_user' not in context.keys():
            context['form_user'] = self.form_user(instance=self.get_user_object())
        if 'formset' not in context.keys():
            context['formset'] = self.formset_class(instance=self.get_object())
        context['extra_schedules'] = models.Schedule.get_schedule_fields(userdatagrup__grup=self.object)
        return context

    def post(self, request, *args, **kwargs):
        if 'username' in request.POST.keys():
            self.object = self.get_object()
            form_user = self.form_user(request.POST, instance=self.get_user_object())
            form = self.get_form_class()(request.POST, instance=self.object)
            if form.is_valid() and form_user.is_valid():
                userdata = form.save()
                user = form_user.save()
                return http.HttpResponseRedirect(redirect_to=self.success_url)
            else:
                return self.get(request)
        else:
            request.POST = request.POST.copy()
            for keyw in request.POST.keys():
                if keyw.endswith('composite') and request.POST[keyw] != '':
                    if request.POST[keyw][0] == 's':
                        request.POST[keyw[:-len('composite')]] = request.POST[keyw][1:]
                        request.POST[keyw[:-len('composite')] + 'grup'] = ''
                    elif request.POST[keyw][0] == 'g':
                        request.POST[keyw[:-len('composite')]] = ''
                        request.POST[keyw[:-len('composite')] + 'grup'] = request.POST[keyw][1:]
            formset = self.formset_class(request.POST, request.FILES, instance=self.get_object())
            if formset.is_valid():
                formset.save()
                return http.HttpResponseRedirect(self.get_success_url_formset())
            else:
                context = self.get_context_data(formset=formset)
                context.update(formset=formset)
                context.update(form=self.get_form_class()(instance=self.get_object()))
                return self.render_to_response(context)

    def get_success_url(self):
        return urls.reverse_lazy('smartlock:users')

    def get_success_url_formset(self):
        return urls.reverse_lazy('smartlock:user', kwargs=dict(pk=self.get_object().pk))


class UserAndUserDataDeleteView(generic.edit.DeleteView):
    model = UserData
    template_name = 'smartlock/userdata_confirm_delete.html'
    success_url = urls.reverse_lazy('smartlock:users')
    extra_context = dict(users_page='active')

    def delete(self, request, *args, **kwargs):
        try:
            user = self.get_object().user
            self.get_object().delete()
            user.delete()
        except ProtectedError:
            messages.add_message(request, messages.ERROR,
                                 'Could not delete User and UserData "{:s}":'.format(self.get_object().username)
                                 + ' it is not allowed to delete user accounts that are listed in user groups'
                                 + ' or that have permissions attached.')
            return http.HttpResponseRedirect(urls.reverse_lazy('smartlock:del_userdata',
                                                               kwargs=dict(pk=self.get_object().pk)))
        return http.HttpResponseRedirect(self.success_url)


class UserDataGroupUpdateView(generic.edit.UpdateView):
    model = UserDataGroup
    # fields = ['name', 'grup']
    form_class = forms.UserDataGroupForm
    template_name = 'smartlock/userdatagroup_detail.html'
    formset_class = django.forms.inlineformset_factory(parent_model=UserDataGroup,
                                                       model=Schedule,
                                                       form=forms.ScheduleForm,
                                                       exclude=tuple(),
                                                       extra=1)
    extra_context = dict(user_groups_page='active')

    def get_context_data(self, **kwargs):
        self.object = self.get_object()
        context = super().get_context_data(**kwargs)
        if 'formset' not in context.keys():
            context['formset'] = self.formset_class(instance=self.get_object())
        context['extra_schedules'] = models.Schedule.get_schedule_fields(userdata__userdatagroup__pk=self.object.pk)
        return context

    def post(self, request, *args, **kwargs):
        if 'name' in request.POST.keys():
            return super().post(request, *args, **kwargs)
        else:
            request.POST = request.POST.copy()
            for keyw in request.POST.keys():
                if keyw.endswith('composite') and request.POST[keyw] != '':
                    if request.POST[keyw][0] == 's':
                        request.POST[keyw[:-len('composite')]] = request.POST[keyw][1:]
                        request.POST[keyw[:-len('composite')] + 'grup'] = ''
                    elif request.POST[keyw][0] == 'g':
                        request.POST[keyw[:-len('composite')]] = ''
                        request.POST[keyw[:-len('composite')] + 'grup'] = request.POST[keyw][1:]
            formset = self.formset_class(request.POST, request.FILES, instance=self.get_object())
            if formset.is_valid():
                formset.save()
                return http.HttpResponseRedirect(self.get_success_url_formset())
            else:
                context = self.get_context_data(formset=formset)
                context.update(formset=formset)
                context.update(form=self.get_form_class()(instance=self.get_object()))
                return self.render_to_response(context)

    def get_success_url(self):
        return urls.reverse_lazy('smartlock:user_groups')

    def get_success_url_formset(self):
        return urls.reverse_lazy('smartlock:user_group', kwargs=dict(pk=self.get_object().pk))


class LockUpdateView(generic.edit.UpdateView):
    model = Lock
    form_class = forms.LockForm
    template_name = 'smartlock/lock_detail.html'
    formset_class = django.forms.inlineformset_factory(parent_model=Lock,
                                                       model=Schedule,
                                                       form=forms.ScheduleForm,
                                                       exclude=tuple(),
                                                       extra=1)
    extra_context = dict(locks_page='active')

    def get_context_data(self, **kwargs):
        self.object = self.get_object()
        context = super().get_context_data(**kwargs)
        if 'formset' not in context.keys():
            context['formset'] = self.formset_class(instance=self.get_object())
        context['extra_schedules'] = models.Schedule.get_schedule_fields(lockgrup__grup=self.object)
        return context

    def post(self, request, *args, **kwargs):
        if 'tmzn' in request.POST.keys():
            return super().post(request, *args, **kwargs)
        else:
            request.POST = request.POST.copy()
            for keyw in request.POST.keys():
                if keyw.endswith('composite') and request.POST[keyw] != '':
                    if request.POST[keyw][0] == 's':
                        request.POST[keyw[:-len('composite')]] = request.POST[keyw][1:]
                        request.POST[keyw[:-len('composite')] + 'grup'] = ''
                    elif request.POST[keyw][0] == 'g':
                        request.POST[keyw[:-len('composite')]] = ''
                        request.POST[keyw[:-len('composite')] + 'grup'] = request.POST[keyw][1:]
            formset = self.formset_class(request.POST, request.FILES, instance=self.get_object())
            if formset.is_valid():
                formset.save()
                return http.HttpResponseRedirect(self.get_success_url_formset())
            else:
                context = self.get_context_data(formset=formset)
                context.update(formset=formset)
                context.update(form=self.get_form_class()(instance=self.get_object()))
                return self.render_to_response(context)

    def get_success_url(self):
        return urls.reverse_lazy('smartlock:locks')

    def get_success_url_formset(self):
        return urls.reverse_lazy('smartlock:lock', kwargs=dict(pk=self.get_object().pk))


class LockDeleteView(generic.edit.DeleteView):
    model = Lock
    success_url = urls.reverse_lazy('smartlock:locks')
    extra_context = dict(locks_page='active')

    def delete(self, request, *args, **kwargs):
        try:
            self.get_object().delete()
        except ProtectedError:
            messages.add_message(request, messages.ERROR,
                                 'Could not delete Lock "{:s}":'.format(self.get_object().name)
                                 + ' it is not allowed to delete Locks that are listed in Lock Groups'
                                 + ' or that have permissions attached.')
            return http.HttpResponseRedirect(urls.reverse_lazy('smartlock:del_lock',
                                                               kwargs=dict(pk=self.get_object().pk)))
        return http.HttpResponseRedirect(self.success_url)


class LockGroupUpdateView(generic.edit.UpdateView):
    model = LockGroup
    template_name = 'smartlock/lockgroup_detail.html'
    form_class = forms.LockGroupForm
    formset_class = django.forms.inlineformset_factory(parent_model=LockGroup,
                                                       model=Schedule,
                                                       form=forms.ScheduleForm,
                                                       exclude=tuple(),
                                                       extra=1)
    extra_context = dict(lock_groups_page='active')

    def get_context_data(self, **kwargs):
        self.object = self.get_object()
        context = super().get_context_data(**kwargs)
        if 'formset' not in context.keys():
            context['formset'] = self.formset_class(instance=self.get_object())
        context['extra_schedules'] = models.Schedule.get_schedule_fields(lock__lockgroup=self.object)
        return context

    def post(self, request, *args, **kwargs):
        if 'name' in request.POST.keys():
            return super().post(request, *args, **kwargs)
        else:
            request.POST = request.POST.copy()
            for keyw in request.POST.keys():
                if keyw.endswith('composite') and request.POST[keyw] != '':
                    if request.POST[keyw][0] == 's':
                        request.POST[keyw[:-len('composite')]] = request.POST[keyw][1:]
                        request.POST[keyw[:-len('composite')] + 'grup'] = ''
                    elif request.POST[keyw][0] == 'g':
                        request.POST[keyw[:-len('composite')]] = ''
                        request.POST[keyw[:-len('composite')] + 'grup'] = request.POST[keyw][1:]
            formset = self.formset_class(request.POST, request.FILES, instance=self.get_object())
            if formset.is_valid():
                formset.save()
                return http.HttpResponseRedirect(self.get_success_url_formset())
            else:
                context = self.get_context_data(formset=formset)
                context.update(formset=formset)
                context.update(form=self.get_form_class()(instance=self.get_object()))
                return self.render_to_response(context)

    def get_success_url(self):
        return urls.reverse_lazy('smartlock:lock_groups')

    def get_success_url_formset(self):
        return urls.reverse_lazy('smartlock:lock_group', kwargs=dict(pk=self.get_object().pk))


class LockGroupDeleteView(generic.edit.DeleteView):
    model = LockGroup
    success_url = urls.reverse_lazy('smartlock:lock_groups')
    extra_context = dict(lock_groups_page='active')

    def delete(self, request, *args, **kwargs):
        try:
            self.get_object().delete()
        except ProtectedError:
            messages.add_message(request, messages.ERROR,
                                 'Could not delete LockGroup "{:s}":'.format(self.get_object().name)
                                 + ' it is not allowed to delete LockGroups that have permissions attached.')
            return http.HttpResponseRedirect(urls.reverse_lazy('smartlock:del_lockgroup',
                                                               kwargs=dict(pk=self.get_object().pk)))
        return http.HttpResponseRedirect(self.success_url)


class UserDataGroupDeleteView(generic.edit.DeleteView):
    model = UserDataGroup
    success_url = urls.reverse_lazy('smartlock:user_groups')
    extra_context = dict(user_groups_page='active')

    def delete(self, request, *args, **kwargs):
        try:
            self.get_object().delete()
        except ProtectedError:
            messages.add_message(request, messages.ERROR,
                                 'Could not delete UserDataGroup "{:s}":'.format(self.get_object().name)
                                 + ' it is not allowed to delete UserDataGroups that have permissions attached.')
            return http.HttpResponseRedirect(urls.reverse_lazy('smartlock:del_userdatagroup',
                                                               kwargs=dict(pk=self.get_object().pk)))
        return http.HttpResponseRedirect(self.success_url)


class UnlockView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'smartlock/unlock_get.html')

    def post(self, request, *args, **kwargs):
        try:
            st_rfid = request.POST['rfid']
            userdata = UserData.objects.get(rfid=st_rfid)
        except KeyError:
            st_rfid = ''
            userdata = None
        except UserData.DoesNotExist:
            userdata = False
        try:
            st_ruid = request.POST['ruid']
            lock = Lock.objects.get(ruid=st_ruid)
        except KeyError:
            st_ruid = ''
            lock = None
        except (ValueError, Lock.DoesNotExist):
            lock = None
        try:
            flag_bttn = bool(Lock.objects.get(ruid=request.POST['button']))
        except KeyError:
            flag_bttn = False
        if (userdata is not False and
            ((userdata is not None and not flag_bttn) or (userdata is None and flag_bttn)) and
            lock is not None and
            Schedule.validate_lock_rfid_pair(st_ruid=st_ruid,
                                             st_rfid=st_rfid)):
            resp = http.HttpResponse('request accepted, open')
            succ = True
        else:
            resp = http.HttpResponse('request denied')
            succ = False
        if userdata == False:
            userdata = None
        ulog = UnlockAttemptLog(ruid=st_ruid,
                                rfid=st_rfid,
                                userdata=userdata,
                                lock=lock,
                                succ=succ)
        ulog.save()
        if 'test' not in sys.argv:
            print('→ {:s}'.format(str(ulog)))
        return resp
