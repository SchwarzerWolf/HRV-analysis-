"""Запуск анализа командой python hrv/hrv_analysis.py или python -m hrv.hrv_analysis."""

import sys
from pathlib import Path

if __name__ == "__main__":
    # При запуске по пути Python ищет модули внутри hrv. Добавляем корень проекта.
    if not __package__:
        sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from hrv.analysis.pipeline import main

    main()
