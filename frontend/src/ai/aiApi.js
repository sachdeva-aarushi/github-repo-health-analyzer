const API_BASE_URL = 'http://127.0.0.1:8000';

/**
 * Fetch AI generated summary for a repository
 * @param {string} owner - Repository owner
 * @param {string} repo - Repository name
 * @returns {Promise<Object>} AI summary response
 */
export async function fetchAISummary(owner, repo) {
    const response = await fetch(`${API_BASE_URL}/ai/summary`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ owner, repo })
    });

    if (!response.ok) {
        throw new Error(`Failed to fetch AI summary: ${response.statusText}`);
    }

    return response.json();
}

/**
 * Ask the AI a specific question about the repository
 * @param {string} owner - Repository owner
 * @param {string} repo - Repository name
 * @param {string} question - Question to ask
 * @returns {Promise<Object>} AI answer response
 */
export async function askRepositoryQuestion(owner, repo, question, viewState = null) {
    const response = await fetch(`${API_BASE_URL}/ai/question`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ owner, repo, question, dashboard_context: viewState })
    });

    if (!response.ok) {
        throw new Error(`Failed to ask repository question: ${response.statusText}`);
    }

    return response.json();
}
