# Generated by Django 4.1.7 on 2023-02-21 20:17

from django.db import migrations, models
import notes.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='List',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('last_edited', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='ListItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('index', models.IntegerField(default=0)),
                ('body', models.CharField(max_length=500)),
                ('checked', models.BooleanField(default=False)),
                ('last_edited', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ['index'],
            },
        ),
        migrations.CreateModel(
            name='Note',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slug', models.SlugField(auto_created=True, blank=True, editable=False, max_length=200, unique=True)),
                ('title', models.CharField(help_text='Enter a title for your note', max_length=400, null=True)),
                ('content', notes.fields.NoteContentField(blank=True, null=True)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('last_edited', models.DateTimeField(auto_now=True)),
                ('starred', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name': 'note',
                'verbose_name_plural': 'notes',
                'ordering': ['-date_created', 'title'],
            },
        ),
        migrations.CreateModel(
            name='Text',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('body', models.TextField(blank=True, default='', help_text='Write your note here', null=True)),
                ('last_edited', models.DateTimeField(auto_now=True)),
            ],
        ),
    ]