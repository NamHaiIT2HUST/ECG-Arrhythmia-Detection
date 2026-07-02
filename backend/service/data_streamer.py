import csv
import asyncio
import os
from core.config import settings # Gọi setting từ core

async def ecg_file_reader(filepath=settings.MOCK_DATA_PATH, delay_ms=100):
    if not os.path.exists(filepath):
        yield 0.0
        return

    while True:
        with open(filepath, mode='r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                yield float(row["value"])
                await asyncio.sleep(delay_ms / 1000.0)