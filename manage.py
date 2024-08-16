import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ProjectA.settings') #змінна середовища
    try:
        from django.core.management import execute_from_command_line # виконання команд Django з командного рядка
    except ImportError as exc:         #не вдалося імпортувати/неактивоване серидовище
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)         #дозволяє виконувати адміністративні команди Django


if __name__ == '__main__': # Перевірка, чи є скрипт основним модулем
    main()
