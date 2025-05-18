import json

class PromptBuilder:
    def __init__(self, repo_data):
        self.repo_data = repo_data
        self.max_tokens = 16000
        self.token_estimate_factor = 1.5

    def _estimate_tokens(self, text):
        return int(len(text) / 4 * self.token_estimate_factor)

    def _get_file_language(self, filename):
        ext_map = {'py': 'python', 'js': 'javascript', 'ts': 'typescript', 'html': 'html', 'css': 'css',
                   'md': 'markdown', 'json': 'json', 'yml': 'yaml', 'yaml': 'yaml', 'java': 'java',
                   'go': 'go', 'rs': 'rust', 'c': 'c', 'cpp': 'cpp', 'h': 'c', 'hpp': 'cpp', 'sh': 'bash'}
        ext = filename.split('.')[-1].lower() if '.' in filename else ''
        return ext_map.get(ext, '')
        
    def _load_base_prompt(self):
        with open("templates/readme_prompt_template.txt", "r", encoding="utf-8") as f:
            return f.read()


    def build_prompt(self):
        files = self.repo_data.files
        base_prompt = self._load_base_prompt()

        if not files:
            print("⚠️ No files found in repository.")
            return "No code files or structure found in the repository."

        file_tree = "\n".join(sorted(files.keys()))
        prompt = base_prompt + f"## File Tree:\n```text\n{file_tree}\n```\n\n" "## File Contents:\n"

        content_blocks = []
        current_tokens = self._estimate_tokens(prompt)

        for file_path, content in files.items():
            print(f"📄 Adding file to prompt: {file_path}")
            if not content:
                continue
            if len(content) > 3000:
                content = content[:3000] + "\n... (content truncated)"
            lang = self._get_file_language(file_path)
            block = f"\n### File: {file_path}\n```{lang}\n{content}\n```"
            block_tokens = self._estimate_tokens(block)
            if current_tokens + block_tokens < self.max_tokens:
                content_blocks.append(block)
                current_tokens += block_tokens
            else:
                print(f"⚠️ Skipping {file_path} due to token limit.")
                break

        prompt += "\n".join(content_blocks)
        prompt += "\n\nReturn only the README.md markdown content."
        return prompt