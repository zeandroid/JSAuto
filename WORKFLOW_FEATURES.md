# GitHub Actions Workflow Features

## Overview

The workflow (`.github/workflows/fetch-designer-jobs.yml`) provides automated daily job fetching with intelligent change detection and Git integration.

## Key Features

### ✅ Automated Scheduling
- **Runs daily at midnight UTC** (configurable via cron expression)
- **Manual trigger support** (`workflow_dispatch`) for on-demand runs
- **Timezone**: Uses UTC by default (adjust cron for your timezone)

### ✅ Smart Job Fetching
- Queries Creative Circle API for remote designer positions
- Filters for jobs with "designer" in the title
- Verifies jobs are active (filters out closed positions)
- Automatically skips duplicate jobs (by ID)
- Appends only new jobs to CSV

### ✅ Intelligent Change Detection
- Detects if new jobs were added
- Only commits to repository if changes exist
- Uses `git diff` to compare before/after

### ✅ Git Integration
- Automatically commits new jobs with timestamp
- Pushes changes back to the repository
- Uses GitHub's default token (no auth setup needed)
- Includes descriptive commit messages: `chore: update designer jobs - 2026-01-28 14:35:00`

### ✅ Dependency Caching
- Caches pip dependencies for faster runs
- Significantly reduces execution time on subsequent runs

### ✅ Detailed Logging & Summary
- Shows total jobs fetched per page
- Displays number of new jobs found
- Provides workflow summary in GitHub Actions interface
- Total designer jobs count in database

### ✅ Error Handling
- Gracefully handles API failures
- Continues if individual job detail checks fail
- Logs warnings for inactive jobs
- Provides clear error messages in logs

## Workflow Steps (in order)

1. **Checkout repository** — Pulls latest code from branch
2. **Set up Python** — Installs Python 3.11 with pip caching
3. **Install dependencies** — Runs `pip install -e .`
4. **Fetch designer jobs** — Executes main script
5. **Check for changes** — Detects if CSV was modified
6. **Commit and push** — If changes found, commits and pushes
7. **Summary** — Displays results and status

## Execution Time

- **Typical run:** 3-5 minutes (includes API queries for 100+ jobs)
- **With caching:** 2-3 minutes on subsequent runs
- **API calls:** ~100 jobs/page × 5 pages = 500 API calls (1 per search page)
- Plus up to 26 additional calls for job detail checks (is_active)

## What Gets Committed

Only `data/designer_jobs.csv` is committed when changes are detected:
- CSV file grows over time as new jobs are added
- Old jobs never removed (historical data preserved)
- Duplicate jobs never added (checked by ID)

Example commit:
```
chore: update designer jobs - 2026-01-28 00:15:42

3 new designer jobs added:
- Senior Designer @ RHR International
- Content Designer @ PayPal
- UX Designer @ Abbott
```

## Environment & Configuration

### Build Environment
- **OS:** Ubuntu Latest (GitHub-hosted runner)
- **Python:** 3.11
- **Dependencies:** Installed from `pyproject.toml`

### Environment Variables
Set in workflow for each run:
```yaml
DATA_DIR: ./data
DESIGNER_CSV_FILE: designer_jobs.csv
```

Can be customized in workflow file if needed.

### GitHub Token
Uses default `GITHUB_TOKEN` with automatically-provided permissions:
- Read repository code
- Write to repository (for commits/pushes)
- No additional setup required

## Notifications & Monitoring

### Built-in Notifications
- **Failure:** GitHub emails you if workflow fails
- **Success:** No email, but visible in Actions tab
- **Changes:** New commits appear in repository automatically

### Manual Checking
1. Go to **Actions** tab on GitHub
2. Select **Fetch Designer Jobs Daily** workflow
3. View all past runs with status and logs
4. Click on specific run for detailed logs

### Change History
Track all job updates via Git history:
```bash
git log --oneline --grep="update designer jobs"
```

## Performance & Costs

### GitHub Actions Free Tier
- ✅ Unlimited workflows on public repositories
- ✅ 2,000 free minutes/month on private repositories
- ✅ This workflow uses <5 minutes per run

**Monthly cost:** $0 for this workflow (well under free limits)

### Optimization Tips
1. Caching enabled (pip packages cached between runs)
2. Only commits if changes detected (no unnecessary pushes)
3. Uses lightweight Python 3.11 image
4. API calls are fast (~1 req/sec per workflow design)

## Advanced Features (Configurable)

### Change Notifications
Can be added to workflow:
- Slack notifications
- Email alerts
- Discord webhooks
- Custom notifications

### Alternative Branches
Can push to different branch (e.g., `jobs-data`):
```yaml
git checkout -b jobs-data || git checkout jobs-data
```

### Conditional Steps
Can run additional steps based on results:
- Send email only if new jobs found
- Post to social media if count exceeds threshold
- Archive old data

### Scheduled Reports
Can add summary reports (e.g., weekly stats):
- Total new jobs this week
- Average salary by role
- Companies with most openings

## Logs & Debugging

### View Workflow Logs
1. Go to **Actions** tab
2. Click **Fetch Designer Jobs Daily**
3. Click specific workflow run
4. Expand each step to see full output

### Common Log Messages
```
✅ Fetching page 1...
  Found 20 jobs on page 1
Fetching page 2...
  Found 20 jobs on page 2
...
Saved 3 new designer jobs to CSV
```

### Debug Mode
To see more detailed logs, add to workflow:
```yaml
- run: python scripts/fetch_creative_circle.py
  env:
    PYTHONUNBUFFERED: 1
    LOGLEVEL: DEBUG
```

## Maintenance

### Annual Review
- Check if schedule still makes sense
- Verify no new dependencies needed
- Test manual run if long time since last execution

### Updating Python Version
Edit workflow to change Python version:
```yaml
- uses: actions/setup-python@v4
  with:
    python-version: '3.12'  # Change this
```

### Updating Schedule
Edit cron expression in workflow file:
```yaml
schedule:
  - cron: '0 0 * * *'  # Modify this line
```

---

**Created:** 2026-01-28  
**Status:** ✅ Production Ready
