from rest_framework import permissions
from django.contrib.auth import get_user_model
User = get_user_model()



class IsAdministratorOrSuperuser(permissions.IsAdminUser):
    '''Permits admins and superusers only'''
    def has_permission(self, request, view):
        if request.user.is_authenticated and (request.user.is_admin or request.user.is_superuser):
            return True
        return False


class UserAccountOwnerToUpdateReadDeleteOrAdminReadOnlyPermission(permissions.DjangoModelPermissions):

    perms_map = {
        'GET': ['%(app_label)s.view_%(model_name)s'],
        'OPTIONS': [],
        'HEAD': [],
        'POST': [],
        'PUT': ['%(app_label)s.change_%(model_name)s'],
        'PATCH': ['%(app_label)s.change_%(model_name)s'],
        'DELETE': ['%(app_label)s.delete_%(model_name)s'],
    }

    authenticated_users_only = True



                
