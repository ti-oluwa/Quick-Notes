from rest_framework import generics

from .models import Note
from .serializers import NoteSerializer, StrippedNoteSerializer
from api.mixins import SlugLookupMixin, UserQuerySetMixin, AllowOwnerOnlyMixin

global_queryset = Note.objects.all()


class NoteListCreateAPIView(UserQuerySetMixin, SlugLookupMixin, generics.ListCreateAPIView):
    queryset = global_queryset
    serializer_class = StrippedNoteSerializer


class StarredNoteListAPIView(UserQuerySetMixin, SlugLookupMixin, generics.ListAPIView):
    queryset = global_queryset
    serializer_class = StrippedNoteSerializer

    def get_queryset(self, *args, **kwargs):
        qs = super().get_queryset(*args, **kwargs)
        return qs.filter(starred=True)


class NoteDetailAPIView(AllowOwnerOnlyMixin, SlugLookupMixin, generics.RetrieveAPIView):
    queryset = global_queryset
    serializer_class = NoteSerializer


class NoteUpdateAPIView(AllowOwnerOnlyMixin, SlugLookupMixin, generics.UpdateAPIView):
    queryset = global_queryset
    serializer_class = NoteSerializer


class NoteDestroyAPIView(AllowOwnerOnlyMixin, SlugLookupMixin, generics.DestroyAPIView):
    queryset = global_queryset
    serializer_class = NoteSerializer


class NoteSearchAPIView(UserQuerySetMixin, SlugLookupMixin, generics.ListAPIView):
    queryset = global_queryset
    serializer_class = StrippedNoteSerializer

    def get_queryset(self):
        query = self.request.GET.get('q')

        if not query:
            return Note.objects.none()

        qs = super().get_queryset().search(query)
        return qs

