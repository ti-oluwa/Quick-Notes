from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Permission, Group, AbstractBaseUser, User
from django.db.models.query import QuerySet
from typing import List, Pattern, Type, Dict
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured, ValidationError
from django.apps import apps
from django.utils.itercompat import is_iterable
import re
from abc import abstractmethod



class GroupNotFoundError(Exception):
    note = "Group not found! It may have been deleted"
    def __init__(self, note=None):
        if note:
            self.note = note

    def add_note(self, __note: str=note):
        return super().add_note(__note)


class GroupPermissionManager:
    '''
    Manages `Group` objects permissions
    '''
    default_configuration_name = "GPM_CONFIG"
    __allowed_perms__: QuerySet[Permission] = Permission.objects.none()
    __disallowed_perms__: QuerySet[Permission] = Permission.objects.none()
    perm_str_pattern = re.compile('[a-z]{1,}.[a-z]{2,}_[a-z]{1,}')
    perm_str_validation_error = ValidationError("The permission string should take form <app_label>.<permission>_<model_name>")
    ActiveUserModel: AbstractBaseUser | User = None

    def __init__(self, group_name: str):
        group, _ = Group.objects.get_or_create(name=group_name)
        self.group_name = group.name.lower().capitalize()
        super().__init__()
        self.add_permissions(default=True)
        self.revoke_permissions(default=True)

    def __repr__(self):
        return "Permission manager for %s group" % self.group_name

    def __str__(self):
        return self.__repr__()

    def __getattribute__(self, __name: str):
        if __name == "default_configuration_name":
            value: str = super().__getattribute__(__name)
            return value.upper()

        return super().__getattribute__(__name)


    def __setattr__(self, __name: str, __value, __key: str=None):
        if __name in ("__allowed_perms__", "__disallowed_perms__") and (__key is None or __key != self.group_name):
            raise AttributeError("'%s' is not a mutable attribute" % __name)

        if __name == "default_configuration_name":
            if not isinstance(__value, str) or isinstance(__value, list):
                raise AttributeError("Invalid attribute type for `default_configuration_name`. `default_configuration_name` should be a string")

        if __name == "perm_str_pattern":
            if not isinstance(__value, Pattern):
                raise AttributeError("Invalid attribute type for `perm_str_pattern`. `perm_str_pattern` should be a regex pattern")

        if __name == "perm_str_validation_error":
            if not isinstance(__value, ValidationError):
                raise AttributeError("Invalid attribute type for `perm_str_validation_error`, `perm_str_validation_error` should be a 'ValidationError'")

        return super().__setattr__(__name, __value)


    def __get_all_attrs__(self):
        '''
        Returns a dict containing all attribute of the instance.
        '''
        attrs = {
            'name': self.__str__(),
            'group_name': self.group_name,
            'group': self.group,
            'allowed_permissions': self.allowed_permissions,
            'disallowed_permissions': self.disallowed_permissions,
            'permission_string_pattern': self.perm_str_pattern,
        }
        return attrs

    @property
    def group(self):
        '''
        Returns the `Group` object the instance is managing.
        '''
        group = Group.objects.filter(name__iexact=self.group_name)
        if group.exists():
            return group.first()
        else:
            raise GroupNotFoundError

    @property
    def allowed_permissions(self):
        '''
        A queryset containing all permissions the `instance.group` is allowed to have.
        '''
        return self.__allowed_perms__

    @property
    def disallowed_permissions(self):
        '''
        A queryset containing all permissions that the `instance.group` is not allowed to have.
        '''
        return self.__disallowed_perms__


    def __get_default_perms__(self):
        '''
        Validates and returns the default permission configurations in settings.py
        '''
        default_allowed_perms = None
        default_disallowed_perms = None

        if hasattr(settings, self.default_configuration_name):
            gpm_config: Dict = getattr(settings, self.default_configuration_name)
            if not isinstance(gpm_config, dict):
                raise ImproperlyConfigured("Invalid type: {} for {}".format(type(gpm_config), self.default_configuration_name))
        
        default_allowed_perms = gpm_config.get("ALLOWED_PERMS_FOR_%s" % self.group_name.upper(), None)
        if default_allowed_perms is not None and (not isinstance(default_allowed_perms, list) or not all([isinstance(item, str) for item in default_allowed_perms])):
            raise ImproperlyConfigured("settings.{}.{} should be of type List[str, ...]".format(self.default_configuration_name, "ALLOWED_PERMS_FOR_%s" % self.group_name.upper()))

        default_disallowed_perms = gpm_config.get("DISALLOWED_PERMS_FOR_%s" % self.group_name.upper(), None)
        if default_disallowed_perms is not None and (not isinstance(default_disallowed_perms, list) or not all([isinstance(item, str) for item in default_disallowed_perms])):
            raise ImproperlyConfigured("settings.{}.{} should be of type List[str, ...]".format(self.default_configuration_name, "DISALLOWED_PERMS_FOR_%s" % self.group_name.upper()))
        
        return (default_allowed_perms, default_disallowed_perms)


    @abstractmethod
    def __validate_perm_strs__(self, perm_strs: str | List[str]):
        '''
        Accepts and Validates a permission string with the defined `perm_str_pattern` attribute or a list of such permission string.
        
        This is an `abstractmethod` and it must be implemented when subclassing.

        Returns a list of permission strings.
        '''
        perm_str_pattern = self.perm_str_pattern
        validation_error = self.perm_str_validation_error
        perm_str_list: List[str] = []

        if not isinstance(perm_strs, (list, str)):
            raise ValueError("`perm_strs` should be a permission string or list of permission strings and not %s" % type(perm_strs))
        else:
            if isinstance(perm_strs, list):
                perm_str_list.extend(perm_strs)
            else:
                perm_str_list.append(perm_strs)   

        for perm_str in perm_str_list:
            if not re.fullmatch(perm_str_pattern, perm_str) and not len(perm_str.split('.')) == 2:
                raise validation_error

            app_label, permission_codename = perm_str.split('.')
            model_name = permission_codename.split('_')[-1]
            try:
                _ = apps.get_model(app_label=app_label, model_name=model_name, require_ready=True)
            except ValueError:
                raise validation_error

        return perm_str_list

    
    def __validate_perm_objects__(self, perm_objects: Permission | QuerySet[Permission] | List[Permission]):
        '''
        Accepts and Validates a `Permission` object, queryset or  list of `Permission` objects.

        Returns a queryset containing the `Permission` object(s).
        '''
        perm_objects_id_list = []
        perm_objects_qs: QuerySet[Permission] = Permission.objects.none()
        
        if not isinstance(perm_objects, (list, Permission, QuerySet)):
            raise ValueError("`perm_obj` should be a permission obj or list of permission obj  and not %s" % type(perm_objects))

        if isinstance(perm_objects, list):
            perm_objects_id_list.extend([obj.codename for obj in perm_objects])

        elif isinstance(perm_objects, Permission):
            perm_objects_id_list.append(perm_objects.codename)

        elif isinstance(perm_objects, QuerySet):
            perm_objects_qs |= perm_objects
         
        perm_objects_qs |= Permission.objects.filter(codename__in=perm_objects_id_list)
        return perm_objects_qs


    def __validate_user_objects__(self, users: Type[User | AbstractBaseUser] | QuerySet[User | AbstractBaseUser]):
        if not self.ActiveUserModel:
            raise AttributeError("Invalid type: %s for `instance.ActiveUserModel`" % type(self.ActiveUserModel))

        if not isinstance(users, (self.ActiveUserModel, QuerySet)):
            raise TypeError(users)

        if isinstance(users, QuerySet) and not isinstance(users.first(), self.ActiveUserModel):
            raise TypeError('Invalid queryset for QuerySet[%s]' % self.ActiveUserModel.__class__.__name__.title())

        user_qs = self.ActiveUserModel.objects.none()
        if is_iterable(users):
            user_qs |= users
        else:
            user_qs |= self.ActiveUserModel.objects.filter(pk=users.pk)

        return user_qs
            

    def get_contenttype(self, perm_str: str):
        '''
        Returns the `ContentType` of the model as defined in the permission string.
        '''
        if not isinstance(perm_str, str) or isinstance(perm_str, list):
            raise TypeError("`perm_str` should be of type str not %s" % type(perm_str))

        self.__validate_perm_strs__(perm_str)
        app_label, permission_codename = perm_str.split('.')
        model_name = permission_codename.split('_')[-1]
        model = apps.get_model(app_label=app_label, model_name=model_name, require_ready=True)
        return ContentType.objects.get_for_model(model)

    
    def get_all_permissions(self):
        '''Returns `instance.group.permissions.all`'''
        return self.group.permissions.all()

    def get_perm_objects(self, perm_strs: str | List[str]):
        '''
        Accepts a permission string or a list of permission strings and returns a queryset containing the corresponding `Permission` object(s).
        '''
        perm_strs = self.__validate_perm_strs__(perm_strs)
        objs: QuerySet[Permission] = Permission.objects.none()
        for perm_str in perm_strs:
            content_type = self.get_contenttype(perm_str)
            try:
                perm = Permission.objects.filter(content_type=content_type, codename=perm_str.split('.')[-1])
                objs |= perm

            except Permission.DoesNotExist:
                raise ValueError(f"`{perm_str}` is not a valid permission string!")
        return objs


    def add_permissions(self, perm_objects: Permission | QuerySet[Permission] | List[Permission]=None, perm_strs: str | List[str]=None, default=True):
        '''
        Adds permissions to `instance.group`.

        PARAMS DESCRIPTION:
        - `perm_objects`: A `Permission` object, queryset or list of `Permission` objects.
        - `perm_strs`: A permission string or list of permission strings.
        - `default`: The default permission(s) configured in settings.py will be added if set to True, or otherwise will be done if set to False.

        '''
        if not any((perm_objects, perm_strs, default)):
            raise SyntaxError("You cannot set the `default` argument to 'False' if `perms_objects` and `perm_strs` are None")
        
        permissions_qs: QuerySet[Permission] = Permission.objects.none()

        if default and self.__get_default_perms__()[0]:
            permissions_qs |= self.get_perm_objects(self.__get_default_perms__()[0])

        if perm_objects:
            perm_objects = self.__validate_perm_objects__(perm_objects)
            permissions_qs |= perm_objects

        if perm_strs:
            perm_strs = self.__validate_perm_strs__(perm_strs)
            permissions_qs |= self.get_perm_objects(perm_strs)

        if permissions_qs:
            self.__setattr__("__allowed_perms__", self.allowed_permissions.union(permissions_qs), self.group_name)

            for perm in permissions_qs:
                self.group.permissions.add(perm)
            self.group.save()


    def revoke_permissions(self, perm_objects: Permission | QuerySet[Permission] | List[Permission]=None, perm_strs: str | List[str]=None, default=True):
        '''
        Removes permissions to `instance.group`.

        PARAMS DESCRIPTION:
        - `perm_objects`: A `Permission` object, queryset or list of `Permission` objects.
        - `perm_strs`: A permission string or list of permission strings.
        - `default`: The default permission(s) configured in settings.py will be removed if set to True, or otherwise will be done if set to False.

        '''
        if not any((perm_objects, perm_strs, default)):
            raise SyntaxError("You cannot set the `default` argument to 'False' if `perms_objects` and `perm_strs` are None")
        
        permissions_qs: QuerySet[Permission] = Permission.objects.none()

        if default and self.__get_default_perms__()[-1]:
            permissions_qs |= self.get_perm_objects(self.__get_default_perms__()[-1])

        if perm_objects:
            perm_objects = self.__validate_perm_objects__(perm_objects)
            permissions_qs |= perm_objects

        if perm_strs:
            perm_strs = self.__validate_perm_strs__(perm_strs)
            permissions_qs |= self.get_perm_objects(perm_strs)

        if permissions_qs:
            for perm in permissions_qs:
                value = self.allowed_permissions.exclude(codename=perm.codename)
            self.__setattr__("__allowed_perms__", value, self.group_name)
            self.__setattr__("__disallowed_perms__", self.disallowed_permissions.union(permissions_qs), self.group_name)

            for perm in permissions_qs:
                self.group.permissions.remove(perm)
            self.group.save()

    
    def add_to_group(self, users: Type[User | AbstractBaseUser] | QuerySet[User | AbstractBaseUser]):
        user_qs = self.__validate_user_objects__(users)
        if user_qs:
            for user in user_qs:
                self.group.user_set.add(user)
            self.group.save()


    def remove_from_group(self, users: Type[User | AbstractBaseUser] | QuerySet[User | AbstractBaseUser]):
        user_qs = self.__validate_user_objects__(users)
        if user_qs:
            for user in user_qs:
                self.group.user_set.remove(user)
            self.group.save()


