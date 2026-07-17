# ScanGuard AI

**AI-Powered Network Security Analysis Platform**

> Automatically analyzes Nmap scan results and explains them in simple language using AI.

![React](https://img.shields.io/badge/React-18-61DAFB?style=flat&logo=react)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104-009688?style=flat&logo=fastapi)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?style=flat&logo=postgresql)
![Tailwind](https://img.shields.io/badge/Tailwind-3.3-06B6D4?style=flat&logo=tailwindcss)
![Docker](https://img.shields.io/badge/Docker-24-2496ED?style=flat&logo=docker)
![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=flat&logo=python)

---

## Table of Contents

- [Problem](#problem)
- [Solution](#solution)
- [Features](#features)
- [Screenshots](#screenshots)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Configuration](#configuration)
- [Usage](#usage)
- [API Documentation](#api-documentation)
- [How It Works](#how-it-works)
- [Contributing](#contributing)
- [License](#license)

---

## Problem

Many SMEs and organizations don't know which devices or services are exposed on their networks. Traditional security audits are expensive, and Nmap scan output is highly technical — difficult for non-security staff to interpret.

## Solution

ScanGuard AI is a web app that automatically analyzes Nmap scan results and explains them in simple language. Upload your scan file and get:

- Plain-English explanations of every open port
- A risk score from 0 to 100
- Detection of outdated services with known vulnerabilities
- Actionable security recommendations
- Professional PDF reports for stakeholders

---

## Features

| Feature | Description |
|---|---|
| **File Upload** | Upload `.xml`, `.nmap`, or `.gnmap` Nmap scan files |
| **AI Analysis** | OpenRouter GPT explains every port in plain English |
| **Risk Score** | 0-100 score based on ports, services, and vulnerabilities |
| **Outdated Detection** | Flags outdated software with known CVEs |
| **Recommendations** | Actionable security advice prioritized by severity |
| **PDF Reports** | Professional reports with charts and findings |
| **Dashboard** | Visual overview with Chart.js (line, doughnut, bar) |
| **Scan Comparison** | Track risk score trends over time |
| **Team Management** | Invite codes, roles, shared scans |
| **Dark Mode** | Built-in dark mode toggle |
| **JWT Authentication** | Secure register/login with bcrypt |
| **Scan Comments** | Collaborate with notes on scan results |

---

## Tech Stack

### Frontend
- **React 18** with Vite
- **Tailwind CSS 3** for styling
- **Chart.js** for dashboard visualizations
- **React Router 6** for SPA routing
- **Axios** for API calls
- **Lucide React** for icons
- **React Dropzone** for file uploads
- **React Hot Toast** for notifications

### Backend
- **FastAPI** (Python 3.11)
- **SQLAlchemy 2.0** (async) with **AsyncPG**
- **Alembic** for database migrations
- **python-jose** for JWT tokens
- **passlib** with bcrypt for passwords
- **httpx** for async HTTP (OpenRouter API)
- **lxml** for Nmap XML parsing
- **WeasyPrint** for PDF generation
- **Jinja2** for HTML templates

### Infrastructure
- **PostgreSQL 16** for database
- **Redis 7** for caching
- **Docker** and **Docker Compose** for deployment
- **Nginx** for frontend serving and API proxying

### AI
- **OpenRouter API** with GPT-3.5-turbo (free tier compatible)

---

## Project Structure

```
scanguard/
├── docker-compose.yml              # Container orchestration
├── README.md
├── sample_scan.xml                 # Test Nmap XML for demo
│
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── alembic.ini
│   │
│   ├── migrations/
│   │   ├── env.py
│   │   └── versions/
│   │       └── 001_initial.py      # Database schema
│   │
│   └── app/
│       ├── main.py                 # FastAPI app + CORS
│       │
│       ├── core/
│       │   ├── config.py           # Environment settings
│       │   └── database.py         # Async SQLAlchemy engine
│       │
│       ├── models/
│       │   └── models.py           # SQLAlchemy ORM models
│       │
│       ├── api/
│       │   ├── auth.py             # Register, login, JWT
│       │   ├── scans.py            # Upload, list, detail, PDF
│       │   ├── teams.py            # Create, join, invite codes
│       │   └── dashboard.py        # Stats, charts, trends
│       │
│       ├── services/
│       │   ├── nmap_parser.py      # XML parser + risk scoring
│       │   ├── ai_service.py       # OpenRouter GPT integration
│       │   └── pdf_service.py      # HTML-to-PDF reports
│       │
│       └── utils/
│           ├── auth.py             # JWT + password hashing
│           └── schemas.py          # Pydantic validation
│
└── frontend/
    ├── Dockerfile
    ├── nginx.conf                  # SPA routing + API proxy
    ├── package.json
    ├── vite.config.js
    ├── tailwind.config.js
    ├── postcss.config.js
    ├── index.html
    │
    └── src/
        ├── main.jsx
        ├── App.jsx                 # Router configuration
        ├── index.css               # Tailwind + custom styles
        │
        ├── context/
        │   └── AuthContext.jsx     # Auth state + dark mode
        │
        ├── components/
        │   ├── Layout.jsx          # Main app shell
        │   ├── Sidebar.jsx         # Collapsible navigation
        │   └── Navbar.jsx          # Top bar + user menu
        │
        ├── pages/
        │   ├── Landing.jsx         # Public marketing page
        │   ├── Login.jsx           # Sign in
        │   ├── Register.jsx        # Create account
        │   ├── Dashboard.jsx       # Charts + recent scans
        │   ├── UploadScan.jsx      # Drag-and-drop upload
        │   ├── Scans.jsx           # Scan history + filters
        │   ├── ScanDetail.jsx      # Full analysis view
        │   └── Team.jsx            # Team management
        │
        └── utils/
            ├── api.js              # Axios instance + interceptors
            └── helpers.js          # Risk colors, formatters
```

---

## Getting Started

### Prerequisites

- **Docker** and **Docker Compose** (v2+)
- **Git**
- Internet connection (for AI features via OpenRouter)

### Quick Start

1. **Clone the repository**

```bash
git clone https://github.com/yourusername/scanguard.git
cd scanguard
```

2. **Add yourself to the docker group** (if not already)

```bash
sudo usermod -aG docker $USER
newgrp docker
```

3. **Start the application**

```bash
docker-compose up --build
```

4. **Open in browser**

| Service | URL |
|---|---|
| Frontend | http://localhost:3000 |
| Backend API | http://localhost:8000 |
| API Docs (Swagger) | http://localhost:8000/docs |
| API Docs (ReDoc) | http://localhost:8000/redoc |

5. **Register an account** and start scanning.

---

## Configuration

### Environment Variables

All configuration is in `docker-compose.yml`. You can override these as needed:

| Variable | Default | Description |
|---|---|---|
| `DATABASE_URL` | `postgresql+asyncpg://scanguard:scanguard_secret@db:5432/scanguard` | Async database URL |
| `SYNC_DATABASE_URL` | `postgresql://scanguard:scanguard_secret@db:5432/scanguard` | Sync URL for Alembic |
| `REDIS_URL` | `redis://redis:6379/0` | Redis connection string |
| `SECRET_KEY` | `change-me-in-production-super-secret-key-2024` | JWT signing secret |
| `OPENROUTER_API_KEY` | *(pre-configured)* | OpenRouter API key |
| `OPENROUTER_MODEL` | `openai/gpt-3.5-turbo` | AI model to use |
| `UPLOAD_DIR` | `/app/uploads` | File storage path |
| `MAX_UPLOAD_SIZE` | `52428800` (50MB) | Max upload size in bytes |

### Production Deployment

Before deploying to production, change these values:

```yaml
SECRET_KEY: your-random-64-char-secret-here
POSTGRES_PASSWORD: your-strong-database-password
```

---

## Usage

### 1. Upload a Scan

- Go to **Upload Scan** in the sidebar
- Drag and drop an Nmap XML file (or click to browse)
- Enter a title and target (e.g., `192.168.1.0/24`)
- Select the scan type
- Click **Analyze with AI**

### 2. View Analysis

- **Overview tab**: AI summary, outdated services, scan details
- **Ports tab**: Every open port with AI explanations and risk levels
- **Recommendations tab**: Prioritized security actions
- **Comments tab**: Add notes and collaborate with your team

### 3. Generate PDF Reports

- Open any completed scan
- Click **Export PDF** in the top right
- Download the professional report to share with stakeholders

### 4. Track Trends

- The **Dashboard** shows your risk score trend over 30 days
- Compare multiple scans to see improvement over time
- Use filters to find critical or high-risk scans

### 5. Team Collaboration

- Go to **Team** in the sidebar
- Create a new team or join with an invite code
- Team members can share and view each other's scans

---

## API Documentation

### Authentication

```
POST /api/auth/register    - Create account
POST /api/auth/login       - Get JWT token
GET  /api/auth/me          - Current user info
```

### Scans

```
POST   /api/scans/upload        - Upload Nmap file (multipart/form-data)
GET    /api/scans/              - List user's scans
GET    /api/scans/{id}          - Scan detail with ports
DELETE /api/scans/{id}          - Delete a scan
GET    /api/scans/{id}/pdf      - Download PDF report
POST   /api/scans/{id}/comments - Add comment
GET    /api/scans/{id}/comments - List comments
```

### Teams

```
POST   /api/teams/       - Create team
POST   /api/teams/join   - Join with invite code
GET    /api/teams/me     - Get my team
GET    /api/teams/members - List team members
DELETE /api/teams/leave   - Leave team
```

### Dashboard

```
GET /api/dashboard/       - Aggregated stats + chart data
```

Full interactive API docs are available at `/docs` when the server is running.

---

## How It Works

### Nmap Parsing

The backend parses Nmap XML output using Python's `lxml` library. It extracts:
- Host information (IP, hostname, status)
- Port data (number, protocol, state)
- Service details (name, product, version)
- Script output and banners

### Risk Scoring (0-100)

The risk score is calculated based on:
- **Open ports** with known vulnerable services (telnet, RDP, SMB, etc.)
- **Outdated software versions** compared to known safe ranges
- **Exposure level** (database ports, remote access services on public IPs)
- **Attack surface** (total number of open ports)

Score ranges:
- **80-100**: Critical — immediate action required
- **60-79**: High — significant security concerns
- **40-59**: Medium — review and harden
- **20-39**: Low — minor improvements possible
- **0-19**: Minimal — well-secured

### AI Integration

Uses the **OpenRouter API** (GPT-3.5-turbo by default) to:
1. Explain each open port in plain English
2. Generate an executive summary of the entire scan
3. Provide prioritized security recommendations

If the AI service is unavailable, fallback explanations are generated from built-in knowledge of common services and vulnerabilities.

### PDF Generation

Reports are generated using:
1. **Jinja2** templates with styled HTML
2. **WeasyPrint** to render HTML to PDF
3. Includes risk assessment, port table, AI explanations, and recommendations

---

## Database Schema

| Table | Description |
|---|---|
| `users` | User accounts with roles and team membership |
| `teams` | Teams with invite codes |
| `scans` | Scan metadata, risk scores, AI summaries |
| `scan_ports` | Individual port findings per scan |
| `scan_comments` | User comments on scans |

---

## Development

### Running without Docker

**Backend:**

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Start PostgreSQL locally, then:
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

**Frontend:**

```bash
cd frontend
npm install
npm run dev
```

### Useful Commands

```bash
# View backend logs
docker-compose logs -f backend

# Access PostgreSQL
docker-compose exec db psql -U scanguard -d scanguard

# Rebuild after changes
docker-compose up --build

# Stop all containers
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

---

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing`)
5. Open a Pull Request

---

## License

MIT License. See [LICENSE](LICENSE) for details.

---

## Acknowledgments

- [Nmap](https://nmap.org/) — the network scanner
- [OpenRouter](https://openrouter.ai/) — AI API provider
- [FastAPI](https://fastapi.tiangolo.com/) — Python web framework
- [Chart.js](https://www.chartjs.org/) — visualization library
- [Tailwind CSS](https://tailwindcss.com/) — utility-first CSS
