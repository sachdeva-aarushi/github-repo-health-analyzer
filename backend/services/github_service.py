import os
import time
import requests
from typing import List, Dict, Optional, Any
from dotenv import load_dotenv
from utils.cache import global_cache

# Load .env from project root (two levels up from backend/services/)
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '..', '.env'))

# GitHub API base URL
GITHUB_API_BASE = "https://api.github.com"

def _get_headers() -> Dict[str, str]:
    """Build request headers, including auth token if available."""
    headers = {"Accept": "application/vnd.github.v3+json"}
    token = os.getenv("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"token {token}"
    return headers


def _fetch_github_api(url: str, params: Dict = None, cache_key: str = None) -> Any:
    """
    Unified fetch function for all GitHub API requests.
    Supports caching, request deduplication, and structured rate-limit logging.
    """
    if not cache_key:
        cache_key = f"github_api:{url}:{str(params)}"

    def do_fetch():
        start_time = time.time()
        headers = _get_headers()
        try:
            response = requests.get(url, params=params, headers=headers, timeout=15)
            duration = time.time() - start_time
            
            # Extract rate limit headers
            limit = response.headers.get("X-RateLimit-Limit")
            remaining = response.headers.get("X-RateLimit-Remaining")
            reset = response.headers.get("X-RateLimit-Reset")
            
            # Print rate limit diagnostic logs
            print(f"[GitHub API] Fetch: {url} | Params: {params} | Status: {response.status_code} | "
                  f"Duration: {duration:.3f}s | Limit: {limit} | Remaining: {remaining} | Reset: {reset}")
            
            # Detect rate limiting
            if response.status_code == 403 and "rate limit" in response.text.lower():
                print("Rate Limit Error: GitHub API rate limit exceeded. "
                      "Set a GITHUB_TOKEN in .env to increase your limit.")
                response.raise_for_status()

            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"[GitHub API] Error fetching {url}: {e}")
            raise e

    is_hit = [True]
    def on_cache_hit():
        is_hit[0] = True
        print(f"[GitHub API] Cache HIT: {url} | Params: {params}")

    is_hit[0] = False
    
    try:
        data = global_cache.get_or_fetch(
            key=cache_key,
            fetch_fn=do_fetch,
            cache_hit_callback=on_cache_hit
        )
        if not is_hit[0]:
            print(f"[GitHub API] Cache MISS: {url} | Params: {params}")
        return data
    except Exception:
        return None


def run_startup_validation() -> Dict[str, Any]:
    """
    Performs startup verification of GITHUB_TOKEN and rate limit status.
    Prints a clear diagnostic report to the console.
    """
    import sys
    token = os.getenv("GITHUB_TOKEN")
    print("\n" + "="*50)
    print(" GITINTEL STARTUP VALIDATION: GITHUB AUTHENTICATION")
    print("="*50)
    sys.stdout.flush()
    
    if not token:
        print("[WARNING] GITHUB_TOKEN is missing in the environment or .env file.")
        print("[WARNING] Requests will be unauthenticated and limited to 60 requests/hour.")
        print("="*50 + "\n")
        sys.stdout.flush()
        return {
            "status": "missing",
            "authenticated": False,
            "rate_limit": 60,
            "message": "Token is missing"
        }
        
    url = f"{GITHUB_API_BASE}/rate_limit"
    try:
        response = requests.get(url, headers=_get_headers(), timeout=10)
        if response.status_code == 401:
            print("[ERROR] GITHUB_TOKEN was loaded but is INVALID (Authentication Failure).")
            print("[ERROR] GitHub API returned 401 Unauthorized.")
            print("="*50 + "\n")
            sys.stdout.flush()
            return {
                "status": "invalid",
                "authenticated": False,
                "message": "Token is invalid (401 Unauthorized)"
            }
            
        response.raise_for_status()
        data = response.json()
        core = data.get("resources", {}).get("core", {})
        limit = core.get("limit", 60)
        remaining = core.get("remaining", 0)
        
        if limit >= 5000:
            print("[SUCCESS] GITHUB_TOKEN loaded successfully!")
            print(f"[SUCCESS] Authenticated Rate Limit: {limit} requests/hour (Authenticated).")
            print(f"[STATUS] Remaining requests: {remaining}/{limit}")
            print("="*50 + "\n")
            sys.stdout.flush()
            return {
                "status": "valid",
                "authenticated": True,
                "rate_limit": limit,
                "remaining": remaining,
                "message": "Token is valid and authenticated"
            }
        else:
            print("[WARNING] Token was accepted but rate limit is unexpectedly low.")
            print(f"[WARNING] Rate Limit: {limit} requests/hour (Possibly unauthenticated).")
            print("="*50 + "\n")
            sys.stdout.flush()
            return {
                "status": "low_limit",
                "authenticated": False,
                "rate_limit": limit,
                "message": "Token is valid but limit is low"
            }
            
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Failed to connect to GitHub API during startup validation: {e}")
        print("="*50 + "\n")
        sys.stdout.flush()
        return {
            "status": "connection_error",
            "authenticated": False,
            "message": f"Connection error: {e}"
        }



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
    cache_key = f"github:commits:{owner}:{repo}:{per_page}"
    return _fetch_github_api(url, params, cache_key)


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
    url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/contributors"
    params = {"per_page": 100}
    cache_key = f"github:contributors:{owner}:{repo}"
    return _fetch_github_api(url, params, cache_key)


def get_repo_metadata(owner: str, repo: str):
    url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}"
    cache_key = f"github:metadata:{owner}:{repo}"
    return _fetch_github_api(url, {}, cache_key)


def get_pull_requests(owner: str, repo: str):
    url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/pulls"
    params = {"state": "all", "per_page": 100}
    cache_key = f"github:pulls:{owner}:{repo}"
    return _fetch_github_api(url, params, cache_key)

def get_repo_languages(owner: str, repo: str):
    url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/languages"
    cache_key = f"github:languages:{owner}:{repo}"
    return _fetch_github_api(url, {}, cache_key)

def get_issues(owner: str, repo: str):
    url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/issues"
    params = {"state": "all", "per_page": 100}
    cache_key = f"github:issues:{owner}:{repo}"
    return _fetch_github_api(url, params, cache_key)


def get_repo_tree(owner: str, repo: str):
    repo_data = get_repo_metadata(owner, repo)
    if not repo_data:
        return {"tree": []}
    default_branch = repo_data.get("default_branch", "main")
    url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/git/trees/{default_branch}"
    params = {"recursive": 1}
    cache_key = f"github:tree:{owner}:{repo}:{default_branch}"
    return _fetch_github_api(url, params, cache_key)

def get_file_content(owner: str, repo: str, path: str):
    url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/contents/{path}"
    cache_key = f"github:file:{owner}:{repo}:{path}"
    return _fetch_github_api(url, {}, cache_key)
