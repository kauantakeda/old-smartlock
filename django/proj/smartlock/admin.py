from django.contrib import admin

from django.conf import settings

from .models import UserData, UserDataGroup
from .models import Lock, LockGroup
from .models import UnlockAttemptLog
from .models import Schedule

admin.site.register(UserData)
admin.site.register(UserDataGroup)

admin.site.register(Lock)
admin.site.register(LockGroup)

admin.site.register(UnlockAttemptLog)

admin.site.register(Schedule)
