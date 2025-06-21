import os
import requests
import json
import sys

# Debug flag
DEBUG = True

def debug_log(msg):
    if DEBUG:
        print(f"[DEBUG] {msg}")

# === CONFIG ===
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
if not GITHUB_TOKEN:
    print("[ERROR] GITHUB_TOKEN is not set!", file=sys.stderr)
    exit(1)
else:
    debug_log(f"GITHUB_TOKEN starts with: {GITHUB_TOKEN[:6]}... (length: {len(GITHUB_TOKEN)})")

REPO = os.getenv("GITHUB_REPOSITORY")  # Format: owner/repo
if not REPO:
    print("[ERROR] GITHUB_REPOSITORY is not set!", file=sys.stderr)
    exit(1)
else:
    debug_log(f"GITHUB_REPOSITORY: {REPO}")

PR_NUMBER = os.getenv("GITHUB_REF").split("/")[2]
if not PR_NUMBER:
    print("[ERROR] GITHUB_REF is not set or not in the correct format!", file=sys.stderr)
    exit(1)
else:
    debug_log(f"GITHUB_REF: {PR_NUMBER}")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    print("[ERROR] GEMINI_API_KEY is not set!", file=sys.stderr)
    exit(1)
else:
    debug_log(f"GEMINI_API_KEY starts with: {GEMINI_API_KEY[:6]}... (length: {len(GEMINI_API_KEY)})")

HEADERS = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json"
}
debug_log(f"HEADERS: {HEADERS}")


def get_changed_files():
    url = f"https://api.github.com/repos/{REPO}/pulls/{PR_NUMBER}/files"
    print(f"[INFO] Fetching changed files from: {url}")
    response = requests.get(url, headers=HEADERS)
    if response.status_code != 200:
        print(f"[ERROR] GitHub API error {response.status_code}: {response.text}")
        return []
    return response.json()


def clean_gemini_comment(comment):
    """
    Clean and format Gemini's response for GitHub inline comments.
    - Trims whitespace
    - Limits length to 650 chars
    - Removes excessive blank lines
    """
    comment = comment.strip()
    comment = '\n'.join([line.rstrip() for line in comment.splitlines() if line.strip() != ''])
    max_length = 650
    if len(comment) > max_length:
        comment = comment[:max_length] + "…"
    return comment

def generate_review_comment(diff_hunk, filename):
    prompt = f"""
You're a senior Android reviewer. Carefully review this code diff from `{filename}`.

- Only return specific, actionable, and concise inline review comments.
- Use clear markdown formatting for code, lists, or warnings.
- Avoid generic feedback. Focus on deprecated APIs, performance, testability, and Android best practices.
- Each comment should be suitable for direct posting as a GitHub inline review.
- If the diff is fine, return a short positive note.

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
    debug_log(f"Gemini API URL: {url}")
    debug_log(f"Request headers: {headers}")
    debug_log(f"Request data: {json.dumps(data)}")
    response = requests.post(url, headers=headers, data=json.dumps(data))
    debug_log(f"Response status: {response.status_code}")
    debug_log(f"Response text: {response.text}")
    if response.status_code == 200:
        result = response.json()
        comment = result.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
        comment = clean_gemini_comment(comment)
        debug_log(f"Extracted comment: {comment}")
        return comment or "⚠️ No useful feedback was generated."
    else:
        print(f"[ERROR] Gemini API error {response.status_code}: {response.text}")
        return "⚠️ Gemini API error."

# Minimal test for Gemini API integration
if __name__ == "__main__":
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
    debug_log(f"Gemini API URL: {url}")
    debug_log(f"Request headers: {headers}")
    debug_log(f"Request data: {json.dumps(data)}")
    response = requests.post(url, headers=headers, data=json.dumps(data))
    debug_log(f"Response status: {response.status_code}")
    debug_log(f"Response text: {response.text}")
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


def fetch_file_content(repo, path):
    url = f"https://api.github.com/repos/{repo}/contents/{path}"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        data = response.json()
        # If file is not binary
        if data.get('encoding') == 'base64':
            import base64
            return base64.b64decode(data['content']).decode('utf-8', errors='replace')
        else:
            return data.get('content', '')
    else:
        print(f"[ERROR] Could not fetch {path}: {response.status_code}")
        return ''

def generate_test_coverage_comment(source_code, test_code, source_filename, test_filename):
    prompt = f"""
You are an expert software reviewer. Analyze the following source code and its unit tests.

Source file: {source_filename}
---
{source_code}

Test file: {test_filename}
---
{test_code}

List any important test scenarios that are missing or weakly covered. Format your answer as a markdown bullet list suitable for a GitHub code review comment. If all important scenarios are covered, reply with a short positive note.
"""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"
    headers = {"Content-Type": "application/json"}
    data = {"contents": [{"parts": [{"text": prompt}]}]}
    debug_log(f"[Coverage] Gemini prompt: {prompt[:200]}...")
    response = requests.post(url, headers=headers, data=json.dumps(data))
    debug_log(f"[Coverage] Response status: {response.status_code}")
    debug_log(f"[Coverage] Response text: {response.text}")
    if response.status_code == 200:
        result = response.json()
        comment = result.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
        comment = clean_gemini_comment(comment)
        return comment
    else:
        print(f"[ERROR] Gemini API error {response.status_code}: {response.text}")
        return None

def post_pr_comment(body):
    url = f"https://api.github.com/repos/{REPO}/issues/{PR_NUMBER}/comments"
    payload = {"body": body}
    response = requests.post(url, headers=HEADERS, json=payload)
    if response.status_code != 201:
        print(f"[ERROR] Failed to post PR comment: {response.status_code} - {response.text}")
    else:
        print(f"[INFO] PR summary comment posted.")

def main():
    print("[INFO] Starting AI code review process...")
    files = get_changed_files()
    if not files:
        print("[INFO] No changed files found.")
        return

    test_file_exts = ("Test.kt", "Test.java", "_test.py", "test_", "Test.py")
    coverage_comments = []

    for f in files:
        filename = f.get("filename", "")
        status = f.get("status", "")
        hunk = f.get("patch", "")

        print(f"[INFO] Processing file: {filename} (status: {status})")

        # --- Regular code review for Kotlin/Java ---
        if filename.endswith((".kt", ".java")) and not filename.endswith(test_file_exts):
            if hunk and status in ["modified", "added"]:
                comment = generate_review_comment(hunk, filename)
                post_inline_comment(comment, filename, position=1)

        # --- Test coverage analysis ---
        if filename.endswith(test_file_exts):
            test_code = fetch_file_content(REPO, filename)
            # Try to infer the source file path
            if filename.endswith("Test.kt"):
                source_filename = filename.replace("Test.kt", ".kt").replace("/test/", "/main/")
            elif filename.endswith("Test.java"):
                source_filename = filename.replace("Test.java", ".java").replace("/test/", "/main/")
            elif filename.endswith("_test.py"):
                source_filename = filename.replace("_test.py", ".py")
            elif filename.endswith("Test.py"):
                source_filename = filename.replace("Test.py", ".py")
            elif filename.startswith("test_") and filename.endswith(".py"):
                source_filename = filename.replace("test_", "", 1)
            else:
                source_filename = None
            source_code = fetch_file_content(REPO, source_filename) if source_filename else ''
            if source_code:
                coverage_comment = generate_test_coverage_comment(source_code, test_code, source_filename, filename)
                if coverage_comment and not any(x in coverage_comment.lower() for x in ["all important scenarios are covered", "no missing test"]):
                    coverage_comments.append(f"**Test coverage review for `{filename}`:**\n{coverage_comment}")

    # Post summary comment if any missing/weak coverage is found
    if coverage_comments:
        summary = "\n\n".join(coverage_comments)
        post_pr_comment(summary)



if __name__ == "__main__":
    main()
