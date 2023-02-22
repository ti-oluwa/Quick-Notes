from django.contrib.auth import get_user_model
from rest_framework import generics

from .serializers import UserSerializer, StrippedUserSerializer
from api.permissions import IsAdministratorOrSuperuser
from api.mixins import UsernameLookupMixin
User = get_user_model()

global_queryset = User.objects.all()



class UserListAPIView(UsernameLookupMixin, generics.ListAPIView):
    serializer_class = StrippedUserSerializer
    queryset = global_queryset
    permission_classes = [IsAdministratorOrSuperuser]


class UserCreateAPIView(UsernameLookupMixin, generics.CreateAPIView):
    serializer_class = UserSerializer
    queryset = global_queryset


class UserDetailAPIView(UsernameLookupMixin, generics.RetrieveAPIView):
    serializer_class = UserSerializer
    queryset = global_queryset


class UserUpdateAPIView(UsernameLookupMixin, generics.UpdateAPIView):
    serializer_class = UserSerializer
    queryset = global_queryset


class UserDeleteAPIView(UsernameLookupMixin, generics.DestroyAPIView):
    serializer_class = UserSerializer
    queryset = global_queryset


class UserSearchAPIView(UserListAPIView):
    permission_classes = [IsAdministratorOrSuperuser]

    def get_queryset(self):
        query = self.request.GET.get('q')

        if not query:
            return User.objects.none()
            
        qs = super().get_queryset().search(query)
        return qs

    

