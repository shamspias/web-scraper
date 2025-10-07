# Web Scraper

Professional web scraping tool with real-time progress tracking and beautiful UI.

**⚠️ LEGAL NOTICE: Only use on websites you own or have explicit permission to scrape.**

---

## 🎯 What It Does

A full-stack web scraping application that:
- Discovers all pages on a website automatically
- Extracts clean, readable text (no HTML/Markdown)
- Downloads images with metadata
- Tracks progress in real-time
- Organizes output by domain and timestamp
- Provides a beautiful web interface

---

## 🏗️ Architecture

```
┌─────────────────────┐
│   Vue 3 Frontend    │  → Beautiful UI with real-time updates
│   (Port 3000)       │
└──────────┬──────────┘
           │ REST API
           ↓
┌─────────────────────┐
│  FastAPI Backend    │  → Async web scraping
│   (Port 8000)       │
└──────────┬──────────┘
           │ Playwright
           ↓
┌─────────────────────┐
│   Target Website    │  → Authorized websites only
└─────────────────────┘
           │
           ↓
┌─────────────────────┐
│  File Storage       │  → scraped_data/{domain}_{time}/
│  - sitemap.json     │
│  - pages/           │
│  - images/          │
└─────────────────────┘
```

### Stack
- **Frontend**: Vue 3, Vite, Tailwind CSS, Pinia, Vue Router
- **Backend**: FastAPI, Playwright, BeautifulSoup, Pydantic
- **Storage**: File system (JSON + TXT + Images)

---

## 🚀 Installation

### Prerequisites
- Python 3.9+
- Node.js 18+
- npm

### Backend Setup

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium

# Create environment file
cp .env.example .env
# Edit .env with your settings

# Run server
uvicorn main:app --reload
```

Backend runs at: **http://localhost:8000**

### Frontend Setup

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Create environment file
cp .env.example .env

# Run dev server
npm run dev
```

Frontend runs at: **http://localhost:3000**

### Production Build

```bash
# Build frontend
cd frontend
npm run build

# Copy dist to backend
cp -r dist ../backend/frontend/

# Run backend (serves frontend)
cd ../backend
uvicorn main:app --host 0.0.0.0 --port 8000
```

Everything runs at: **http://localhost:8000**

---

## 📡 API Documentation

### Base URL
```
http://localhost:8000/api/v1
```

### Endpoints

#### 1. Health Check
```http
GET /api/v1/health
```

**Response:**
```json
{
  "status": "healthy",
  "service": "web-scraper",
  "active_jobs": 0
}
```

---

#### 2. Start Scraping Job
```http
POST /api/v1/scrape
```

**Request Body:**
```json
{
  "url": "https://example.com",
  "max_depth": 3,
  "include_images": true,
  "authorization_token": "your-token-here"
}
```

**Response:**
```json
{
  "job_id": "abc-123-def",
  "status": "pending",
  "message": "Scraping job started"
}
```

---

#### 3. Get Job Status
```http
GET /api/v1/scrape/{job_id}
```

**Response:**
```json
{
  "job_id": "abc-123-def",
  "status": "completed",
  "message": "Scraping completed successfully",
  "output_directory": "./scraped_data/example_com_20251007_143052",
  "total_pages_scraped": 42,
  "sitemap": {
    "total_urls": 42,
    "urls": ["url1", "url2", "..."]
  },
  "pages": [...],
  "errors": []
}
```

**Status Values:**
- `pending` - Job queued
- `in_progress` - Currently scraping
- `completed` - Successfully finished
- `failed` - Error occurred

---

#### 4. List All Jobs
```http
GET /api/v1/jobs
```

**Response:**
```json
{
  "total_jobs": 5,
  "jobs": [
    {
      "job_id": "abc-123",
      "status": "completed",
      "url": "https://example.com"
    }
  ]
}
```

---

#### 5. Delete Job
```http
DELETE /api/v1/scrape/{job_id}
```

**Response:**
```json
{
  "message": "Job deleted successfully"
}
```

---

### API Examples

**cURL:**
```bash
# Start scraping
curl -X POST http://localhost:8000/api/v1/scrape \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com",
    "max_depth": 2,
    "include_images": true,
    "authorization_token": "test-token-12345"
  }'

# Check status
curl http://localhost:8000/api/v1/scrape/{job_id}
```

**Python:**
```python
import requests

# Start scraping
response = requests.post(
    "http://localhost:8000/api/v1/scrape",
    json={
        "url": "https://example.com",
        "max_depth": 3,
        "include_images": True,
        "authorization_token": "your-token"
    }
)

job_id = response.json()["job_id"]

# Get status
status = requests.get(f"http://localhost:8000/api/v1/scrape/{job_id}")
print(status.json())
```

**JavaScript:**
```javascript
// Start scraping
const response = await fetch('http://localhost:8000/api/v1/scrape', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    url: 'https://example.com',
    max_depth: 3,
    include_images: true,
    authorization_token: 'your-token'
  })
});

const { job_id } = await response.json();

// Get status
const status = await fetch(`http://localhost:8000/api/v1/scrape/${job_id}`);
const data = await status.json();
```

---

## 📂 Output Structure

Each scraping job creates a directory:

```
scraped_data/
└── example_com_20251007_143052/
    ├── summary.txt              # Overview
    ├── sitemap.json            # All discovered URLs
    ├── all_pages.json          # Complete data
    ├── pages/                  # Individual page texts
    │   ├── 0001_index.txt
    │   ├── 0002_about.txt
    │   └── 0003_contact.txt
    └── images/                 # Downloaded images
        ├── abc123def456.jpg
        └── 789xyz012345.png
```

---

## ⚙️ Configuration

### Backend (.env)

Key settings:
```env
MAX_CONCURRENT_PAGES=5    # Concurrent scraping (1-20)
PAGE_TIMEOUT=30000        # Page load timeout (ms)
MAX_DEPTH=5               # Crawl depth (1-10)
SAVE_IMAGES=true          # Download images
OUTPUT_DIR=./scraped_data # Output directory
```

### Frontend (.env)

```env
VITE_API_URL=/api/v1      # API endpoint
```

---

## 🎨 Features

### Backend
- ✅ Async web scraping with Playwright
- ✅ Automatic link discovery (no sitemap needed)
- ✅ Clean text extraction (removes HTML/CSS/JS)
- ✅ Image downloading with metadata
- ✅ Background job processing
- ✅ Real-time progress updates
- ✅ Error handling and logging
- ✅ URL-based file organization

### Frontend
- ✅ Beautiful modern UI
- ✅ Real-time progress tracking (auto-refresh)
- ✅ Job management dashboard
- ✅ Detailed result views
- ✅ Mobile responsive design
- ✅ Status indicators and badges
- ✅ Loading states and animations
- ✅ Error handling

---

## 🧪 Testing

**Backend:**
```bash
cd backend
python test_complete_api.py
```

**Frontend:**
```bash
cd frontend
npm run dev
# Open http://localhost:3000 in browser
```

**Test with example.com:**
1. Start both backend and frontend
2. Open http://localhost:3000
3. Enter URL: `https://example.com`
4. Max Depth: `2`
5. Authorization Token: `test-token-12345`
6. Click "Start Scraping"
7. Watch real-time progress

---

## 🚢 Deployment

### Docker

```bash
# Build
docker-compose up -d

# Access
http://localhost:8000
```

### Manual

```bash
# Build frontend
cd frontend && npm run build

# Run backend
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000
```

---

## 📊 Performance

- **Speed**: 5-10 pages/second
- **Concurrent Pages**: Configurable (default 5)
- **Memory**: ~200MB base + ~50MB per concurrent page
- **Storage**: ~1-5MB per page (text + images)

---

## 🔒 Security

- **Authorization required**: Token validation on every request
- **CORS protection**: Configurable origins
- **Rate limiting**: Optional (configurable)
- **Input validation**: Pydantic schemas
- **Error sanitization**: No sensitive data in errors

---

## 🐛 Troubleshooting

**Backend not starting:**
```bash
playwright install chromium
pip install -r requirements.txt
```

**Frontend errors:**
```bash
rm -rf node_modules package-lock.json
npm install
```

**CORS errors:**
Check `CORS_ORIGINS` in backend `.env`

**Scraping fails:**
- Verify authorization token (min 10 chars)
- Check website is accessible
- Increase `PAGE_TIMEOUT` in `.env`

---

## 📝 License

MIT License - Free for personal and commercial use.

**⚠️ LEGAL REMINDER**: Only scrape websites you own or have explicit permission to access. Unauthorized scraping may violate laws including CFAA, DMCA, and website Terms of Service.

---

## 🙏 Credits

Built with:
- [FastAPI](https://fastapi.tiangolo.com/)
- [Playwright](https://playwright.dev/)
- [Vue 3](https://vuejs.org/)
- [Tailwind CSS](https://tailwindcss.com/)

---

## 📞 Support

- Documentation: See `/docs` endpoint
- Issues: Open a GitHub issue
- Legal: Read `PRIVACY.md` before use

---

**Happy (Legal) Scraping! 🚀**