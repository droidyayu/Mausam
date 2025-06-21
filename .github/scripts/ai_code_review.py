import os
import requests
from vertexai.preview.language_models import TextGenerationModel
from vertexai.preview import vertex_ai

# Initialize Vertex AI
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "ai-code-review-463612")
LOCATION = os.getenv("GOOGLE_CLOUD_REGION", "europe-west3")
vertex_ai.init(project=PROJECT_ID, location=LOCATION)

# Load GitHub info from environment
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO = os.getenv("GITHUB_REPOSITORY")  # e.g. "username/repo"
PR_NUMBER = os.getenv("GITHUB_REF", "").split("/")[-1]  # Extract PR number from ref

HEADERS = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json"
}

def get_changed_files():
    url = f"https://api.github.com/repos/{REPO}/pulls/{PR_NUMBER}/files"
    print(f"[INFO] Fetching changed files from: {url}")
    response = requests.get(url, headers=HEADERS)

    try:
        data = response.json()
    except Exception as e:
        print(f"[ERROR] Failed to parse JSON from GitHub API: {e}")
        return []

    if response.status_code != 200:
        print(f"[ERROR] GitHub API error {response.status_code}: {data}")
        return []

    print(f"[INFO] Files fetched: {[f.get('filename') for f in data]}")
    return data

def generate_review_comment(diff_hunk, filename):
    print(f"[INFO] Generating review for {filename}")
    prompt = f"""
You're a senior Kotlin/Java reviewer. Review this diff in file `{filename}`.
Look for: deprecated APIs, performance issues, best practices, and suggest improvements.
Use a constructive, friendly tone like a helpful team member. Format the answer concisely.

Here’s the code diff:
{diff_hunk}
"""

    model = TextGenerationModel.from_pretrained("gemini-ultra-1")  # or your preferred Gemini model
    response = model.predict(
        prompt,
        max_output_tokens=1024,
        temperature=0.4,
        top_p=0.8,
    )

    comment = response.text.strip()
    print(f"[INFO] Review comment generated for {filename}")
    return comment

def get_latest_commit_sha():
    url = f"https://api.github.com/repos/{REPO}/pulls/{PR_NUMBER}"
    print(f"[INFO] Fetching latest commit SHA from: {url}")
    response = requests.get(url, headers=HEADERS)

    if response.status_code != 200:
        print(f"[ERROR] Failed to get latest commit SHA: {response.status_code} - {response.text}")
        return None

    sha = response.json()["head"]["sha"]
    print(f"[INFO] Latest commit SHA: {sha}")
    return sha

def post_inline_comment(body, path, position):
    commit_sha = get_latest_commit_sha()
    if not commit_sha:
        print("[ERROR] Skipping comment post due to missing commit SHA.")
        return

    url = f"https://api.github.com/repos/{REPO}/pulls/{PR_NUMBER}/comments"
    payload = {
        "body": body,
        "commit_id": commit_sha,
        "path": path,
        "position": position
    }

    print(f"[INFO] Posting comment to {path} at position {position}")
    response = requests.post(url, headers=HEADERS, json=payload)

    if response.status_code != 201:
        print(f"[ERROR] Failed to post comment: {response.status_code} - {response.text}")
    else:
        print(f"[INFO] Comment posted successfully on {path}")

def main():
    print("[INFO] Starting AI code review process...")
    files = get_changed_files()

    if not isinstance(files, list):
        print("[ERROR] GitHub API did not return a list of files.")
        print(f"[DEBUG] Response was: {files}")
        return

    for f in files:
        if not isinstance(f, dict):
            print(f"[WARNING] Unexpected file entry: {f}")
            continue

        filename = f.get("filename", "")
        status = f.get("status", "")
        hunk = f.get("patch", "")

        print(f"[INFO] Processing file: {filename} (status: {status})")

        if not filename.endswith((".kt", ".java")):
            print(f"[INFO] Skipping non-Kotlin/Java file: {filename}")
            continue

        if hunk and status in ["modified", "added"]:
            review = generate_review_comment(hunk, filename)
            if review:
                post_inline_comment(review, filename, position=1)

if __name__ == "__main__":
    main()
