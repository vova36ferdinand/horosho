#!/bin/bash
set -e

echo "=== 1. Проверка покрытия тестами ==="
coverage run --branch -m pytest
coverage report -m

echo "=== 2. Запуск REPL меню ==="
python src/repl.py