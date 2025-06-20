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
    try:
        data = response.json()
    except Exception as e:
        print(f"Failed to parse JSON from GitHub API: {e}")
        return []

    if response.status_code != 200:
        print(f"GitHub API error {response.status_code}: {data}")
        return []

    return data

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
    if response.status_code != 200:
        print(f"OpenAI API error: {response.status_code} - {response.text}")
        return "⚠️ AI Review failed to generate comment."
    return response.json()["choices"][0]["message"]["content"].strip()

def post_inline_comment(body, path, position):
    url = f"https://api.github.com/repos/{REPO}/pulls/{PR_NUMBER}/comments"
    payload = {
        "body": body,
        "commit_id": get_latest_commit_sha(),
        "path": path,
        "position": position
    }
    response = requests.post(url, headers=HEADERS, json=payload)
    if response.status_code != 201:
        print(f"Failed to post comment: {response.status_code} - {response.text}")

def get_latest_commit_sha():
    url = f"https://api.github.com/repos/{REPO}/pulls/{PR_NUMBER}"
    response = requests.get(url, headers=HEADERS)
    if response.status_code != 200:
        print(f"Failed to get latest commit SHA: {response.status_code} - {response.text}")
        return None
    return response.json()["head"]["sha"]

def main():
    files = get_changed_files()

    if not isinstance(files, list):
        print("Error: GitHub API did not return a list of files.")
        print(f"Response was: {files}")
        return

    for f in files:
        if not isinstance(f, dict):
            print(f"Unexpected file entry: {f}")
            continue

        if not f.get("filename", "").endswith((".kt", ".java")):
            continue

        hunk = f.get("patch", "")
        if hunk and f.get("status") in ["modified", "added"]:
            review = generate_review_comment(hunk, f["filename"])
            if review:
                post_inline_comment(review, f["filename"], position=1)

if __name__ == "__main__":
    main()
