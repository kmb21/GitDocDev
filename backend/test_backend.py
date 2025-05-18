# test_backend.py

import requests

# Local server address
URL = "http://localhost:8000/generate-readme"

# Static test repo
repo_url = "https://github.com/kmb21/Railway-Rout-building-game"  # You can change this to any public GitHub repo

response = requests.post(URL, json={"repo_url": repo_url})

if response.ok:
    readme = response.json().get("readme", "")
    print("✅ README GENERATED:\n\n")
    print(readme)
else:
    print("❌ ERROR:")
    print(response.status_code)
    print(response.text)
