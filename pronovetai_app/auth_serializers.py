# pronovetai_app/auth_serializers.py
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = "user_login"          # use your legacy column name

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # 1️⃣  make the auto-generated password field optional
        self.fields["password"].required = False

        # 2️⃣  add the legacy password key that the front-end sends
        self.fields["user_pass"] = serializers.CharField(write_only=True)

    def validate(self, attrs):
        attrs = attrs.copy()                       # may be an immutable QueryDict
        attrs["password"] = attrs.pop("user_pass")  # map legacy → real
        return super().validate(attrs)
