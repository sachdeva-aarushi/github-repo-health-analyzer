from fastapi import APIRouter,Query, HTTPException
from services.github_service import get_repo_tree, get_file_content
import requests
from utils.helpers import build_tree_structure
from analysis.evolution_analysis import summarize_structure

router = APIRouter(
    prefix="/repo",
    tags=["Repository Structure"]
)

from utils.cache import global_cache

@router.get("/structure/{owner}/{repo}")
def get_structure(owner: str, repo: str):
    cache_key = f"endpoint:structure:{owner.lower()}:{repo.lower()}"
    
    def fetch():
        tree_data = get_repo_tree(owner, repo)

        structure = summarize_structure(tree_data)
        tree = build_tree_structure(tree_data)

        return {
            "repository": f"{owner}/{repo}",
            "total_files": structure["total_files"],
            "total_folders": structure["total_folders"],
            "tree": tree
        }

    return global_cache.get_or_fetch(cache_key, fetch)



@router.get("/file/{owner}/{repo}")
def get_file(owner: str, repo: str, path: str = Query(...)):

    file_data = get_file_content(owner, repo, path)

    return {
        "name": file_data.get("name"),
        "path": file_data.get("path"),
        "content": file_data.get("content"),
        "encoding": file_data.get("encoding")
    }