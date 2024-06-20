from django.contrib import admin
from .models import Topup_info


class Topup_infoAdmin(admin.ModelAdmin):
    list_display=("user", "quantity", "Date", "Category", "top_up")
    admin.site.rgister(Topup_info, Topup_infoAdmin)

    from django.contrib.sessions.models import Session
    admin.site.register(Session)

    from .models import UserProfile
    admin.site.register(UserProfile)



