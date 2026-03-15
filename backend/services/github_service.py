import os
import requests
from typing import List, Dict, Optional
from dotenv import load_dotenv

# Load .env from project root (one level up from backend/)
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

# GitHub API base URL
GITHUB_API_BASE = "https://api.github.com"

def _get_headers() -> Dict[str, str]:
    """Build request headers, including auth token if available."""
    headers = {"Accept": "application/vnd.github.v3+json"}
    token = os.getenv("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"token {token}"
    return headers


def get_commits(owner: str, repo: str, per_page: int = 100) -> Optional[List[Dict]]:
    """
    Fetch commits from a GitHub repository.

    Args:
        owner: Repository owner (username or organization)
        repo: Repository name
        per_page: Number of commits to fetch per page (max 100)

    Returns:
        List of commit data dictionaries, or None if request fails
    """
    url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/commits"
    params = {"per_page": per_page}

    try:
        response = requests.get(url, params=params, headers=_get_headers(), timeout=15)

        #Detect rate limiting
        if response.status_code == 403 and "rate limit" in response.text.lower():
            print("Rate Limit Error: GitHub API rate limit exceeded. "
                  "Set a GITHUB_TOKEN in .env to increase your limit.")
            return None

        response.raise_for_status()
        return response.json()

    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error: {e}")
        return None
    except requests.exceptions.ConnectionError:
        print("Connection Error: Could not connect to GitHub API")
        return None
    except requests.exceptions.Timeout:
        print("Timeout Error: Request took too long")
        return None
    except requests.exceptions.RequestException as e:
        print(f"Request Error: {e}")
        return None


def get_rate_limit() -> Optional[Dict]:
    """Return the current GitHub API rate-limit status."""
    url = f"{GITHUB_API_BASE}/rate_limit"
    try:
        response = requests.get(url, headers=_get_headers(), timeout=10)
        response.raise_for_status()
        data = response.json()
        core = data.get("resources", {}).get("core", {})
        return {
            "limit": core.get("limit"),
            "remaining": core.get("remaining"),
            "reset_at": core.get("reset"),
        }
    except requests.exceptions.RequestException:
        return None

def get_contributors(owner: str, repo: str):
    url = f"https://api.github.com/repos/{owner}/{repo}/contributors"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()
