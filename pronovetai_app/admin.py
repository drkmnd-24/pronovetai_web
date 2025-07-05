from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django import forms

from .models import (User, UserType, Company,
                     Building, Unit, ODForm,
                     Address, Contact)


class CustomUserCreationForm(forms.ModelForm):
    """
    A form for creating new users.  We include the usual
    user-type fields plus two BooleanFields here, but they
    aren’t real model fields.
    """
    password1 = forms.CharField(label="Password", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Password confirmation", widget=forms.PasswordInput)

    # declare them at form-level
    is_active = forms.BooleanField(label="Active", required=False, initial=True)
    is_staff = forms.BooleanField(label="Staff status", required=False, initial=False)

    class Meta:
        model = User
        fields = (
            "username", "email",
            "first_name", "last_name",
            "user_type",
            "is_staff", "is_superuser", "is_active",
        )

    def clean_password2(self):
        p1 = self.cleaned_data.get("password1")
        p2 = self.cleaned_data.get("password2")
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("Passwords don't match")
        return p2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        # apply our form-level booleans
        user.is_active = self.cleaned_data["is_active"]
        user.is_staff = self.cleaned_data["is_staff"]
        if commit:
            user.save()
        return user


class CustomUserChangeForm(forms.ModelForm):
    """
    A form for updating existing users; similarly we handle
    is_active and is_staff here at the form level.
    """
    is_active = forms.BooleanField(label="Active", required=False)
    is_staff = forms.BooleanField(label="Staff status", required=False)

    class Meta(UserChangeForm.Meta):
        model  = User
        fields = (
            "username", "email",
            "first_name", "last_name",
            "user_type",
            "is_staff", "is_superuser", "is_active",
            "groups", "user_permissions",
        )

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_active = self.cleaned_data["is_active"]
        user.is_staff = self.cleaned_data["is_staff"]
        if commit:
            user.save()
        return user


@admin.register(User)
class CustomUserAdmin(BaseUserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = User

    list_display = (
        "username", "email", "first_name", "last_name",
        "user_type", "is_staff", "is_superuser", "is_active",
    )
    list_filter = ("is_staff", "is_superuser", "is_active", "user_type")
    search_fields = ("username", "first_name", "last_name", "email")
    ordering = ("username",)

    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Personal info", {"fields": ("first_name", "last_name", "email")}),
        ("Role", {"fields": ("user_type",)}),
        ("Permissions", {"fields": (
            "is_active", "is_staff", "is_superuser",
            "groups", "user_permissions",
        )}),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": (
                "username", "email",
                "first_name", "last_name", "user_type",
                "password1", "password2",
                "is_staff", "is_superuser", "is_active",
            ),
        }),
    )

    filter_horizontal = ("groups", "user_permissions")


admin.site.register(UserType)
admin.site.register(Company)
admin.site.register(Building)
admin.site.register(Unit)
admin.site.register(ODForm)
admin.site.register(Address)
admin.site.register(Contact)
