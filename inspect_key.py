from backend.config import settings

key = settings.FULLENRICH_API_KEY
print(f"Key: '{key}'")
print(f"Length: {len(key)}")
print(f"Hex: {key.encode('utf-8').hex()}")
