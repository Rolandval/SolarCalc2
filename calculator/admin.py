from django.contrib import admin
from .models import Users, Panels, Inverters, Batteries

# Register your models here.
admin.site.register(Users)
admin.site.register(Panels)
admin.site.register(Inverters)
admin.site.register(Batteries)