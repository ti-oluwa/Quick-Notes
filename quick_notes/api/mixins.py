from django.db import models
from rest_framework import serializers, exceptions
from django.contrib.auth import get_user_model

User = get_user_model()


class SlugLookupMixin():
    '''Sets the `lookup parameters` to `slug`'''
    lookup_field = 'slug'
    lookup_url_kwarg = 'slug'


class UsernameLookupMixin():
    '''Sets the `lookup parameters` to `username`'''
    lookup_field = 'username'
    lookup_url_kwarg = 'username'


class UserQuerySetMixin():
    '''Returns a user exclusive queryset'''
    
    def get_queryset(self, *args, **kwargs):
        qs: models.QuerySet = super().get_queryset(*args, **kwargs)
        
        return qs.filter(owner=self.request.user)


class AllowOwnerOnlyMixin():
    '''
        Allows only the `User` that owns the object to access the object.

        - The `obj_owner_field_name` refers to the serializer model field pointing to the user object.
    '''
    
    obj_owner_field_name = 'owner'
    
    def get_object(self, *args, **kwargs):
        obj = super().get_object(*args, **kwargs)

        if not hasattr(obj, self.obj_owner_field_name):
            raise serializers.FieldDoesNotExist(f"object does not have field `{self.obj_owner_field_name}`")

        obj_owner: User = getattr(obj, self.obj_owner_field_name)

        if not isinstance(obj_owner, User):
            raise TypeError(f"'object_owner_field_name' points to a field which does not contain a {User.__class__.__name__} object")

        user: User = self.request.user

        if not user.is_authenticated or not user == obj_owner:
            raise exceptions.PermissionDenied("You are not authorized to access this object")

        return obj


class AllowUserOrSuperuserMixin():

    def get_object(self, *args, **kwargs):
        user = super().get_object(*args, **kwargs)
        
        if not user.is_authenticated or not (self.request.user.pk == user.pk or self.request.user.is_superuser):
            raise exceptions.PermissionDenied("You are not authorized to access this account")
        return user


class AllowUserOnlyMixin():

    def get_object(self, *args, **kwargs):
        user = super().get_object(*args, **kwargs)
        
        if not user.is_authenticated or not self.request.user.pk == user.pk:
            raise exceptions.PermissionDenied("You are not authorized to access this account")
        return user



