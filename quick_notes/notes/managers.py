from django.db import models



class NoteQuerySet(models.QuerySet):
    '''Note model custom queryset'''
    
    def search(self, query, user=None):
        lookup = models.Q(title__icontains=query) | models.Q(content__icontains=query)
        qs = self.filter(lookup)

        if user:
            qs2 = self.filter(user=user).filter(lookup)
            # qs = qs.union(qs2).distinct()
            qs = (qs | qs2).distinct()

        return qs.order_by('title')


class NoteManager(models.Manager):
    '''Note model custom objects manager'''

    def get_queryset(self):
        return NoteQuerySet(self.model, using=self._db)

    def search(self, query, user=None):
        return self.get_queryset().search(query, user=user)