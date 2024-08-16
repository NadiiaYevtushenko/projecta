"""
ASGI config for ProjectA project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/asgi/
"""

import os  #надає інтерфейс для взаємодії з операційною системою; вик. для налаштування змінних середовища.

from django.core.asgi import get_asgi_application #  повертає об'єкт ASGI-додатка, який використовується для обробки запитів

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ProjectA.settings') #налаштувань Django проекту ProjectA.

application = get_asgi_application()
#створення об'єкта ASGI-додатка і призначає його змінній application.
# Цей об'єкт буде використовуватися сервером для обробки запитів.
