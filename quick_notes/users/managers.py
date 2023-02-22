from django.contrib.auth.models import BaseUserManager
from django.db import models



class AbstractBaseUserManager(BaseUserManager):
    '''Custom `User` model manager'''
    use_in_migrations = True

    def create_user(self, username, firstname, lastname, email, password, **other_fields):

        if not username:
            raise ValueError('Username is a required field')

        if not firstname:
            raise ValueError('Firstname is a required field')

        if not lastname:
            raise ValueError('Lastname is a required field')

        if not password:
            raise ValueError('Password is a required field')

        fields = {
            'username': username,
            'firstname': firstname,
            'lastname': lastname,
            'email': self.normalize_email(email),
        }
        fields.update(**other_fields)
        user = self.model(**fields)
        user.set_password(password)

        if user.is_admin or user.is_superuser:
            user.is_staff = True

        user.save(using=self._db)
        return user


    def create_superuser(self, username, firstname, lastname, email, password, **other_fields):
        
        if other_fields.get('is_superuser') and other_fields.get('is_superuser') is not True:
            raise ValueError("Super user must have is_superuser=True")

        fields = {
            'username': username,
            'firstname': firstname,
            'lastname': lastname,
            'email': email,
            'password': password,
            'is_admin': True,
            'is_superuser': True,
        }

        fields.update(**other_fields)
        user = self.create_user(**fields)
        
        return user

    def get_queryset(self):
        return UserQuerySet(model=self.model, using=self._db)

    def search(self, query):
        return self.get_queryset().search(query=query)


class UserQuerySet(models.QuerySet):
    '''Custom `User` model custom queryset'''

    def search(self, query):
        lookup = models.Q(username__icontains=query) | models.Q(firstname__icontains=query) | models.Q(lastname__icontains=query) | models.Q(other_name__icontains=query)
        qs = self.filter(lookup)
        return qs