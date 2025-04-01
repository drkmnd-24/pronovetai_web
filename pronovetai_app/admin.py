from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User, Company, Building, Unit, ODForm, Address, Contact


admin.site.register(User, UserAdmin)
admin.site.register(Company)
admin.site.register(Building)
admin.site.register(Unit)
admin.site.register(ODForm)
admin.site.register(Address)
admin.site.register(Contact)
