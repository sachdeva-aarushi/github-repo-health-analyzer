# Backend - GitHub Repo Health Analyzer

FastAPI-based REST API backend for analyzing GitHub repository commit data.

## 🏗️ Architecture

This backend provides a REST API that:
1. Fetches commit data from the GitHub REST API
2. Processes and aggregates the data using pandas
3. Returns JSON responses for frontend visualization

## 📦 Components

### `main.py`
The core FastAPI application with three endpoints:

- **GET `/`**: Health check endpoint
  - Returns: `{"status": "API running"}`
  
- **GET `/test/{owner}/{repo}`**: Basic repository information
  - Returns: Repository name and total commit count
  
- **GET `/commits/{owner}/{repo}`**: Analyzed commit data
  - Returns: Dates and counts for chart visualization

**Features**:
- CORS middleware enabled for frontend communication
- HTTPException handling for errors
- Clean, documented endpoint functions

### `github_api.py`
GitHub REST API client with robust error handling.

**Function**: `get_commits(owner, repo, per_page=100)`

- Fetches commit data from `https://api.github.com/repos/{owner}/{repo}/commits`
- Parameters:
  - `owner`: Repository owner (username or organization)
  - `repo`: Repository name
  - `per_page`: Number of commits to fetch (default: 100, max: 100)
- Returns: List of commit dictionaries or `None` on error

**Error Handling**:
- HTTP errors (404, 403, etc.)
- Connection errors
- Timeout errors (10-second limit)
- General request exceptions

### `analysis.py`
Pandas-based data processing module.

**Function**: `analyze_commits(commits)`

- Extracts commit timestamps from GitHub API response
- Creates a pandas DataFrame
- Converts timestamps to datetime objects
- Aggregates commits by day
- Returns chart-ready data structure

**Process**:
1. Extract dates from `commit['commit']['author']['date']`
2. Convert to pandas datetime
3. Strip time component (keep date only)
4. Use `value_counts()` to count commits per day
5. Sort by date
6. Return as separate arrays for dates and counts

## 🔧 Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Setup

```bash
# Navigate to backend directory
cd backend

# Install dependencies
pip install -r requirements.txt
```

### Dependencies

```
fastapi       # Web framework
uvicorn       # ASGI server
requests      # HTTP client for GitHub API
pandas        # Data processing and analysis
```

## 🚀 Running the Server

### Development Mode (with auto-reload)

```bash
uvicorn main:app --reload
```

Server will run at: **http://localhost:8000**

### Production Mode

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

### Alternative: Using Python directly

```bash
python -m uvicorn main:app --reload
```

## 📡 API Reference

### Endpoint Details

#### 1. Health Check
```
GET /
```

**Response**:
```json
{
  "status": "API running"
}
```

#### 2. Repository Test
```
GET /test/{owner}/{repo}
```

**Parameters**:
- `owner`: Repository owner (path parameter)
- `repo`: Repository name (path parameter)

**Response**:
```json
{
  "repository": "facebook/react",
  "commit_count": 100
}
```

**Error Response** (404):
```json
{
  "detail": "Could not fetch data for repository facebook/react. Please check if the repository exists."
}
```

#### 3. Commit Analysis
```
GET /commits/{owner}/{repo}
```

**Parameters**:
- `owner`: Repository owner (path parameter)
- `repo`: Repository name (path parameter)

**Response**:
```json
{
  "repository": "facebook/react",
  "data": {
    "dates": ["2024-01-15", "2024-01-16", "2024-01-17"],
    "counts": [12, 8, 15]
  }
}
```

**Error Response** (404):
```json
{
  "detail": "Could not fetch data for repository facebook/react. Please check if the repository exists."
}
```

## 🧪 Testing

### Manual Testing with Browser

Navigate to `http://localhost:8000/docs` to access the **interactive API documentation** (Swagger UI).

You can test all endpoints directly from the browser!

### Testing with curl

```bash
# Health check
curl http://localhost:8000/

# Test endpoint
curl http://localhost:8000/test/facebook/react

# Commits analysis
curl http://localhost:8000/commits/facebook/react
```

### Testing with Python

```python
import requests

# Test endpoint
response = requests.get("http://localhost:8000/test/facebook/react")
print(response.json())

# Commits endpoint
response = requests.get("http://localhost:8000/commits/facebook/react")
print(response.json())
```

## ⚠️ GitHub API Rate Limits

### Unauthenticated Requests
- **60 requests per hour** per IP address
- Rate limit resets every hour

### Authenticated Requests (Recommended for Production)
- **5,000 requests per hour** with GitHub token
- Requires personal access token

### Adding Authentication (Optional)

To use authenticated requests, modify `github_api.py`:

```python
def get_commits(owner: str, repo: str, per_page: int = 100) -> Optional[List[Dict]]:
    url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/commits"
    params = {"per_page": per_page}
    
    # Add GitHub token
    headers = {
        "Authorization": "token YOUR_GITHUB_TOKEN_HERE"
    }
    
    response = requests.get(url, params=params, headers=headers, timeout=10)
    # ... rest of the code
```

**Get a token**: https://github.com/settings/tokens

## 🔍 Common Issues

### Port Already in Use
If port 8000 is already in use:
```bash
uvicorn main:app --reload --port 8001
```

### Module Not Found
Make sure you're in the `backend` directory and dependencies are installed:
```bash
cd backend
pip install -r requirements.txt
```

### CORS Errors
The current configuration allows all origins (`allow_origins=["*"]`). For production, update to specific origins:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Your frontend URL
    ...
)
```

## 📈 Performance Considerations

- **Caching**: Consider implementing caching for frequently requested repositories
- **Rate Limiting**: Add rate limiting middleware to prevent abuse
- **Pagination**: Current implementation fetches only 100 commits; consider adding pagination for larger datasets
- **Async Requests**: For multiple repositories, consider async/await patterns

## 🚀 Deployment

For production deployment:

1. Use a production-grade ASGI server
2. Enable HTTPS
3. Configure specific CORS origins
4. Add GitHub authentication token
5. Implement caching layer (Redis)
6. Add logging and monitoring
7. Use environment variables for configuration

Example production command:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

## 📚 Further Reading

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [GitHub REST API Documentation](https://docs.github.com/en/rest)
- [Pandas Documentation](https://pandas.pydata.org/docs/)
- [Uvicorn Documentation](https://www.uvicorn.org/)

---

**Questions or Issues?** Open an issue on GitHub!
