import requests
import os
import base64
import json

class GitHubRepo:
    def __init__(self, owner, repo):
        self.owner = owner
        self.repo = repo
        self.api_base = f"https://api.github.com/repos/{owner}/{repo}"
        self.files = {}
        self.readme_content = None
        self.max_file_size = 1024 * 50
        self.max_chunk_size = 1024 * 15

    def fetch_files(self):
        contents_url = f"{self.api_base}/contents"
        all_paths = self._get_all_paths(contents_url)

        print("🔍 All file paths fetched:", all_paths)

        for path in all_paths:
            result = self._fetch_file(path)
            if result:
                print(f"✅ Successfully fetched content of: {path}")
                self.files[path] = result

        for path in self.files:
            if path.lower() == "readme.md":
                self.readme_content = self.files[path]
                break

        return self.files

    def _get_all_paths(self, url, path=""):
        headers = {}
        if github_token := os.getenv("GITHUB_TOKEN"):
            headers["Authorization"] = f"token {github_token}"

        response = requests.get(url, headers=headers)
        response.raise_for_status()
        items = response.json()
        print(f"📦 JSON returned for {url}:\n", json.dumps(items, indent=2))
        paths = []
        dirs = []

        for item in items:
            item_path = os.path.join(path, item["name"]) if path else item["name"]
            if item["type"] == "file" and self._is_relevant_file(item_path):
                paths.append(item_path)
            elif item["type"] == "dir":
                dirs.append((item["url"], item_path))

        for dir_url, dir_path in dirs:
            paths.extend(self._get_all_paths(dir_url, dir_path))

        return paths

    def _is_relevant_file(self, path):
        return True
        extensions = ['.py', '.js', '.ts', '.html', '.css', '.md', '.json',
                      '.yaml', '.yml', '.toml', '.java', '.go', '.rs', '.c',
                      '.cpp', '.h', '.hpp', '.sh', '.txt']
        return any(path.lower().endswith(ext) for ext in extensions) or path.lower() in ['dockerfile', 'license', 'requirements.txt', 'package.json']

    def _fetch_file(self, path):
        url = f"{self.api_base}/contents/{path}"
        headers = {}
        if github_token := os.getenv("GITHUB_TOKEN"):
            headers["Authorization"] = f"token {github_token}"

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            if data.get("encoding") == "base64" and data.get("content"):
                content = base64.b64decode(data["content"]).decode('utf-8', errors='replace')
                return content
        except Exception as e:
            print(f"❌ Error fetching file {path}: {e}")
        return None