import os
import httpx
import json
# from prompt_builder import PromptBuilder
from file_analyzer import FileAnalyzer, load_prompt_template
from dotenv import load_dotenv

load_dotenv()


api_key = os.getenv("OPENAI_API_KEY")



class ReadmeGenerator:
    def __init__(self, repo_data):
        self.repo_data = repo_data
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.readme_prompt = load_prompt_template("templates/readme_generation_prompt.txt")

    async def generate_readme(self):
        file_analyzer = FileAnalyzer(self.api_key)

        analyzed_data = []
        for path, content in self.repo_data.files.items():
            if not content.strip():
                continue
            print(f"Analyzing {path}")
            try:
                file_summary = await file_analyzer.analyze_file(path, content)
                analyzed_data.append(file_summary)
            except Exception as e:
                print(f"Failed to analyze {path}: {e}")
        print("here now")

        prompt = self.readme_prompt + f"file_summaries:, {json.dumps(analyzed_data, indent=2)}"
        print(prompt)
        return await self._ask_openai(prompt)

    async def _ask_openai(self, prompt: str) -> str:
        print("📤 Sending prompt to OpenAI...")
        async with httpx.AsyncClient(timeout=180) as client:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }

            payload = {
                "model": "gpt-4",
                "messages": [
                    {"role": "system", "content": "You are a professional enterprise documentation assistant."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.5,
                "max_tokens": 4096
            }

            try:
                response = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers=headers,
                    json=payload
                )
                response.raise_for_status()
            except httpx.HTTPStatusError as e:
                print("❌ OpenAI API returned an error:")
                print(f"Status Code: {e.response.status_code}")
                print(f"Response Text: {e.response.text}")
                raise
            except httpx.RequestError as e:
                print(f"❌ Request failed: {e}")
                raise

            try:
                json_data = response.json()
                print("✅ OpenAI response received.")
                return json_data["choices"][0]["message"]["content"].strip()
            except Exception as e:
                print("❌ Failed to parse OpenAI response JSON.")
                print(f"Raw response text:\n{response.text}")
                raise


