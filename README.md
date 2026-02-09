# GitHub Repo Health Analyzer

A full-stack web application that analyzes GitHub repository health by visualizing commit activity over time. Built with FastAPI (backend) and React (frontend), this tool helps developers understand repository engagement patterns.

## 🎯 Features

- **GitHub Integration**: Fetches real-time commit data from any public GitHub repository
- **Data Analysis**: Uses pandas to process and aggregate commit data by day
- **Interactive Visualization**: Displays commit activity as an interactive line chart using Chart.js
- **Error Handling**: Graceful handling of invalid repositories and API errors
- **Responsive UI**: Clean, minimal interface built with React and Vite

## 🏗️ Architecture

### Backend (FastAPI + Python)
- **`main.py`**: FastAPI application with CORS-enabled REST API endpoints
- **`github_api.py`**: GitHub REST API client for fetching commit data
- **`analysis.py`**: Pandas-based commit data processing and aggregation
- **Tech Stack**: FastAPI, Uvicorn, Requests, Pandas

### Frontend (React + Vite)
- **`App.jsx`**: Main application component with repository input form
- **`CommitsChart.jsx`**: Chart.js line chart visualization component
- **`api.js`**: API client for backend communication
- **Tech Stack**: React 18, Vite 5, Chart.js, react-chartjs-2

### Data Flow

```
User Input (owner/repo)
    ↓
React Frontend (Form Submission)
    ↓
API Request → Backend /commits/{owner}/{repo}
    ↓
GitHub API Client (fetch commits)
    ↓
Pandas Analysis (aggregate by date)
    ↓
JSON Response (dates + counts)
    ↓
Chart.js Visualization
    ↓
Display to User
```

## 📋 Prerequisites

- **Python 3.8+** for backend
- **Node.js 16+** and npm for frontend
- Git for version control

## 🚀 Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/sachdeva-aarushi/github-repo-health-analyzer.git
cd github-repo-health-analyzer
```

### 2. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Install Python dependencies
pip install -r requirements.txt

# Run the FastAPI server
uvicorn main:app --reload
```

The backend will run at **http://localhost:8000**

### 3. Frontend Setup

```bash
# Navigate to frontend directory (from project root)
cd frontend

# Install Node.js dependencies
npm install

# Run the development server
npm run dev
```

The frontend will run at **http://localhost:3000**

## 🎮 Usage

1. Open your browser and navigate to **http://localhost:3000**
2. Enter a repository owner (e.g., `facebook`)
3. Enter a repository name (e.g., `react`)
4. Click **Analyze** to fetch and visualize commit data
5. View the interactive commit activity chart
6. Optionally expand "View Raw JSON Data" to see the underlying data

### Example Repositories to Try

- `facebook/react` - React JavaScript library
- `microsoft/vscode` - Visual Studio Code
- `torvalds/linux` - Linux kernel
- `tensorflow/tensorflow` - TensorFlow ML library

## 📊 API Endpoints

### Backend REST API

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Health check endpoint |
| `/test/{owner}/{repo}` | GET | Get basic repo info and commit count |
| `/commits/{owner}/{repo}` | GET | Get analyzed commit data for visualization |

### Response Format

**GET /commits/{owner}/{repo}**

```json
{
  "repository": "facebook/react",
  "data": {
    "dates": ["2024-01-15", "2024-01-16", "2024-01-17"],
    "counts": [12, 8, 15]
  }
}
```

## ⚠️ Important Notes

### GitHub API Rate Limits

- **Unauthenticated requests**: 60 requests per hour per IP
- **Authenticated requests**: 5,000 requests per hour (requires GitHub token)

If you exceed the rate limit, you'll receive a 403 error. To use authenticated requests, you can modify `backend/github_api.py` to include a GitHub personal access token.

### Commit Fetch Limit

The application currently fetches up to **100 commits** per repository (GitHub API default). For repositories with more commits, only the most recent 100 will be analyzed.

## 📁 Project Structure

```
github-repo-health-analyzer/
│
├── backend/
│   ├── main.py              # FastAPI application
│   ├── github_api.py        # GitHub API client
│   ├── analysis.py          # Data analysis with pandas
│   ├── requirements.txt     # Python dependencies
│   └── README.md            # Backend documentation
│
├── frontend/
│   ├── index.html           # HTML entry point
│   ├── package.json         # Node.js dependencies
│   ├── vite.config.js       # Vite configuration
│   └── src/
│       ├── main.jsx         # React entry point
│       ├── App.jsx          # Main app component
│       ├── api.js           # API client
│       ├── components/      # Reusable components
│       └── charts/
│           └── CommitsChart.jsx  # Chart visualization
│
├── .gitignore
└── README.md                # This file
```

## 🛠️ Development

### Backend Development

The backend runs with auto-reload enabled, so code changes will automatically restart the server:

```bash
cd backend
uvicorn main:app --reload
```

### Frontend Development

The frontend uses Vite's hot module replacement for instant updates:

```bash
cd frontend
npm run dev
```

### Building for Production

**Backend**: No build step required, deploy with a production ASGI server

**Frontend**:
```bash
cd frontend
npm run build
```

The production build will be in `frontend/dist/`

## 🤝 Contributing

Contributions are welcome! Feel free to:
- Report bugs
- Suggest new features
- Submit pull requests

## 📄 License

This project is open source and available for educational purposes.

## 🙏 Acknowledgments

- GitHub REST API for providing repository data
- FastAPI for the elegant Python web framework
- Chart.js for beautiful data visualization
- React and Vite for the modern frontend experience

---

**Built with ❤️ for developers analyzing GitHub repositories**
