from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser


class CustomUserAdmin(UserAdmin) : 

    list_display = ("username", "firstname" , "lastname", "other_name", "date_joined" , "last_login" , "is_admin" , "is_staff", "is_superuser")
    search_fields = ("username", "firstname", "lastname", "other_name", "is_admin", "is_staff")
    readonly_fields = ("id" , "date_joined" , "last_login")
    filter_horizontal = ()
    fieldsets = ()
    list_filter = ("username" ,"firstname" ,"lastname", "is_staff", "is_admin", 'last_login')
    add_fieldsets = (
        (None, {'fields': ('username', 'firstname', 'lastname', 'other_name', 'password1', 'password2', "is_admin" , "is_staff")}),
    )
    ordering = ["username"]

admin.site.register(CustomUser, CustomUserAdmin)
