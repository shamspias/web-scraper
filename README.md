# Web Scraper

Professional web scraping tool with hierarchical sitemap, structured content extraction, and persistent storage.

**⚠️ LEGAL NOTICE: Only use on websites you own or have explicit permission to scrape.**

---

## 🎯 What's New in v0.0.2

- ✅ **Hierarchical Sitemap**: Builds complete site hierarchy before scraping
- ✅ **Image URLs Only**: Extracts image URLs without downloading files
- ✅ **Structured Content**: Preserves content structure with images at exact positions
- ✅ **Persistent Storage**: Auto-loads previous scraping jobs on restart
- ✅ **Smart URL Filtering**: Skips non-webpage files (.pdf, .png, .csv, etc.)
- ✅ **JSON & CSV Export**: Multiple output formats for easy integration
- ✅ **Domain Restriction**: Only scrapes URLs under the given domain

---

## 📊 Output Structure

Each scraping job creates:

```
scraped_data/
└── example_com_20251007_143052/
    ├── sitemap.json          # Hierarchical URL structure
    ├── pages.json            # All pages with structured content
    ├── pages.csv             # CSV format for spreadsheets
    └── summary.json          # Job summary and statistics
```

### sitemap.json
```json
{
  "total_urls": 42,
  "base_url": "https://example.com",
  "hierarchy": {
    "https://example.com": [
      "https://example.com/about",
      "https://example.com/products"
    ],
    "https://example.com/products": [
      "https://example.com/products/item1",
      "https://example.com/products/item2"
    ]
  },
  "urls": ["url1", "url2", "..."]
}
```

### pages.json
```json
[
  {
    "url": "https://example.com",
    "title": "Example Domain",
    "metadata": {
      "description": "Example description",
      "keywords": "example, test",
      "author": "John Doe"
    },
    "structured_content": [
      {
        "type": "text",
        "content": "This is a paragraph of text."
      },
      {
        "type": "image",
        "url": "https://example.com/image.jpg",
        "alt": "Example image",
        "title": "Image title"
      },
      {
        "type": "text",
        "content": "More text after the image."
      }
    ],
    "all_images": [
      "https://example.com/image1.jpg",
      "https://example.com/image2.jpg"
    ],
    "scraped_at": "2025-10-07T14:30:52"
  }
]
```

### pages.csv
```csv
url,title,description,keywords,author,image_count,content_blocks,full_content,all_images
"https://example.com","Example","Description","keywords","Author","2","15","Full text content [IMAGE: url] more text","url1; url2"
```

---

## 🏗️ Architecture

```
┌─────────────────────┐
│   Vue 3 Frontend    │  → Real-time progress tracking
│   (Port 3000)       │  → Auto-loads previous jobs
└──────────┬──────────┘
           │ REST API
           ↓
┌─────────────────────┐
│  FastAPI Backend    │  → Async scraping
│   (Port 8000)       │  → Persistent storage
│                     │  → Hierarchical crawling
└──────────┬──────────┘
           │
           ↓
    1. Build Sitemap Hierarchy
    2. Filter URLs (same domain only)
    3. Skip non-webpage files
    4. Scrape with structure preservation
    5. Save as JSON + CSV
           │
           ↓
┌─────────────────────┐
│  File Storage       │
│  - sitemap.json     │  → Hierarchical structure
│  - pages.json       │  → Structured content
│  - pages.csv        │  → Spreadsheet format
│  - summary.json     │  → Statistics
└─────────────────────┘
```

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

# Run dev server
npm run dev
```

Frontend runs at: **http://localhost:3000**

---

## 📡 API Endpoints

### 1. Start Scraping
```http
POST /api/v1/scrape
Content-Type: application/json

{
  "url": "https://example.com",
  "max_depth": 3,
  "authorization_token": "your-token-here"
}
```

**Process:**
1. Validates URL and authorization
2. Builds hierarchical sitemap (only same-domain URLs)
3. Filters out non-webpage files
4. Scrapes pages with structured content
5. Saves as JSON and CSV

### 2. Get Job Status
```http
GET /api/v1/scrape/{job_id}
```

Returns job status, progress, and results.

### 3. List All Jobs
```http
GET /api/v1/jobs
```

Lists all jobs including those loaded from disk.

### 4. Reload Jobs
```http
POST /api/v1/reload
```

Reloads all jobs from scraped_data directory.

### 5. Delete Job
```http
DELETE /api/v1/scrape/{job_id}
```

Removes job from memory (files remain on disk).

---

## ⚙️ Configuration

### Key Settings (.env)

```env
# Concurrent pages (1-20)
MAX_CONCURRENT_PAGES=5

# Page timeout (milliseconds)
PAGE_TIMEOUT=30000

# Max crawl depth (1-10)
MAX_DEPTH=5

# Output directory
OUTPUT_DIR=./scraped_data
```

---

## 🎨 Features

### Backend
- ✅ Hierarchical sitemap building
- ✅ Same-domain URL filtering
- ✅ Non-webpage file exclusion (.pdf, .png, .csv, etc.)
- ✅ Structured content extraction (text + images at positions)
- ✅ Image URL extraction (no downloads)
- ✅ JSON and CSV export
- ✅ Persistent storage (auto-load on restart)
- ✅ Background job processing
- ✅ Real-time progress updates

### Frontend
- ✅ Beautiful modern UI
- ✅ Real-time progress tracking
- ✅ Auto-refresh for active jobs
- ✅ View hierarchical sitemaps
- ✅ Browse structured content
- ✅ Persistent job list (survives restart)
- ✅ Mobile responsive

---

## 🔧 URL Filtering

### Automatically Skipped Extensions
```
.pdf, .doc, .docx, .xls, .xlsx, .ppt, .pptx
.zip, .rar, .tar, .gz, .7z
.jpg, .jpeg, .png, .gif, .bmp, .svg, .webp, .ico
.mp4, .avi, .mov, .wmv, .flv, .mkv
.mp3, .wav, .ogg, .flac
.exe, .dmg, .app, .deb, .rpm
.xml, .json, .csv, .txt
```

Only HTML pages are scraped!

---

## 📝 Usage Example

### 1. Start Scraping
```bash
curl -X POST http://localhost:8000/api/v1/scrape \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com",
    "max_depth": 2,
    "authorization_token": "my-secure-token-12345"
  }'
```

### 2. Check Status
```bash
curl http://localhost:8000/api/v1/scrape/{job_id}
```

### 3. View Results
Results are automatically saved in:
```
./scraped_data/example_com_20251007_143052/
```

### 4. Restart Backend
When you restart the backend, all previous jobs are automatically loaded!

---

## 🎯 Workflow

1. **Submit URL** → Backend validates authorization
2. **Build Sitemap** → Crawls site, builds hierarchy
3. **Filter URLs** → Keeps only same-domain web pages
4. **Scrape Pages** → Extracts structured content
5. **Save Results** → JSON + CSV with full structure
6. **Auto-Load** → On restart, loads all previous jobs

---

## 🚢 Deployment

### Docker (Coming Soon)

### Manual Production
```bash
# Build frontend
cd frontend && npm run build

# Copy to backend
cp -r dist ../backend/frontend/

# Run backend
cd ../backend
uvicorn main:app --host 0.0.0.0 --port 8000
```

---

## 📊 Performance

- **Speed**: 5-10 pages/second
- **Concurrent**: 5 pages (configurable)
- **Memory**: ~200MB base + ~50MB per concurrent page
- **Storage**: ~100KB-1MB per page (JSON + CSV)

---

## 🐛 Troubleshooting

### Jobs not showing after restart
- Check `./scraped_data/` directory exists
- Ensure `summary.json`, `sitemap.json`, `pages.json` exist
- Check backend logs for load errors
- Try POST `/api/v1/reload` to force reload

### Scraping fails
- Verify authorization token (min 10 chars)
- Check URL is accessible
- Ensure it's a webpage (not .pdf, .png, etc.)
- Increase `PAGE_TIMEOUT` in `.env`

### Too many URLs
- Reduce `MAX_DEPTH` in `.env`
- Check for pagination loops
- Verify same-domain filtering is working

---

## 🔒 Security

- **Authorization Required**: 10+ character tokens
- **Domain Restriction**: Only scrapes given domain
- **File Type Filtering**: Skips non-webpage files
- **Rate Limiting**: Configurable concurrent pages
- **Input Validation**: Pydantic schemas

---

## 📄 Output Format Details

### Structured Content
Content is saved as an array of blocks:

```json
{
  "type": "text",
  "content": "Paragraph text"
}
```

```json
{
  "type": "image",
  "url": "https://example.com/image.jpg",
  "alt": "Image description",
  "title": "Image title"
}
```

This preserves the **exact position** of images in the content flow!

### Metadata Extraction
- Page title
- Meta description
- Meta keywords
- Open Graph tags
- Author information

---

## 📝 License

MIT License - Free for personal and commercial use.

**⚠️ LEGAL REMINDER**: Only scrape websites you own or have explicit permission to access.

---

## 🙏 Credits

Built with:
- [FastAPI](https://fastapi.tiangolo.com/)
- [Playwright](https://playwright.dev/)
- [Vue 3](https://vuejs.org/)
- [Tailwind CSS](https://tailwindcss.com/)