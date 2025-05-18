from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django import forms
from django.utils.translation import gettext_lazy as _

from .models import (
    User, UserType, Company, Building, Unit, ODForm, Address, Contact
)


# 1) A creation form that only asks for the essentials:
class CustomUserCreationForm(forms.ModelForm):
    password1 = forms.CharField(label=_("Password"), widget=forms.PasswordInput)
    password2 = forms.CharField(label=_("Confirm password"), widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ("username", "email", "user_type")

    def clean_password2(self):
        p1 = self.cleaned_data.get("password1")
        p2 = self.cleaned_data.get("password2")
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError(_("Passwords don’t match"))
        return p2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


# 2) A change form for the existing user:
class CustomUserChangeForm(forms.ModelForm):
    class Meta:
        model = User
        fields = (
            "username", "email", "first_name", "last_name",
            "is_active", "is_staff", "is_superuser", "user_type"
        )


# 3) Finally, hook them into your UserAdmin
@admin.register(User)
class CustomUserAdmin(BaseUserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = User

    list_display = ("username", "email", "first_name", "last_name", "is_staff", "user_type")
    list_filter = ("is_staff", "is_superuser", "is_active", "user_type")
    search_fields = ("username", "email", "first_name", "last_name")
    ordering = ("username",)

    fieldsets = (
        (None,               {"fields": ("username", "password")}),
        (_("Personal info"), {"fields": ("first_name", "last_name", "email", "user_type")}),
        (_("Permissions"),   {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("username", "email", "user_type", "password1", "password2"),
        }),
    )


# 4) And register the rest of your models as before:
admin.site.register(UserType)
admin.site.register(Company)
admin.site.register(Building)
admin.site.register(Unit)
admin.site.register(ODForm)
admin.site.register(Address)
admin.site.register(Contact)
