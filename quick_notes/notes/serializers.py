from rest_framework import serializers
from django.template.defaultfilters import slugify
from typing import Dict
import json

from .models import Note
from .fields import INITIAL_CONTENT_FORMAT


class NoteSerializer(serializers.ModelSerializer):
    '''Note objects serializer'''

    allowed_content_types = ['text', 'list', 'list_item']

    title = serializers.CharField(required=True)
    content = serializers.JSONField(source="note_content.content", initial=INITIAL_CONTENT_FORMAT, required=True)
    details = serializers.JSONField(source="content.details", read_only=True)
    slug = serializers.SlugField(read_only=True)
    url = serializers.HyperlinkedIdentityField(view_name='note-detail', read_only=True, lookup_field='slug')
    edit_url = serializers.HyperlinkedIdentityField(view_name='note-update', read_only=True, lookup_field='slug')
    owner_username = serializers.CharField(source="owner.username", read_only=True)
    date_created = serializers.SerializerMethodField(read_only=True)
    last_edited = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Note
        fields = [
            'owner_username',
            'title',
            'content',
            'details',
            'slug',
            'starred',
            'url',
            'edit_url',
            'date_created',
            'last_edited',
        ]

    def get_date_created(self, note):
        return f"{note.date_created.date()} {note.date_created.time()}"

    def get_last_edited(self, note):
        return f"{note.last_edited.date()} {note.last_edited.time()}"

    def create(self, validated_data: Dict):
        validated_data['title'] = validated_data.get('title').strip()
        validated_data['note_content'] = validated_data['note_content']['content']
        request = self.context.get('request')
        validated_data.update({'owner': request.user})
        validated_data = self.add_slug(validated_data)

        return Note.objects.create(**validated_data)


    def update(self, instance, validated_data):
        title = validated_data.get('title').strip()
        validated_data['note_content'] = validated_data['note_content']['content']

        if instance.title.lower() != title.lower():
            validated_data = self.add_slug(validated_data)

        return super().update(instance, validated_data)

    
    def add_slug(self, validated_data: Dict):
        if not isinstance(validated_data, dict):
            raise TypeError('validated_data should be of type "dict"')

        title = validated_data.get('title')
        owner = validated_data.get('owner')
        slug = slugify(title)

        if owner:
            qs = Note.objects.filter(owner=owner, slug=slug)
            if qs.exists():
                slug = f'{slug}-{qs.count()}'
                
        validated_data['slug'] = slug

        return validated_data 


class StrippedNoteSerializer(NoteSerializer):
    class Meta(NoteSerializer.Meta):
        fields = [
            'title',
            'content',
            'slug',
            'owner_username',
            'url',
            'edit_url',
        ]



