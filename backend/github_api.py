import requests
from typing import List, Dict, Optional

# GitHub API base URL
GITHUB_API_BASE = "https://api.github.com"

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
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()  # Raise exception for 4xx/5xx status codes
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
