from django.urls import path
from django.contrib.auth.decorators import login_required
from django.views import generic
from django import urls
from django.conf import settings
from django.contrib import auth
import django.forms

from . import views, models, forms

app_name = 'smartlock'
urlpatterns = [
    path('',
         login_required(views.HomeView.as_view()),
         name='index'),
    path('account/', views.account, name='account'),
    path('manage/',
         generic.RedirectView.as_view(url=urls.reverse_lazy('smartlock:users')),
         name='manage'),
    # UserData
    path('manage/users/',
         login_required(generic.ListView.as_view(model=models.UserData,
                                                 extra_context=dict(users_page='active'))),
         name='users'),
    path('manage/users/<int:pk>',
         login_required(views.UserAndUserDataUpdateView.as_view()),
         name='user'),
    path('manage/users/del_userdata/<int:pk>',
         login_required(views.UserAndUserDataDeleteView.as_view()),
         name='del_userdata'),
    path('manage/users/new_user/',
         login_required(views.UserAndUserDataCreateView.as_view()),
         name='new_user'),
    # UserDataGroup
    path('manage/user_groups/',
         login_required(generic.ListView.as_view(model=models.UserDataGroup,
                                                 extra_context=dict(user_groups_page='active'))),
         name='user_groups'),
    path('manage/user_groups/<int:pk>',
         login_required(views.UserDataGroupUpdateView.as_view()),
         name='user_group'),
    path('manage/del_userdatagroup/<int:pk>',
         login_required(views.UserDataGroupDeleteView.as_view()),
         name='del_userdatagroup'),
    path('manage/user_groups/new_user_group/',
         login_required(generic.CreateView.as_view(model=models.UserDataGroup,
                                                   fields=['name', 'grup'],
                                                   success_url=urls.reverse_lazy('smartlock:user_groups'),
                                                   extra_context=dict(user_groups_page='active'))),
         name='new_user_group'),
    # Lock
    path('manage/locks/',
         login_required(generic.ListView.as_view(model=models.Lock,
                                                 extra_context=dict(locks_page='active'))),
         name='locks'),
    path('manage/locks/<int:pk>',
         login_required(views.LockUpdateView.as_view()),
         name='lock'),
    path('manage/locks/del_lock/<int:pk>',
         login_required(views.LockDeleteView.as_view()),
         name='del_lock'),
    path('manage/locks/new_lock/',
         login_required(generic.CreateView.as_view(model=models.Lock,
                                                   fields=['name', 'tmzn'],
                                                   success_url=urls.reverse_lazy('smartlock:locks'),
                                                   extra_context=dict(locks_page='active'))),
         name='new_lock'),
    # LockGroup
    path('manage/lock_groups/',
         login_required(generic.ListView.as_view(model=models.LockGroup,
                                                 extra_context=dict(lock_groups_page='active'))),
         name='lock_groups'),
    path('manage/lock_groups/<int:pk>',
         login_required(views.LockGroupUpdateView.as_view()),
         name='lock_group'),
    path('manage/locks/del_lockgroup/<int:pk>',
         login_required(views.LockGroupDeleteView.as_view()),
         name='del_lockgroup'),
    path('manage/lock_groups/new_lock_group/',
         login_required(
             generic.CreateView.as_view(model=models.LockGroup, fields=['name', 'grup'],
                                        success_url=urls.reverse_lazy('smartlock:lock_groups'),
                                        extra_context=dict(lock_groups_page='active'))),
         name='new_lock_group'),
    # UnlockAttemptLog
    path('manage/unlockattemptlog/',
         login_required(generic.ListView.as_view(model=models.UnlockAttemptLog,
                                                 extra_context=dict(logs_page='active'))),
         name='logs'),
    # UnlockView
    path('unlock', views.UnlockView.as_view(), name='unlock'),
]
