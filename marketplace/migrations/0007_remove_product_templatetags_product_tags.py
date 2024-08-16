# Generated by Django 5.0.7 on 2024-08-10 19:39

import taggit.managers
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('marketplace', '0006_product_tags'),
        ('taggit', '0006_rename_taggeditem_content_type_object_id_taggit_tagg_content_8fc721_idx'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='templatetags',
        ),
        migrations.AddField(
            model_name='product',
            name='tags',
            field=taggit.managers.TaggableManager(help_text='A comma-separated list of tags.', through='taggit.TaggedItem', to='taggit.Tag', verbose_name='Tags'),
        ),
    ]
