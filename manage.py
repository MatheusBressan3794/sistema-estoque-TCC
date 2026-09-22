#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
import sqlite3

os.environ["PYTHONUTF8"] = "1"

# Decodifica corretamente os caracteres antigos do SQLite (como ç em latin1)
old_connect = sqlite3.connect
def new_connect(*args, **kwargs):
    conn = old_connect(*args, **kwargs)
    conn.text_factory = lambda b: b.decode('latin1', errors='replace')
    return conn
sqlite3.connect = new_connect


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'controle_estoque.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()