from django.db import models
from django.contrib.auth import get_user_model
from django.template.defaultfilters import slugify
from django.utils.translation import gettext_lazy as _

from .managers import NoteManager
from .fields import NoteContentField, INITIAL_CONTENT_FORMAT

User = get_user_model()


class Note(models.Model):
    '''Notes model'''

    title = models.CharField(max_length=400, null=True, help_text='Enter a title for your note')
    note_content = NoteContentField(null=True)
    owner = models.ForeignKey(User, related_name='notes', on_delete=models.CASCADE, verbose_name='Note owner', default=None, null=True)
    slug = models.SlugField(max_length=200, unique=True, auto_created=True, editable=False, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    last_edited = models.DateTimeField(auto_now=True)
    starred = models.BooleanField(default=False)

    objects = NoteManager()

    class Meta:
        verbose_name = _("note")
        verbose_name_plural = _("notes")
        ordering = ['-date_created', 'title']
        unique_together = ('slug', 'owner')

    def __str__(self):
        return self.slug


    def save(self, *args, **kwargs):
        if not self.slug:
            slug = slugify(self.title)

            if self.owner:
                qs = Note.objects.filter(owner=self.owner, slug=slug)
                if qs.exists():
                    slug = f'{slug}_{qs.count()}'
                    
            self.slug = slug

        return super().save(*args, **kwargs)


    
