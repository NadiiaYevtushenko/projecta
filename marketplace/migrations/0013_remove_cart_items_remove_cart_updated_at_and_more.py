# Generated by Django 5.0.7 on 2024-08-13 12:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('marketplace', '0012_cart_cartitem_cart_items'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cart',
            name='items',
        ),
        migrations.RemoveField(
            model_name='cart',
            name='updated_at',
        ),
        migrations.DeleteModel(
            name='CartItem',
        ),
    ]
