from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Accepts legacy keys coming from the front-end:
        user_login | user_pass
    Maps them to Django’s canonical names:
        username   | password
    """

    # declare the incoming JSON fields
    user_login = serializers.CharField(write_only=True)
    user_pass  = serializers.CharField(write_only=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # make the default 'username' and 'password' *optional*
        # (they will be filled in validate())
        self.fields["username"].required = False
        self.fields["password"].required = False

    def validate(self, attrs):
        attrs = attrs.copy()                # might be an immutable QueryDict
        attrs["username"] = attrs.pop("user_login")
        attrs["password"] = attrs.pop("user_pass")
        return super().validate(attrs)
