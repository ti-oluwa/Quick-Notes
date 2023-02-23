from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token


from . import views

urlpatterns = [
    path('', views.UserListAPIView.as_view(), name="account-list"),
    path('create/', views.UserCreateAPIView.as_view(), name="account-create"),
    path('authenticate/', obtain_auth_token, name="account-authenticate"),
    path('find/', views.UserSearchAPIView.as_view(), name="account-find"),
    path('<str:username>/', views.UserDetailAPIView.as_view(), name="account-detail"),
    path('<str:username>/update/', views.UserUpdateAPIView.as_view(), name="account-update"),
    path('<str:username>/change-password/', views.PasswordChangeAPIView.as_view(), name="account-change-password"),
    path('<str:username>/delete/', views.UserDeleteAPIView.as_view(), name="account-delete"),
]
