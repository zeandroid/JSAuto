"""CSV utilities for saving job listings."""
import csv
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# CSV column headers for job listings
CSV_HEADERS = [
    "job_id",
    "job_title",
    "company_name",
    "location",
    "hourly_min",
    "hourly_max",
    "salary_type",
    "job_type",
    "recruiter_name",
    "recruiter_email",
    "posted_date",
    "description_short",
    "skills_tags",
    "url",
]


class JobCSVWriter:
    """Handle reading/writing job listings to CSV with append functionality."""

    def __init__(self, filepath: str):
        """
        Initialize CSV writer.

        Args:
            filepath: Path to CSV file (created if doesn't exist).
        """
        self.filepath = Path(filepath)
        self._ensure_headers()

    def _ensure_headers(self):
        """Create CSV file with headers if it doesn't exist."""
        if not self.filepath.exists():
            logger.info(f"Creating new CSV file: {self.filepath}")
            with open(self.filepath, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)
                writer.writeheader()

    def append_job(self, job_dict: Dict[str, Any]) -> None:
        """
        Append a single job to the CSV file.

        Args:
            job_dict: Dictionary with job data (keys should match CSV_HEADERS).
        """
        with open(self.filepath, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)
            
            # Extract only the columns we need
            row = {key: job_dict.get(key, "") for key in CSV_HEADERS}
            writer.writerow(row)

    def append_jobs(self, jobs: List[Dict[str, Any]]) -> None:
        """
        Append multiple jobs to the CSV file.

        Args:
            jobs: List of dictionaries with job data.
        """
        with open(self.filepath, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)
            
            for job_dict in jobs:
                row = {key: job_dict.get(key, "") for key in CSV_HEADERS}
                writer.writerow(row)
        
        logger.info(f"Appended {len(jobs)} jobs to {self.filepath}")

    def read_jobs(self) -> List[Dict[str, Any]]:
        """
        Read all jobs from CSV file.

        Returns:
            List of dictionaries, one per job row.
        """
        if not self.filepath.exists():
            return []
        
        jobs = []
        with open(self.filepath, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            jobs = list(reader)
        
        return jobs

    def get_existing_job_ids(self) -> set:
        """
        Get set of job IDs already in CSV (for duplicate detection).

        Returns:
            Set of job_id values.
        """
        jobs = self.read_jobs()
        return {job.get("job_id", "") for job in jobs if job.get("job_id")}
