#!/usr/bin/env python
"""Utilitario de linha de comando do Django."""

import os
import sys


def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.dev")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:  # pragma: no cover
        raise ImportError("Django nao encontrado. O ambiente virtual esta ativo?") from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
