import os
import requests
import json

# === CONFIG ===
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO = os.getenv("GITHUB_REPOSITORY")  # Format: owner/repo
PR_NUMBER = os.getenv("GITHUB_REF").split("/")[2]
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

HEADERS = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json"
}


def get_changed_files():
    url = f"https://api.github.com/repos/{REPO}/pulls/{PR_NUMBER}/files"
    print(f"[INFO] Fetching changed files from: {url}")
    response = requests.get(url, headers=HEADERS)
    if response.status_code != 200:
        print(f"[ERROR] GitHub API error {response.status_code}: {response.text}")
        return []
    return response.json()


def generate_review_comment(diff_hunk, filename):
    prompt = f"""
You're a senior Android reviewer. Carefully review this code diff from `{filename}`.
Check for deprecated APIs, performance bottlenecks, testability, and Android best practices.

Return only constructive inline comments (like a helpful engineer). Avoid generic feedback.
Use concise bullet points when possible.

Diff:
{diff_hunk}
"""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"
    headers = {"Content-Type": "application/json"}
    data = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ]
    }
    response = requests.post(url, headers=headers, data=json.dumps(data))
    if response.status_code == 200:
        result = response.json()
        comment = result.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
        return comment.strip() or "⚠️ No useful feedback was generated."
    else:
        print(f"[ERROR] Gemini API error {response.status_code}: {response.text}")
        return "⚠️ Gemini API error."

# Minimal test for Gemini API integration
if __name__ == "__main__":
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"
    headers = {"Content-Type": "application/json"}
    data = {
        "contents": [
            {
                "parts": [
                    {"text": "Explain how AI works in a few words"}
                ]
            }
        ]
    }
    response = requests.post(url, headers=headers, data=json.dumps(data))
    if response.status_code == 200:
        result = response.json()
        print("Gemini API test response:")
        print(result.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", ""))
    else:
        print(f"[ERROR] Gemini API error {response.status_code}: {response.text}")


def get_latest_commit_sha():
    url = f"https://api.github.com/repos/{REPO}/pulls/{PR_NUMBER}"
    response = requests.get(url, headers=HEADERS)
    if response.status_code != 200:
        print(f"[ERROR] Failed to get latest commit SHA: {response.status_code} - {response.text}")
        return None
    return response.json()["head"]["sha"]


def post_inline_comment(body, path, position):
    sha = get_latest_commit_sha()
    if not sha:
        return
    url = f"https://api.github.com/repos/{REPO}/pulls/{PR_NUMBER}/comments"
    payload = {
        "body": body,
        "commit_id": sha,
        "path": path,
        "position": position
    }
    print(f"[INFO] Posting comment to {path} at position {position}")
    response = requests.post(url, headers=HEADERS, json=payload)
    if response.status_code != 201:
        print(f"[ERROR] Failed to post comment: {response.status_code} - {response.text}")
    else:
        print(f"[INFO] Comment posted on {path}")


def main():
    print("[INFO] Starting AI code review process...")
    files = get_changed_files()
    if not files:
        print("[INFO] No changed files found.")
        return

    for f in files:
        filename = f.get("filename", "")
        status = f.get("status", "")
        hunk = f.get("patch", "")

        print(f"[INFO] Processing file: {filename} (status: {status})")

        if not filename.endswith((".kt", ".java")):
            print(f"[INFO] Skipping non-Kotlin/Java file: {filename}")
            continue

        if hunk and status in ["modified", "added"]:
            comment = generate_review_comment(hunk, filename)
            post_inline_comment(comment, filename, position=1)


if __name__ == "__main__":
    main()
