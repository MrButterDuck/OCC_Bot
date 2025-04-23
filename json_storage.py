import json
import os
from typing import Any


class JsonStorage:
    def __init__(self, filename: str = "data.json"):
        self.filename = filename
        self.data = self._load()

    def _load(self) -> dict:
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                print(
                    f"[WARNING] Файл {self.filename} поврежден."
                    "Создаю новый словарь."
                )
        return {}

    def save(self) -> None:
        with open(self.filename, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=4)

    def get(self, key: str, default: Any = None) -> Any:
        return self.data.get(str(key), default)

    def set(self, key: str, value: Any) -> None:
        self.data[str(key)] = value
        self.save()

    def delete(self, key: str) -> None:
        if key in self.data:
            del self.data[str(key)]
            self.save()

    def clear(self) -> None:
        self.data = {}
        self.save()

    def all(self) -> dict:
        return self.data
