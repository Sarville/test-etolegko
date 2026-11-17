#!/usr/bin/env python3
"""Бенчмарк скачивания с общим лимитом трафика и живой статистикой."""

import sys
import time

import requests

REQUESTS_COUNT = 10
MAX_DOWNLOAD_MB = 20  # Общий лимит скачанных данных за весь тест
CHUNK_SIZE = 64 * 1024  # 64 КиБ


def main() -> None:
    if len(sys.argv) != 2:
        sys.exit("Использование: python download_bench_v2.py <URL>")

    url = sys.argv[1]
    max_bytes = MAX_DOWNLOAD_MB * 1024 * 1024
    headers = {
        "User-Agent": "download-bench/2.0 (speed test)",
        "Accept-Encoding": "identity",
    }
    total_bytes = 0
    completed_requests = 0
    start = time.monotonic()

    try:
        for i in range(1, REQUESTS_COUNT + 1):
            if total_bytes >= max_bytes:
                break

            with requests.get(url, stream=True, headers=headers, timeout=(10, 30)) as response:
                response.raise_for_status()
                while total_bytes < max_bytes:
                    remaining = max_bytes - total_bytes
                    chunk = response.raw.read(min(CHUNK_SIZE, remaining), decode_content=True)
                    if not chunk:
                        break

                    total_bytes += len(chunk)
                    elapsed = time.monotonic() - start
                    average_speed = total_bytes / elapsed if elapsed > 0 else 0
                    print(
                        f"\rЗапрос {i}/{REQUESTS_COUNT} | "
                        f"Скачано: {total_bytes / (1024 * 1024):.2f} / {MAX_DOWNLOAD_MB} МБ | "
                        f"Средняя скорость: {average_speed / (1024 * 1024):.2f} МБ/с",
                        end="", flush=True,
                    )
            completed_requests += 1

    except requests.RequestException as exc:
        print(f"\nОшибка загрузки: {exc}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nТест остановлен пользователем.")

    elapsed = time.monotonic() - start
    print("\n" + "-" * 55)
    print(f"Запросов завершено: {completed_requests}")
    print(f"Всего скачано: {total_bytes / (1024 * 1024):.2f} МБ")
    print(f"Общее время: {elapsed:.2f} с")
    print(f"Средняя скорость: {total_bytes / elapsed / (1024 * 1024):.2f} МБ/с" if elapsed else "Средняя скорость: —")


if __name__ == "__main__":
    main()
