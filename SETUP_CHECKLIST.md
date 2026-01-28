# GitHub Actions Setup Checklist

Follow these steps to enable daily automated job fetching in your GitHub repository.

## Setup Steps

- [ ] **Step 1: Push code to GitHub**
  ```bash
  git add .
  git commit -m "feat: add GitHub Actions workflow for daily job fetching"
  git push origin main
  ```

- [ ] **Step 2: Enable GitHub Actions** (if not already enabled)
  - Go to your repository on GitHub
  - Click **Settings** → **Actions** → **General**
  - Under "Actions permissions", select **Allow all actions and reusable workflows**
  - Click **Save**

- [ ] **Step 3: Verify workflow file exists**
  - In your GitHub repository, navigate to `.github/workflows/`
  - Confirm `fetch-designer-jobs.yml` is present

- [ ] **Step 4: Test the workflow** (optional)
  - Go to **Actions** tab on GitHub
  - Click **Fetch Designer Jobs Daily**
  - Click **Run workflow** → **Run workflow**
  - Monitor the run in real-time

- [ ] **Step 5: Check workflow results**
  - After first run, go to **Actions** tab
  - Click the workflow run
  - Check **Summary** for job count and status
  - Verify `data/designer_jobs.csv` was committed (if new jobs found)

## What Happens Automatically

✅ **Daily at Midnight UTC:**
1. GitHub Actions checks out your code
2. Sets up Python 3.11 environment
3. Installs dependencies (`pip install -e .`)
4. Runs `python scripts/fetch_creative_circle.py`
   - Fetches jobs from Creative Circle API
   - Filters for active designer positions
   - Appends new jobs to `data/designer_jobs.csv`
   - Skips duplicates automatically
5. Detects if new jobs were added
6. If new jobs found:
   - Creates a Git commit with timestamp
   - Pushes changes back to repository
7. Displays summary (total jobs, status, etc.)

## Workflow Configuration

**Current Schedule:** Daily at midnight UTC (`0 0 * * *`)

To change the schedule, edit `.github/workflows/fetch-designer-jobs.yml`:

```yaml
on:
  schedule:
    - cron: '0 0 * * *'  # Change this cron expression
```

**Common cron examples:**
- `0 9 * * *` — 9 AM UTC
- `0 0 * * 1-5` — Weekdays at midnight UTC
- `0 */6 * * *` — Every 6 hours
- `30 8 * * *` — 8:30 AM UTC

## File Structure

```
.github/
└── workflows/
    └── fetch-designer-jobs.yml          # The workflow (created ✅)

data/
└── designer_jobs.csv                    # Updated daily with new jobs

GITHUB_ACTIONS.md                        # Detailed setup guide
```

## Monitoring

### View Workflow Runs
1. Go to your repository
2. Click **Actions** tab
3. Click **Fetch Designer Jobs Daily**
4. See all past and current workflow runs

### Get Notifications
- GitHub will email you if the workflow fails
- Check repository for new commits (jobs were added)

### Manual Trigger
To run the workflow anytime (useful for testing):
1. Go to **Actions** tab
2. Select **Fetch Designer Jobs Daily**
3. Click **Run workflow** button

## Troubleshooting

### Workflow Not Running

**Problem:** No scheduled runs showing up
- **Solution 1:** Wait for the next scheduled time (cron runs UTC)
- **Solution 2:** Manually trigger with `workflow_dispatch` to test
- **Solution 3:** Ensure Settings → Actions is enabled

### Workflow Fails

**Problem:** Red ❌ on workflow run
- **Solution:** Click the failed run and check logs for error details
- Common issues:
  - Python package import errors → Check `pip install -e .` output
  - Git push failures → Check branch protection rules
  - API failures → Creative Circle API might be down

### No New Commits

**Problem:** Workflow runs successfully but doesn't commit changes
- **Expected:** This happens when no new designer jobs are found
- **To verify:** Check the workflow run Summary tab
- **To test:** Manually run `python scripts/fetch_creative_circle.py` locally

## Customization

See [GITHUB_ACTIONS.md](../GITHUB_ACTIONS.md) for:
- Changing the schedule
- Adding Slack/email notifications
- Running on specific branches
- Adding custom environment variables
- Advanced debugging

## Support & Documentation

- **Setup Guide:** [GITHUB_ACTIONS.md](../GITHUB_ACTIONS.md)
- **Script Details:** [README.md](../README.md)
- **GitHub Actions Docs:** https://docs.github.com/actions
- **Cron Syntax:** https://crontab.guru/

---

**Status:** ✅ Ready to deploy  
**Last updated:** 2026-01-28
