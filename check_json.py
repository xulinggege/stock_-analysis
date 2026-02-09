import json
import os

try:
    with open('stock_info_full.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
        print(f"Successfully loaded {len(data)} items.")
        print("Sample item:", data[0] if data else "Empty")
except Exception as e:
    print(f"Error loading json: {e}")
