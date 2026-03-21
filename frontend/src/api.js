// API base URL - adjust if your backend runs on a different port
const API_BASE_URL = 'http://localhost:8000';

/**
 * Fetch commit analysis data for a repository
 * @param {string} owner - Repository owner
 * @param {string} repo - Repository name
 * @returns {Promise<Object>} Commit analysis data
 */
export async function fetchCommitData(owner, repo) {
    const response = await fetch(`${API_BASE_URL}/commits/${owner}/${repo}`);

    if (!response.ok) {
        throw new Error(`Failed to fetch data: ${response.statusText}`);
    }

    return response.json();
}
export const fetchContributors = async (owner, repo) => {
    const response = await fetch(
        `http://127.0.0.1:8000/contributors/${owner}/${repo}`
    );

    if (!response.ok) {
        throw new Error("Failed to fetch contributor data");
    }

    return response.json();
};

export async function fetchRepoOverview(owner, repo) {
    const response = await fetch(
        `http://127.0.0.1:8000/repo/overview/${owner}/${repo}`
    );

    if (!response.ok) {
        throw new Error("Failed to fetch repository overview");
    }

    return await response.json();
}
export async function fetchRepoStructure(owner, repo) {
    const response = await fetch(
        `http://127.0.0.1:8000/repo/structure/${owner}/${repo}`
    );

    if (!response.ok) {
        throw new Error("Failed to fetch repository structure");
    }

    return await response.json();
}

export async function fetchFileContent(owner, repo, path) {
    const response = await fetch(
        `http://127.0.0.1:8000/repo/file/${owner}/${repo}?path=${encodeURIComponent(path)}`
    );

    if (!response.ok) {
        throw new Error("Failed to fetch file content");
    }

    return await response.json();
}