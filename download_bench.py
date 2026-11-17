#!/usr/bin/env python3
"""Простой бенчмарк загрузки: 10 последовательных запросов к URL.

Считает среднее время запроса, общий объём скачанных данных
и скорость скачивания (МБ/с). Во время скачивания показывает
прогресс и текущую скорость в реальном времени.
"""

import sys
import time

import requests

REQUESTS_COUNT = 10
CHUNK_SIZE = 256 * 1024  # 256 КБ


def format_speed(bytes_per_sec: float) -> str:
    if bytes_per_sec <= 0:
        return "—"
    if bytes_per_sec < 1024 * 1024:
        return f"{bytes_per_sec / 1024:8.1f} КБ/с"
    return f"{bytes_per_sec / (1024 * 1024):8.2f} МБ/с"


def main() -> None:
    if len(sys.argv) < 2:
        sys.exit("Использование: python download_bench.py <URL>")

    url = sys.argv[1]
    # Wikimedia и некоторые другие CDN отдают 403 на дефолтный User-Agent requests
    headers = {"User-Agent": "download-bench/1.0 (speed test)"}
    total_bytes = 0
    total_time = 0.0

    for i in range(1, REQUESTS_COUNT + 1):
        start = time.monotonic()
        response = requests.get(url, stream=True, headers=headers)
        response.raise_for_status()

        downloaded = 0
        # Дочитываем тело ответа до конца, считаем байты и рисуем прогресс
        for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
            downloaded += len(chunk)
            elapsed = time.monotonic() - start
            speed = downloaded / elapsed if elapsed > 0 else 0.0
            print(
                f"\r[{i:2d}/{REQUESTS_COUNT}] {downloaded / (1024 * 1024):8.2f} МБ"
                f" | {format_speed(speed)}",
                end="", flush=True,
            )

        elapsed = time.monotonic() - start
        total_bytes += downloaded
        total_time += elapsed
        avg_speed = downloaded / elapsed if elapsed > 0 else 0.0
        print(f"  ✓ за {elapsed:6.3f} с, средняя {format_speed(avg_speed)}")

    avg_time = total_time / REQUESTS_COUNT
    speed_mbps = (total_bytes / (1024 * 1024)) / total_time  # МБ/с

    print("-" * 50)
    print(f"Запросов:            {REQUESTS_COUNT}")
    print(f"Среднее время:       {avg_time:.3f} с")
    print(f"Всего скачано:       {total_bytes / (1024 * 1024):.2f} МБ")
    print(f"Скорость скачивания: {speed_mbps:.2f} МБ/с")


if __name__ == "__main__":
    main()