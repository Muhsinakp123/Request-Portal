from django.contrib import admin

# Register your models here.

from .models import Profile,MaintenanceRequest

admin.site.register(Profile),
admin.site.register(MaintenanceRequest)