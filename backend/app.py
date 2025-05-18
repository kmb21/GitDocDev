from flask import Flask, request, jsonify
import asyncio
import os
from github_repo import GitHubRepo
from readme_generator import ReadmeGenerator

app = Flask(__name__)

@app.route('/generate-readme', methods=['POST'])
def generate_readme_endpoint():
    data = request.json
    repo_url = data.get('repo_url')

    if not repo_url or "github.com" not in repo_url:
        return jsonify({'error': 'Invalid or missing GitHub URL'}), 400

    try:
        url_parts = repo_url.strip('/').split('/')
        owner, repo = url_parts[-2], url_parts[-1]
        print(f"🔍 Processing repo: {owner}/{repo}")

        repo_data = GitHubRepo(owner, repo)
        repo_data.fetch_files()

        generator = ReadmeGenerator(repo_data)
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        readme = loop.run_until_complete(generator.generate_readme())
        loop.close()

        return jsonify({'readme': readme})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    from dotenv import load_dotenv
    load_dotenv()
    port = int(os.getenv('PORT', 8000))
    debug = os.getenv('FLASK_DEBUG', 'false').lower() == 'true'
    app.run(host='0.0.0.0', port=port, debug=debug)
