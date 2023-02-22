from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin


from .managers import AbstractBaseUserManager
from .gpm import GroupPermissionManager




class CustomUser(AbstractBaseUser, PermissionsMixin):
    '''Custom user model'''

    username = models.CharField(max_length=200, unique=True, default=None)
    firstname = models.CharField(max_length=200, verbose_name='First name', default="", null=True)
    lastname = models.CharField(max_length=200, verbose_name='Last name', default="", null=True)
    other_name = models.CharField(max_length=200, verbose_name='Other name', null=True, blank=True, default="")
    email = models.EmailField(verbose_name='Email address', blank=True, default="", null=True)
    is_staff = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(verbose_name='date joined', auto_now_add=True)
    last_login = models.DateTimeField(verbose_name='last login', auto_now=True)

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["firstname", "lastname", "email"]

    objects = AbstractBaseUserManager()


    def __str__(self):
        return self.username


    @property
    def fullname(self):
        if self.other_name:
            return f"{self.firstname} {self.other_name} {self.lastname}".title()  
        return f"{self.firstname} {self.lastname}".title()


    def save(self, *args, **kwargs):
        self.is_staff = any((self.is_admin, self.is_superuser))
        super().save(*args, **kwargs)
        admin_perm_manager = GroupPermissionManager('Admin')
        admin_perm_manager.ActiveUserModel = self.__class__

        if self.is_admin:
            admin_perm_manager.add_to_group(self)
        else:
            admin_perm_manager.remove_from_group(self)





