from django.urls import path, include


urlpatterns = [
    path('accounts/', include('users.urls'), name='accounts'),
    path('notes/', include('notes.urls'), name='notes'),
]
