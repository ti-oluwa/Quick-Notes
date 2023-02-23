from django.contrib.auth import logout
from rest_framework import serializers
from rest_framework.reverse import reverse
from django.contrib.auth.password_validation import validate_password


from .models import CustomUser



class UserSerializer(serializers.ModelSerializer):
    '''User model serializer'''
    username = serializers.CharField(required=True)
    firstname = serializers.CharField(required=True)
    lastname = serializers.CharField(required=True)
    last_active = serializers.SerializerMethodField(read_only=True)
    number_of_notes = serializers.SerializerMethodField(read_only=True)
    number_of_starred_notes = serializers.SerializerMethodField(read_only=True)
    last_created_note = serializers.SerializerMethodField(read_only=True)
    last_edited_note = serializers.SerializerMethodField(read_only=True)
    url = serializers.HyperlinkedIdentityField(view_name='account-detail', read_only=True, lookup_field='username')
    edit_url = serializers.HyperlinkedIdentityField(view_name='account-update', read_only=True, lookup_field='username')
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True, label="Confirm password")

    class Meta:
        model = CustomUser
        fields = [
            'username',
            'fullname',
            'firstname',
            'lastname',
            'other_name',
            'email',
            'password',
            'confirm_password',
            'url',
            'edit_url',
            'last_active',
            'number_of_notes',
            'number_of_starred_notes',
            'last_created_note',
            'last_edited_note',
        ]

    def validate(self, attrs):
        if attrs.get('password', None) and attrs.get('confirm_password', None):
            if attrs['password'] != attrs['confirm_password']:
                raise serializers.ValidationError('Passwords do not match')

            attrs.pop('confirm_password')
        return super().validate(attrs)


    def create(self, validated_data):
        validated_data = self.strip_validated_fields(validated_data)
        return self.Meta.model.objects.create_user(**validated_data)


    def update(self, user, validated_data):
        validated_data = self.strip_validated_fields(validated_data)
        return super().update(user, validated_data)


    def strip_validated_fields(self, validated_data):
        validated_data['username'] = validated_data.get('username').strip()
        validated_data['firstname'] = validated_data.get('firstname').strip()
        validated_data['lastname'] = validated_data.get('lastname').strip()
        validated_data['other_name'] = validated_data.get('other_name', '').strip()
        return validated_data

    def get_number_of_notes(self, user):
        return user.notes.count()

    def get_number_of_starred_notes(self, user):
        return user.notes.filter(starred=True).count()


    def get_last_active(self, user):
        return f"{user.last_login.date()} at {user.last_login.time()}"


    def get_last_created_note(self, user):
        note = user.notes.order_by('-date_created').first()
        request = self.context.get('request')

        if note:
            return reverse(viewname='note-detail', kwargs={'slug': note.slug}, request=request)
        return None


    def get_last_edited_note(self, user):
        note = user.notes.order_by('-date_created').first()
        request = self.context.get('request')

        if note:
            return reverse(viewname='note-detail', kwargs={'slug': note.slug}, request=request)
        return None


class StrippedUserSerializer(UserSerializer):
    '''Stripped version of the `UserSerializer` class'''

    date_joined = serializers.SerializerMethodField(read_only=True)
    class Meta(UserSerializer.Meta):
        fields = [
            'username',
            'fullname',
            'email',
            'firstname',
            'lastname',
            'other_name',
            'edit_url',
            'number_of_notes',
            'last_active',
            'date_joined',
        ]

    def get_date_joined(self, user):
        return f"{user.last_login.date()} at {user.last_login.time()}"


class UserChangeSerializer(UserSerializer):
    new_detail_url = serializers.HyperlinkedIdentityField(view_name='account-detail', read_only=True, lookup_field='username')
    class Meta(UserSerializer.Meta):
        fields = [
            'username',
            'firstname',
            'lastname',
            'other_name',
            'email',
            'new_detail_url',
        ]


class PasswordChangeSerializer(UserSerializer):
    password = serializers.CharField(write_only=True, required=True)
    confirm_password = serializers.CharField(write_only=True, required=True)
    login_url =  serializers.SerializerMethodField(read_only=True)
    message = serializers.SerializerMethodField(read_only=True)

    class Meta(UserSerializer.Meta):
        fields = [
            'username',
            'password',
            'confirm_password',
            'message',
            'login_url',
        ]

    def validate(self, attrs):
        if not attrs.get('password', None) or not attrs.get('confirm_password', None):
            raise serializers.ValidationError('`password` and `confirm_password` are required fields')
        return super().validate(attrs)

    def update(self, user, validated_data):
        request = self.context.get('request')
        password = validated_data.get('password')
        validate_password(password=password, user=user)
        user.set_password(password)
        user.save()
        logout(request)
        return user

    def get_login_url(self, user):
        request = self.context.get('request')
        return reverse(viewname='account-authenticate', request=request)

    def get_message(self, user):
        return f"Password update successful for {user.username}! Please authenticate again."