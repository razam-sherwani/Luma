#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'providerpulse.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    
    # Automatically run migrations on startup for Railway
    if 'runserver' not in sys.argv and 'migrate' not in sys.argv:
        # Run migrations
        execute_from_command_line(['manage.py', 'migrate'])
        # Seed database if it's empty
        try:
            from core.models import HCP
            if not HCP.objects.exists():
                execute_from_command_line(['manage.py', 'shell', '-c', 
                    'import os; exec(open("seed_real_emr.py").read()) if os.path.exists("seed_real_emr.py") else None'])
        except:
            pass
    
    execute_from_command_line(sys.argv)