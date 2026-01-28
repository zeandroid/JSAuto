# Job Search Automation

Automated Python scripts to search for the best job opportunities from multiple job aggregators, tailored to specific skill sets and preferences.

## Project Structure

```
.
├── scripts/               # Executable job fetcher scripts
│   ├── fetch_creative_circle.py   # Creative Circle scraper for designer roles
│   └── fetch_*.py         # (Future) Additional job board fetchers
├── lib/                   # Reusable modules
│   ├── api_client.py      # Generic HTTP client with retry logic
│   └── job_parser.py      # Job parsing and filtering utilities
├── config/                # Configuration files (future)
├── data/                  # Output directory for fetched jobs (JSON)
├── pyproject.toml         # Python project metadata and dependencies
├── .env.example           # Environment variables template
└── README.md              # This file
```

## Quick Start

## Quick Start

### 1. Set up Python environment

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -e .
```

### 2. Configure environment

```bash
cp .env.example .env
# Edit .env with your preferences:
# - DESIGNER_JOB_KEYWORDS: comma-separated job keywords
# - DESIGNER_MIN_SALARY: minimum salary threshold
# - DESIGNER_LOCATION_FILTER: comma-separated location filters
```

### 3. Run Creative Circle fetcher

```bash
python scripts/fetch_creative_circle.py
```

Jobs will be **appended** to `data/designer_jobs.csv`. Duplicate jobs are automatically skipped.

## Automated Daily Fetching with GitHub Actions

For automatic, hands-off job fetching, set up the GitHub Actions workflow:

1. **Enable GitHub Actions** (if not already enabled in your repository settings)
2. **Commit the workflow file**: `.github/workflows/fetch-designer-jobs.yml`
3. **Done!** The workflow runs daily at midnight UTC and automatically commits new jobs

See [GITHUB_ACTIONS.md](GITHUB_ACTIONS.md) for detailed setup and customization options.

**Output CSV columns:**
- `job_id`, `job_title`, `company_name`, `location`, `hourly_min`, `hourly_max`
- `salary_type`, `job_type`, `recruiter_name`, `recruiter_email`
- `posted_date`, `description_short`, `skills_tags`, `url`

Example output:
```
job_id    job_title              company_name  location       hourly_min  hourly_max
927478    Senior Designer        RHR Intl      Chicago, IL    40          45
927425    Content Designer       PayPal        Austin, TX     50          60
927513    UX Designer            Abbott        Alameda, CA    65          70
...
```

## Features

### Current

- **Creative Circle Fetcher** (`scripts/fetch_creative_circle.py`)
  - Queries Creative Circle's remote-only designer job API (20 jobs per page, up to 5 pages)
  - Filters for "designer" in job title
  - Appends new jobs to `designer_jobs.csv` with automatic duplicate detection
  - Exports: job ID, title, company, location, hourly rate, recruiter, posting date, skills, and URL
  - Customizable via `.env` file

### Reusable Components

- **APIClient** (`lib/api_client.py`)
  - Generic HTTP client with automatic retry logic (exponential backoff for 429, 500–504 errors)
  - Support for GET/POST requests
  - Configurable timeouts and max retries

- **JobParser** (`lib/job_parser.py`)
  - `Job` class for standardized job representation
  - `JobFilter` class for filtering by keywords, salary, and location

- **JobCSVWriter** (`lib/job_csv.py`)
  - Append-mode CSV writer for job listings
  - Automatic header creation on first use
  - Duplicate detection by job ID
  - Read/write operations with proper encoding

## Environment Variables

See `.env.example` for all available configuration:

```
DESIGNER_JOB_KEYWORDS=designer,ui,ux,graphic,visual,web
DESIGNER_MIN_SALARY=50000
DESIGNER_LOCATION_FILTER=remote,us
DATA_DIR=./data
LOG_DIR=./logs
```

## Notes for Future Development

### Creative Circle API Details

- **Search endpoint:** `https://candidateportal.creativecircle.com/ccv5-jobs/search`
  - Parameters: `rows`, `page`, `sortType`, `workLocationTypeId` (3=Remote), `daysPosted`, `buid`
  - Returns: list of jobs with title, company, hourly rate, recruiter, skills, location
  - Response fields: `Id`, `jobTitle`, `CompanyName`, `HourlyMin`, `HourlyMax`, `RecruiterName`, `tags`, `DatePost`, `ShortDescription`

- **Details endpoint:** `https://candidateportal.creativecircle.com/ccv5-jobs/details?id=<job_id>&buid=3`
  - Returns: full job description, recruiter email, education requirements, experience level
  - Useful for enriching job data with recruiter contact info

- **Job URL construction:** `https://www.creativecircle.com/jobs/{JobURL}`

## Scheduling the Fetcher

To run the script on a schedule (e.g., daily at 9 AM):

### GitHub Actions (Recommended)

The easiest way is using GitHub Actions (configured in `.github/workflows/fetch-designer-jobs.yml`):
- Runs daily at midnight UTC (change cron schedule if needed)
- Automatically commits new jobs to the repository
- No local setup required after initial configuration

See [GITHUB_ACTIONS.md](GITHUB_ACTIONS.md) for setup and customization.

### Local Cron (macOS/Linux)

For local scheduling without GitHub:

```bash
# Add to crontab
crontab -e

# Add this line (runs daily at 9 AM)
0 9 * * * cd /path/to/JobSearch && /path/to/.venv/bin/python scripts/fetch_creative_circle.py >> logs/fetch.log 2>&1
```

### Windows Task Scheduler

1. Open Task Scheduler
2. Create new task with trigger: Daily, 9:00 AM
3. Action: `python scripts/fetch_creative_circle.py`
4. Working directory: `C:\path\to\JobSearch`

### Adding New Job Boards

To add a new job aggregator (e.g., LinkedIn, Indeed, Flexjobs):

1. Create a new script: `scripts/fetch_<board_name>.py`
2. Implement a fetcher class (follow `CreativeCircleFetcher` pattern)
3. Reuse `APIClient` and `JobFilter` from `lib/`
4. Update this README with usage instructions

### Future Enhancements

- Database storage (SQLite/PostgreSQL) instead of JSON
- Duplicate detection across job boards
- Email notifications for new matches
- Job board API integrations (if available)
- Skill matching and scoring

## Testing

(To be added)

```bash
pytest tests/
```

## License

Personal project
