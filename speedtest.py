#!/usr/bin/env python3
"""Замер скорости скачивания: N последовательных запросов к одному URL."""
import argparse
import sys
import time
import urllib.request

DEFAULT_URL = "https://speed.cloudflare.com/__down?bytes=5000000"
CHUNK = 64 * 1024


def fetch(url: str, timeout: float) -> tuple[int, float]:
    """Скачивает ответ целиком, возвращает (байты, секунды)."""
    req = urllib.request.Request(url, headers={"User-Agent": "speedtest-cli/1.0"})
    start = time.perf_counter()
    total = 0
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        while chunk := resp.read(CHUNK):
            total += len(chunk)
    return total, time.perf_counter() - start


def main() -> int:
    ap = argparse.ArgumentParser(description="Замер скорости скачивания")
    ap.add_argument("url", nargs="?", default=DEFAULT_URL, help="адрес для запросов")
    ap.add_argument("-n", "--requests", type=int, default=10, help="число запросов (10)")
    ap.add_argument("-t", "--timeout", type=float, default=30, help="таймаут запроса, сек")
    args = ap.parse_args()

    total_bytes = 0
    total_time = 0.0
    times = []
    for i in range(1, args.requests + 1):
        try:
            size, sec = fetch(args.url, args.timeout)
        except Exception as e:
            print(f"запрос {i}: ошибка: {e}", file=sys.stderr)
            continue
        total_bytes += size
        total_time += sec
        times.append(sec)
        print(f"запрос {i}: {size} байт за {sec:.3f} с")

    if not times:
        print("ни один запрос не удался", file=sys.stderr)
        return 1

    avg = total_time / len(times)
    mb = total_bytes / 1_000_000
    print(f"\nуспешных запросов: {len(times)} из {args.requests}")
    print(f"среднее время запроса: {avg:.3f} с")
    print(f"скачано всего: {mb:.2f} МБ")
    print(f"скорость: {mb / total_time:.2f} МБ/с ({mb * 8 / total_time:.2f} Мбит/с)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
