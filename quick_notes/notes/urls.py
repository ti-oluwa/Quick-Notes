from django.urls import path
from . import views


urlpatterns = [
    path('', views.NoteListCreateAPIView.as_view(), name='note-list-create'),
    path('find/', views.NoteSearchAPIView.as_view(), name='note-find'),
    path('starred/', views.StarredNoteListAPIView.as_view(), name='starred-note-list'),
    path('<str:slug>/', views.NoteDetailAPIView.as_view(), name='note-detail'),
    path('<str:slug>/edit/', views.NoteUpdateAPIView.as_view(), name="note-update"),
    path('<str:slug>/delete/', views.NoteDestroyAPIView.as_view(), name='note-delete'),
]
