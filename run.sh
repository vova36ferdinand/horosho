#!/bin/bash
set -e

echo "=== 1. Проверка покрытия тестами ==="
python -m coverage run --branch --source=src \
    --omit="src/repl.py,src/__init__.py" -m pytest tests/test_mbt.py
python -m coverage report -m
python -m pytest -q --ignore=tests/test_mbt.py

echo "=== 2. Запуск REPL меню ==="
python src/repl.py
