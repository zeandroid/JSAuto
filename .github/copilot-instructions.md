## Purpose

This file gives concise, actionable guidance for AI coding agents (Copilot-style assistants) to become productive quickly in this repository. It focuses on where to look, how to discover the project's architecture and conventions, and concrete commands/examples to run while exploring.

## Project-Specific Guidance: Job Search Automation

This repository automates job searches across multiple job boards (Creative Circle, LinkedIn, Indeed, etc.) to find best-fit opportunities based on user skills and preferences. Currently implemented: **Creative Circle remote designer job fetcher**.

### Key Components

**Structure:**
- `scripts/fetch_<job_board>.py` — Individual API fetcher for each job board
- `lib/api_client.py` — Reusable HTTP client with retry logic (base for all fetchers)
- `lib/job_parser.py` — Job class and JobFilter for standardized job representation and filtering
- `lib/job_csv.py` — CSV writer with append mode and duplicate detection
- `data/` — Output directory for fetched job listings (CSV files)
- `.env` — Configuration for search filters, output file names

**Current Implementation: Creative Circle Fetcher**

The fetcher queries the public Creative Circle API without authentication:

```bash
python scripts/fetch_creative_circle.py
# Fetches 5 pages (100 jobs) of remote designer roles
# Filters for "designer" in job title
# Appends new jobs to data/designer_jobs.csv
# Automatically skips duplicates based on job_id
```

**CSV Output Schema:**
```
job_id, job_title, company_name, location, hourly_min, hourly_max, salary_type,
job_type, recruiter_name, recruiter_email, posted_date, description_short, skills_tags, url
```

### Adding a New Job Board Fetcher

When adding a new job board (e.g., `fetch_linkedin.py`, `fetch_indeed.py`):

1. **Understand the API/scraping approach:**
   - Check if the board has a public JSON API (LinkedIn, Indeed, Glassdoor often do)
   - For JavaScript-heavy sites, use `Selenium` or `Playwright`
   - For static HTML, use `BeautifulSoup`

2. **Create a new fetcher script** following `scripts/fetch_creative_circle.py`:
   - Implement a `FetcherClass` with at least:
     - `__init__()` — Initialize CSV writer and any config
     - `fetch_jobs()` — Query the API/site and filter for "designer"
     - `_format_job_for_csv()` — Convert API response to CSV dict
   - Return results as list of dicts matching `CSV_HEADERS`

3. **Reuse common components:**
   - Use `JobCSVWriter` from `lib/job_csv.py` for CSV handling (automatic duplicate detection)
   - Use `APIClient` from `lib/api_client.py` for HTTP requests (automatic retries)
   - Use `JobFilter` from `lib/job_parser.py` if filtering by keyword/salary/location

4. **Update environment variables** (`.env.example`):
   - Add board-specific config (e.g., `LINKEDIN_KEYWORDS`, `INDEED_MIN_SALARY`)
   - Add output file name (e.g., `LINKEDIN_CSV_FILE=linkedin_jobs.csv`)

### Common Patterns from Current Implementation

**API Response Parsing:**
```python
# Creative Circle API returns paginated results
response = requests.get(SEARCH_ENDPOINT, params={
    "rows": 20,
    "page": page_number,
    "workLocationTypeId": 3,  # Remote only
})
jobs = response.json().get("jobs", [])

# Filter for "designer" in title
for job in jobs:
    if "designer" in job.get("jobTitle", "").lower():
        # Process job...
```

**CSV Format Mapping:**
```python
def _format_job_for_csv(job_api_response):
    return {
        "job_id": job_api_response.get("Id"),
        "job_title": job_api_response.get("jobTitle"),
        "company_name": job_api_response.get("CompanyName"),
        "hourly_min": job_api_response.get("HourlyMin"),
        # ... map remaining fields
    }
```

**Duplicate Detection:**
```python
# JobCSVWriter handles this automatically
existing_ids = self.csv_writer.get_existing_job_ids()
if job_id not in existing_ids:
    csv_rows.append(formatted_job)
```

### Common Pitfalls

- **API rate limiting** — Creative Circle allows ~1 req/sec. Add delays for slower scraping: `time.sleep(1)`
- **Job ID uniqueness** — Always use a unique, board-specific identifier (e.g., API's native job ID, not generated)
- **Date format consistency** — Parse API dates to ISO or readable format before saving to CSV
- **Missing fields** — Some boards don't provide salary/recruiter; leave empty string `""` in CSV rather than null
- **Location normalization** — Some APIs return coordinates, others return city/state. Normalize to "City, State" format
- **HTML entity decoding** — Job descriptions from HTML might contain `&amp;`, `&lt;`, etc.; use `html.unescape()`

---

## Generic Guidance (for Future Projects)

### Quick start — what to check first

1. Look for top-level language / build manifests: `package.json`, `pyproject.toml`, `requirements.txt`, `go.mod`, `Cargo.toml`, `pom.xml`, `Makefile`, `Dockerfile`.
2. Inspect top-level directories commonly used to hold services or code:
   - `src/`, `cmd/`, `pkg/`, `internal/`, `server/`, `api/`, `services/`, `apps/`, `infra/`, `deploy/`.
3. Locate tests: `tests/`, `__tests__/`, files ending in `*_test.py`, `*.spec.ts`, `*_test.go`.

### Big-picture architecture discovery checklist

- Identify service boundaries by finding multiple `main`/`index`/`server` entry points.
- Search for inter-service contracts: `openapi.yml`, `swagger`, `proto` files, or GraphQL schema files.
- Look for infra and orchestration: `docker-compose.yml`, `k8s/`, `charts/`, `terraform/`.
- Find environment/config patterns: `.env`, `config/`, `settings.py`.

### Build / test / debug workflows

- If `pyproject.toml` / `requirements.txt` exists: create venv, `pip install -e .`, run `pytest`.
- If `package.json` exists: `npm ci` then `npm test` or `npm run build`.
- If `go.mod` exists: `go test ./...` and `go build ./...`.
