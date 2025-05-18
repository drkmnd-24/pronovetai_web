from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from .models import User, Company, Building, Unit, ODForm, Address, Contact


# Custom “add” form — only includes the fields you actually have
class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("username", "email", "first_name", "last_name", "role")


# Custom “change” form
class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = ("username", "email", "first_name", "last_name", "role")


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = User

    list_display = ("username", "email", "first_name", "last_name", "role")
    list_filter = ("role",)  # drop staff/superuser/active filters
    search_fields = ("username", "email", "first_name", "last_name")
    ordering = ("username",)

    # redefine fieldsets so they don’t refer to missing flags
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Personal info", {"fields": ("first_name", "last_name", "email")}),
        ("Role", {"fields": ("role",)}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("username", "role", "password1", "password2"),
        }),
    )

    filter_horizontal = ()


# register the rest of your models normally
admin.site.register(Company)
admin.site.register(Building)
admin.site.register(Unit)
admin.site.register(ODForm)
admin.site.register(Address)
admin.site.register(Contact)
