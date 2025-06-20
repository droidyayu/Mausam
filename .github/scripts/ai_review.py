import os
import requests
import base64

# Load tokens and metadata
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
REPO = os.getenv("GITHUB_REPOSITORY")  # e.g. "username/repo"
PR_NUMBER = os.getenv("GITHUB_REF").split("/")[-1]

HEADERS = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json"
}

def get_changed_files():
    url = f"https://api.github.com/repos/{REPO}/pulls/{PR_NUMBER}/files"
    response = requests.get(url, headers=HEADERS)
    return response.json()

def generate_review_comment(diff_hunk, filename):
    prompt = f"""
You're a senior Kotlin/Java reviewer. Review this diff in file `{filename}`.
Look for: deprecated APIs, performance issues, best practices, and suggest improvements.
Use a constructive, friendly tone like a helpful team member. Format the answer concisely.

Here’s the code diff:
{diff_hunk}
"""
    response = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": "gpt-4",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.4
        }
    )
    return response.json()["choices"][0]["message"]["content"].strip()

def post_inline_comment(body, path, position):
    url = f"https://api.github.com/repos/{REPO}/pulls/{PR_NUMBER}/comments"
    payload = {
        "body": body,
        "commit_id": get_latest_commit_sha(),
        "path": path,
        "position": position
    }
    requests.post(url, headers=HEADERS, json=payload)

def get_latest_commit_sha():
    url = f"https://api.github.com/repos/{REPO}/pulls/{PR_NUMBER}"
    response = requests.get(url, headers=HEADERS)
    return response.json()["head"]["sha"]

def main():
    files = get_changed_files()
    for f in files:
        if not f["filename"].endswith((".kt", ".java")):
            continue

        hunk = f.get("patch", "")
        if hunk and f.get("status") in ["modified", "added"]:
            review = generate_review_comment(hunk, f["filename"])
            # Place at top of hunk (line 1 of patch)
            post_inline_comment(review, f["filename"], position=1)

if __name__ == "__main__":
    main()
