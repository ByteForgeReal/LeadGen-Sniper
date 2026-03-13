import requests
import os
import sys
import json

# Configuration
REPO_OWNER = "ByteForgeReal"
REPO_NAME = "LeadGen-Sniper"
TAG_NAME = "v1.0.0"
RELEASE_NAME = "Professional Release v1.0.0"
BODY = "Professional standalone search & export engine for Google Maps leads. Includes standalone .exe for Windows."
ASSET_PATH = "dist/LeadGen-Sniper.exe"

def create_release(token):
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    # Check if release exists
    print(f"Checking for existing release {TAG_NAME}...")
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/releases/tags/{TAG_NAME}"
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        print(f"Release {TAG_NAME} already exists. Using existing release.")
        release_id = response.json()["id"]
        upload_url = response.json()["upload_url"].split("{")[0]
    else:
        print(f"Creating new release {TAG_NAME}...")
        url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/releases"
        data = {
            "tag_name": TAG_NAME,
            "name": RELEASE_NAME,
            "body": BODY,
            "draft": False,
            "prerelease": False
        }
        response = requests.post(url, headers=headers, json=data)
        if response.status_code != 201:
            print(f"Failed to create release: {response.text}")
            return
        release_id = response.json()["id"]
        upload_url = response.json()["upload_url"].split("{")[0]

    # Upload Asset
    print(f"Uploading {ASSET_PATH} to GitHub Releases...")
    if not os.path.exists(ASSET_PATH):
        print(f"Error: {ASSET_PATH} not found. Please run the build first.")
        return

    with open(ASSET_PATH, 'rb') as f:
        params = {"name": os.path.basename(ASSET_PATH)}
        headers["Content-Type"] = "application/octet-stream"
        upload_response = requests.post(
            upload_url, 
            headers=headers, 
            params=params, 
            data=f
        )
        
    if upload_response.status_code == 201:
        print(f"Successfully uploaded {ASSET_PATH}!")
        print(f"View it at: https://github.com/65{REPO_OWNER}/{REPO_NAME}/releases/tag/{TAG_NAME}")
    else:
        print(f"Failed to upload asset: {upload_response.text}")

if __name__ == "__main__":
    print("--- ByteForge Professional Release Tool ---")
    token = input("Enter your GitHub Personal Access Token (classic, with 'repo' scope): ").strip()
    if not token:
        print("Token is required.")
        sys.exit(1)
    
    try:
        create_release(token)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
