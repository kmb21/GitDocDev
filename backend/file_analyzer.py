import json
import httpx
import re
from typing import List

def extract_json_block(text: str) -> str:
    """Extract valid JSON from GPT response, even if wrapped in markdown."""
    match = re.search(r"```json\s*(.*?)\s*```", text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return text.strip()

def load_prompt_template(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def split_into_chunks(content: str, chunk_size: int = 2000) -> List[str]:
    return [content[i:i + chunk_size] for i in range(0, len(content), chunk_size)]

class FileAnalyzer:
    def __init__(self, api_key):
        self.api_key = api_key
        self.file_prompt_template = load_prompt_template("templates/file_analysis_prompt.txt")

    async def analyze_file(self, file_path: str, content: str) -> dict:
        """Process a single file in chunks and combine analysis results into one summary."""
        chunks = split_into_chunks(content)
        summaries = []

        for i, chunk in enumerate(chunks):
            prompt = self.file_prompt_template + f"content:, {chunk}"
            print(prompt)
            try:
                async with httpx.AsyncClient(timeout=120) as client:
                    headers = {
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    }

                    payload = {
                        "model": "gpt-4",
                        "messages": [
                            {
                                "role": "system",
                                "content": "You are a code analysis assistant. Extract structured JSON info from the following chunk of code."
                            },
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ],
                        "temperature": 0,
                        "max_tokens": 1500
                    }

                    response = await client.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
                    response.raise_for_status()
                    print(response.json())
                    raw = response.json()["choices"][0]["message"]["content"]
                    json_part = extract_json_block(raw)
                    summaries.append(json.loads(json_part))
            except Exception as e:
                print(f"Failed to analyze chunk {i + 1}/{len(chunks)} of {file_path}: {e}")
        return {
            "file": file_path,
            "chunk_count": len(summaries),
            "chunks": summaries
        }
