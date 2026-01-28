# GitHub Actions Setup Guide

This guide explains how to set up and configure the daily job fetching workflow for your repository.

## Overview

The workflow (`.github/workflows/fetch-designer-jobs.yml`) automatically:
- Runs **every day at midnight UTC** (configurable)
- Fetches new designer jobs from Creative Circle API
- Automatically appends new jobs to `data/designer_jobs.csv`
- Commits changes back to the repository with a timestamp
- Provides a summary of results in the GitHub Actions logs

## Quick Setup

### 1. Enable GitHub Actions

1. Go to your GitHub repository
2. Click **Settings** → **Actions** → **General**
3. Under "Actions permissions", select **Allow all actions and reusable workflows**
4. Click **Save**

### 2. Ensure `.env` is configured (optional)

The workflow uses default environment variables. If you want custom values, you can edit `.env.example` and commit it:

```bash
# Configure in .env.example
DESIGNER_CSV_FILE=designer_jobs.csv
DATA_DIR=./data
DESIGNER_JOB_KEYWORDS=designer,ui,ux,graphic,visual,web
```

### 3. Commit and Push

```bash
git add .github/workflows/fetch-designer-jobs.yml
git commit -m "chore: add daily job fetching workflow"
git push
```

That's it! The workflow will now run automatically.

## Schedule Options

To change the run schedule, edit `.github/workflows/fetch-designer-jobs.yml`:

### Daily at Midnight UTC (Current)
```yaml
schedule:
  - cron: '0 0 * * *'
```

### Daily at 9 AM UTC
```yaml
schedule:
  - cron: '0 9 * * *'
```

### Every 6 hours
```yaml
schedule:
  - cron: '0 */6 * * *'
```

### Every weekday at 8 AM UTC
```yaml
schedule:
  - cron: '0 8 * * 1-5'
```

> **Timezone Note**: GitHub Actions uses UTC time. Adjust the hour value accordingly for your timezone.

## Running Manually

You can manually trigger the workflow anytime (useful for testing):

1. Go to **Actions** tab in your GitHub repository
2. Select **Fetch Designer Jobs Daily** workflow
3. Click **Run workflow** → **Run workflow**

## What the Workflow Does

1. **Checkout code** — Pulls the latest repository version
2. **Set up Python** — Installs Python 3.11 with pip caching
3. **Install dependencies** — Runs `pip install -e .`
4. **Fetch jobs** — Executes `python scripts/fetch_creative_circle.py`
   - Queries Creative Circle API
   - Filters for active designer jobs
   - Appends new jobs to `data/designer_jobs.csv`
   - Skips duplicates automatically
5. **Check for changes** — Detects if new jobs were added
6. **Commit changes** — If new jobs found:
   - Creates a Git commit with timestamp
   - Pushes changes back to the repository
7. **Summary** — Logs total job count and status

## GitHub Secrets (If Needed)

If Creative Circle API requires authentication, you can add secrets:

1. Go to **Settings** → **Secrets and variables** → **Actions**
2. Click **New repository secret**
3. Add secret (e.g., `CREATIVE_CIRCLE_API_KEY=your_key`)
4. Use in workflow:
   ```yaml
   env:
     CREATIVE_CIRCLE_API_KEY: ${{ secrets.CREATIVE_CIRCLE_API_KEY }}
   ```

> **Current status**: The Creative Circle API is public, so no API key is needed.

## Monitoring the Workflow

### View Workflow Runs

1. Go to your repository **Actions** tab
2. Select **Fetch Designer Jobs Daily** 
3. Click on a workflow run to see detailed logs

### Workflow Artifacts

Check the **Summary** tab after each run to see:
- Total jobs in database
- Whether new jobs were found
- Commit message with timestamp

### Notifications

GitHub will notify you of:
- Workflow failures (check logs to troubleshoot)
- Successful runs with new commits

## Troubleshooting

### Workflow Not Running

- **Check**: Settings → Actions → Ensure "Allow all actions" is enabled
- **Check**: `.github/workflows/fetch-designer-jobs.yml` exists and is syntactically correct
- **Check**: Repository has at least one commit after adding the workflow file

### Jobs Not Being Committed

- **Reason**: No new jobs found (script ran successfully but found 0 new designer jobs)
- **Solution**: Manually run with `workflow_dispatch` to test

### Git Push Fails

- **Reason**: Insufficient permissions or branch protection rules
- **Solution**: Ensure the workflow has push permissions (default GitHub token)

## Customization Examples

### Add Slack Notifications

Add to workflow (requires Slack webhook secret):

```yaml
- name: Notify Slack
  if: steps.check_changes.outputs.has_changes == 'true'
  run: |
    curl -X POST ${{ secrets.SLACK_WEBHOOK }} \
      -H 'Content-Type: application/json' \
      -d '{"text":"New designer jobs found and added to CSV!"}'
```

### Add Email Notification

Use GitHub's action (requires setup):

```yaml
- name: Send email notification
  if: steps.check_changes.outputs.has_changes == 'true'
  uses: dawidd6/action-send-mail@v3
  with:
    server_address: ${{ secrets.EMAIL_SERVER }}
    server_port: 465
    username: ${{ secrets.EMAIL_USERNAME }}
    password: ${{ secrets.EMAIL_PASSWORD }}
    subject: 'New Designer Jobs Found!'
    to: your-email@example.com
    from: 'GitHub Actions'
    body: 'Check the repository for new designer job listings.'
```

### Add to Different Branch

To push to a different branch (e.g., `jobs-data`):

```yaml
- name: Commit and push changes
  if: steps.check_changes.outputs.has_changes == 'true'
  run: |
    git config user.name "github-actions[bot]"
    git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
    git checkout -b jobs-data || git checkout jobs-data
    git add data/designer_jobs.csv
    git commit -m "chore: update designer jobs - $(date -u +'%Y-%m-%d %H:%M:%S')"
    git push origin jobs-data
```

## Maintenance

### Backup CSV Locally

The CSV is safely stored in the repository. To back it up:

```bash
git clone <your-repo-url>
cp JobSearch/data/designer_jobs.csv ~/backup/designer_jobs.csv
```

### Monitor Job Count

Use GitHub's built-in query to see commit history:

```bash
git log --oneline --grep="update designer jobs" | wc -l
```

## Support

For issues or questions:
1. Check GitHub Actions logs for error messages
2. Review the workflow YAML syntax
3. Test locally with `python scripts/fetch_creative_circle.py`

---

**Last updated**: 2026-01-28
