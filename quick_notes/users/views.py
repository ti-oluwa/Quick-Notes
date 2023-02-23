from typing import Dict
from django.contrib.auth import get_user_model
from rest_framework import generics, exceptions


from .serializers import UserSerializer, StrippedUserSerializer, UserChangeSerializer, PasswordChangeSerializer
from api.permissions import IsAdministratorOrSuperuser
from api.mixins import UsernameLookupMixin, AllowUserOrSuperuserMixin, AllowUserOnlyMixin
User = get_user_model()

global_queryset = User.objects.all()



class UserListAPIView(UsernameLookupMixin, generics.ListAPIView):
    serializer_class = StrippedUserSerializer
    queryset = global_queryset
    permission_classes = [IsAdministratorOrSuperuser]


class UserCreateAPIView(UsernameLookupMixin, generics.CreateAPIView):
    serializer_class = UserSerializer
    queryset = global_queryset
    permission_classes = []


class UserDetailAPIView(AllowUserOrSuperuserMixin, UsernameLookupMixin, generics.RetrieveAPIView):
    serializer_class = UserSerializer
    queryset = global_queryset


class UserUpdateAPIView(AllowUserOrSuperuserMixin, UsernameLookupMixin, generics.UpdateAPIView):
    serializer_class = UserChangeSerializer
    queryset = global_queryset

    def patch(self, request, *args, **kwargs):
        data: Dict = request.data
        user = self.get_object()

        if not data.get('username', None):
            data.update({'username': user.username})
        
        if not data.get('firstname', None):
            data.update({'firstname': user.firstname})
        
        if not data.get('lastname', None):
            data.update({'lastname': user.lastname})

        if not data.get('other_name', None):
            data.update({'other_name': user.other_name})

        if not data.get('email', None):
            data.update({'email': user.email})

        request.PATCH = data
        return super().patch(request, *args, **kwargs)


class UserDeleteAPIView(AllowUserOrSuperuserMixin, UsernameLookupMixin, generics.DestroyAPIView):
    serializer_class = UserSerializer
    queryset = global_queryset



class PasswordChangeAPIView(AllowUserOnlyMixin, UsernameLookupMixin, generics.UpdateAPIView):
    serializer_class = PasswordChangeSerializer
    queryset = global_queryset
    http_method_names = ['patch']

    def patch(self, request, *args, **kwargs):
        data: Dict = request.data
        username = data.get('username', None)
        user = self.get_object()

        if username and user.username == username:
            request.PATCH = data
            return super().patch(request, *args, **kwargs)
        
        raise exceptions.ValidationError('Username does not match this account')


class UserSearchAPIView(UserListAPIView):
    permission_classes = [IsAdministratorOrSuperuser]

    def get_queryset(self):
        query = self.request.GET.get('q')

        if not query:
            return User.objects.none()
            
        qs = super().get_queryset().search(query)
        return qs

    

