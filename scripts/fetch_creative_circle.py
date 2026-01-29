#!/usr/bin/env python3
"""
Creative Circle Job Fetcher for Designer Olga

Fetches design-related job listings from Creative Circle job board.
Filters by 'designer' in job title and saves results to CSV.
"""

import json
import logging
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# Add parent dir to path to import lib modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from lib.api_client import APIClient
from lib.job_csv import JobCSVWriter

# Configure logging with both console and file output
log_dir = Path(os.getenv("LOG_DIR", "./logs"))
log_dir.mkdir(parents=True, exist_ok=True)
log_file = log_dir / f"fetch_creative_circle_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

# Configure root logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler(),
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Creative Circle API Constants
CREATIVE_CIRCLE_API_BASE = "https://candidateportal.creativecircle.com"
CREATIVE_CIRCLE_SEARCH_ENDPOINT = f"{CREATIVE_CIRCLE_API_BASE}/ccv5-jobs/search"
CREATIVE_CIRCLE_DETAILS_ENDPOINT = f"{CREATIVE_CIRCLE_API_BASE}/ccv5-jobs/details"
CREATIVE_CIRCLE_JOB_URL_BASE = "https://candidateportal.creativecircle.com/job-detail"


class CreativeCircleFetcher:
    """Fetch designer jobs from Creative Circle API."""

    def __init__(self):
        """Initialize fetcher for Creative Circle."""
        self.data_dir = Path(os.getenv("DATA_DIR", "./data"))
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # CSV output file for designer jobs
        csv_filename = os.getenv("DESIGNER_CSV_FILE", "designer_jobs.csv")
        self.csv_file = self.data_dir / csv_filename
        self.csv_writer = JobCSVWriter(str(self.csv_file))

    def fetch_jobs(
        self, pages: int = 5, work_location_type_id: int = 3, buid: int = 3
    ) -> Dict[str, Any]:
        """
        Fetch designer jobs from Creative Circle API (remote only).

        Args:
            pages: Number of pages to fetch (20 jobs per page).
            work_location_type_id: 3 = Remote, 1 = On-site, etc.
            buid: Business unit ID (3 = Creative Circle).

        Returns:
            Dictionary with stats: {total_fetched, designer_jobs, new_jobs, csv_file}.
        """
        all_jobs = []
        designer_jobs = []
        existing_ids = self.csv_writer.get_existing_job_ids()
        
        logger.info(f"Starting fetch: {pages} pages, work location type {work_location_type_id}")
        logger.info(f"Existing job IDs in CSV: {len(existing_ids)}")
        
        for page in range(1, pages + 1):
            logger.info(f"Fetching page {page}...")
            
            try:
                # Fetch job listing page
                params = {
                    "rows": 20,
                    "page": page,
                    "sortType": "date",
                    "workLocationTypeId": work_location_type_id,
                    "daysPosted": 0,
                    "buid": buid,
                }
                
                # Add User-Agent to bypass basic IP blocks
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                }
                
                response = requests.get(
                    CREATIVE_CIRCLE_SEARCH_ENDPOINT, params=params, headers=headers, timeout=10
                )
                response.raise_for_status()
                data = response.json()
                
                jobs = data.get("jobs", [])
                logger.info(f"  Found {len(jobs)} jobs on page {page}")
                
                # Filter for designer jobs
                for job in jobs:
                    job_title = job.get("jobTitle", "").lower()
                    
                    # Check if 'designer' appears in job title
                    if "designer" in job_title:
                        job_id = job.get("Id")
                        
                        # Skip if already in CSV
                        if job_id in existing_ids:
                            logger.debug(f"  Skipping duplicate job ID: {job_id}")
                            continue
                        
                        # Check if job is still active by fetching details
                        if not self._is_job_active(job_id):
                            logger.debug(f"  Skipping inactive job ID: {job_id}")
                            continue
                        
                        designer_jobs.append(job)
                        all_jobs.append(job)
                
            except Exception as e:
                logger.error(f"Error fetching page {page}: {e}")
                continue
        
        # Convert API response to CSV format and save
        csv_rows = [self._format_job_for_csv(job) for job in designer_jobs]
        
        if csv_rows:
            # Append new jobs to CSV
            self.csv_writer.append_jobs(csv_rows)
            logger.info(f"Appended {len(csv_rows)} new designer jobs to CSV")
            
            # Read all jobs from CSV
            all_jobs_in_csv = self.csv_writer.read_jobs()
            
            # Sort by job_id descending
            all_jobs_in_csv.sort(
                key=lambda x: int(x.get("job_id", 0)) if x.get("job_id") else 0,
                reverse=True
            )
            
            # Write sorted jobs back to CSV
            self.csv_writer.write_jobs(all_jobs_in_csv)
            logger.info(f"Rewrote CSV with {len(all_jobs_in_csv)} jobs sorted by job_id DESC")
        
        return {
            "total_fetched": len(all_jobs),
            "designer_jobs_found": len(designer_jobs),
            "csv_file": str(self.csv_file),
        }

    def _format_job_for_csv(self, job_api_response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert API job response to CSV row format.

        Args:
            job_api_response: Raw API response for a job.

        Returns:
            Dictionary with CSV column names as keys.
        """
        job_id = job_api_response.get("Id", "")
        
        # Build job URL: https://candidateportal.creativecircle.com/job-detail/[jobID]
        full_url = f"{CREATIVE_CIRCLE_JOB_URL_BASE}/{job_id}" if job_id else ""
        
        # Format location: City, State (or mark as Remote if location type is 3)
        cities = job_api_response.get("City", [])
        states = job_api_response.get("StateCode", [])
        
        if cities and states:
            location = f"{', '.join(cities)}, {', '.join(states)}"
        else:
            location = "Remote"
        
        # Skills/tags
        tags = job_api_response.get("tags", [])
        skills_tags = ", ".join(tags) if tags else ""
        
        # Posted date format
        posted_date = job_api_response.get("DatePost", "")
        if posted_date:
            # Convert ISO format to readable date
            try:
                dt = datetime.fromisoformat(posted_date.replace("Z", "+00:00"))
                posted_date = dt.strftime("%Y-%m-%d %H:%M")
            except Exception:
                pass
        
        # Short description (first 200 chars of job description after cleaning)
        short_desc = job_api_response.get("ShortDescription", "")
        
        # Clean CSS styling from description first, then truncate
        short_desc = self._clean_description(short_desc)[:200]
        
        return {
            "job_id": job_id,
            "job_title": job_api_response.get("jobTitle", ""),
            "company_name": job_api_response.get("CompanyName", ""),
            "location": location,
            "hourly_min": job_api_response.get("HourlyMin", ""),
            "hourly_max": job_api_response.get("HourlyMax", ""),
            "salary_type": job_api_response.get("SalaryType", ""),
            "job_type": self._get_job_type(job_api_response),
            "recruiter_name": job_api_response.get("RecruiterName", ""),
            "recruiter_email": "",  # Not in search response, need details endpoint
            "posted_date": posted_date,
            "description_short": short_desc,
            "skills_tags": skills_tags,
            "url": full_url,
        }

    def _get_job_type(self, job_data: Dict[str, Any]) -> str:
        """
        Extract job type (Contract, Permanent, etc.) from job data.

        Args:
            job_data: Job dictionary from API.

        Returns:
            Job type string.
        """
        tax_term = job_data.get("TaxTerm", "")
        
        # Map tax terms to job types
        tax_term_map = {
            "CONT": "Contract",
            "PERM": "Permanent",
            "TEMP": "Temporary",
            "FT": "Full-time",
            "PT": "Part-time",
        }
        
        return tax_term_map.get(tax_term, tax_term or "Unknown")

    def _is_job_active(self, job_id: str) -> bool:
        """
        Check if a job is still active by fetching its details.

        Args:
            job_id: Creative Circle job ID.

        Returns:
            True if job is active, False otherwise.
        """
        try:
            params = {"id": job_id, "buid": 3}
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            response = requests.get(
                CREATIVE_CIRCLE_DETAILS_ENDPOINT, params=params, headers=headers, timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            is_active = data.get("isActive", False)
            return is_active
            
        except Exception as e:
            logger.warning(f"Error checking if job {job_id} is active: {e}")
            # If we can't determine, assume it's active to be safe
            return True

    def _clean_description(self, text: str) -> str:
        """
        Remove CSS styling and HTML artifacts from job description.

        Args:
            text: Raw description text possibly containing CSS.

        Returns:
            Cleaned description text.
        """
        # Use BeautifulSoup to strip HTML tags and get text
        soup = BeautifulSoup(text, 'html.parser')
        
        # Remove style tags
        for style in soup.find_all('style'):
            style.decompose()
        
        # Get clean text
        clean_text = soup.get_text(separator=' ')
        
        # Remove CSS-like patterns (word { ... }, tr th { ... }, etc.)
        # This handles nested braces and multiple selectors
        clean_text = re.sub(r'[a-z\s,]+\s*{[^}]*}', '', clean_text, flags=re.IGNORECASE)
        
        # Remove remaining single-letter CSS selectors followed by spaces
        clean_text = re.sub(r'\b[a-z]\s+(?=\w)', '', clean_text, flags=re.IGNORECASE)
        
        # Remove multiple consecutive spaces
        clean_text = re.sub(r'\s+', ' ', clean_text)
        
        # Strip leading/trailing whitespace
        clean_text = clean_text.strip()
        
        return clean_text

    def close(self):
        """Close any resources."""
        pass


def main():
    """Main entry point."""
    logger.info("Starting Creative Circle job fetcher for designer Olga")
    
    fetcher = CreativeCircleFetcher()
    
    try:
        # Fetch designer jobs from Creative Circle (remote only, pages 1-5)
        results = fetcher.fetch_jobs(pages=5)
        
        print("\n" + "=" * 80)
        print("CREATIVE CIRCLE DESIGNER JOB FETCH RESULTS")
        print("=" * 80)
        print(f"Total jobs fetched:      {results['total_fetched']}")
        print(f"Designer jobs found:     {results['designer_jobs_found']}")
        print(f"CSV file:                {results['csv_file']}")
        print("=" * 80 + "\n")
        
        if results["designer_jobs_found"] > 0:
            # Read and display summary (already sorted by fetch_jobs)
            csv_writer = JobCSVWriter(results["csv_file"])
            all_jobs = csv_writer.read_jobs()
            
            print(f"✓ Successfully saved {len(all_jobs)} designer jobs to CSV\n")
            print("Top 5 newest designer jobs (sorted by job ID DESC):")
            for i, job in enumerate(all_jobs[:5], 1):
                print(f"\n{i}. {job['job_title']} @ {job['company_name']}")
                print(f"   Location: {job['location']}")
                print(f"   Rate: ${job['hourly_min']} - ${job['hourly_max']}/hr")
                print(f"   Posted: {job['posted_date']}")
                print(f"   URL: {job['url']}")
        else:
            logger.warning("No designer jobs found in this fetch")
            print("No designer jobs found in this fetch.")
            
    except Exception as e:
        logger.error(f"Error during job fetch: {e}", exc_info=True)
        sys.exit(1)
    finally:
        fetcher.close()


if __name__ == "__main__":
    main()
