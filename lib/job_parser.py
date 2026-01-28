"""Job listing parsing and filtering utilities."""
import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class Job:
    """Represents a job listing."""

    def __init__(
        self,
        job_id: str,
        title: str,
        company: str,
        url: str,
        source: str,
        location: Optional[str] = None,
        salary_min: Optional[int] = None,
        salary_max: Optional[int] = None,
        job_type: Optional[str] = None,
        description: Optional[str] = None,
        posted_date: Optional[str] = None,
        fetched_at: Optional[str] = None,
    ):
        """Initialize a Job object."""
        self.job_id = job_id
        self.title = title
        self.company = company
        self.url = url
        self.source = source
        self.location = location
        self.salary_min = salary_min
        self.salary_max = salary_max
        self.job_type = job_type
        self.description = description
        self.posted_date = posted_date
        self.fetched_at = fetched_at or datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        """Convert job to dictionary."""
        return {
            "job_id": self.job_id,
            "title": self.title,
            "company": self.company,
            "url": self.url,
            "source": self.source,
            "location": self.location,
            "salary_min": self.salary_min,
            "salary_max": self.salary_max,
            "job_type": self.job_type,
            "description": self.description,
            "posted_date": self.posted_date,
            "fetched_at": self.fetched_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Job":
        """Create Job from dictionary."""
        return cls(
            job_id=data.get("job_id"),
            title=data.get("title"),
            company=data.get("company"),
            url=data.get("url"),
            source=data.get("source"),
            location=data.get("location"),
            salary_min=data.get("salary_min"),
            salary_max=data.get("salary_max"),
            job_type=data.get("job_type"),
            description=data.get("description"),
            posted_date=data.get("posted_date"),
            fetched_at=data.get("fetched_at"),
        )


class JobFilter:
    """Filter jobs by criteria."""

    def __init__(
        self,
        keywords: Optional[List[str]] = None,
        min_salary: Optional[int] = None,
        locations: Optional[List[str]] = None,
    ):
        """
        Initialize job filter.

        Args:
            keywords: Job title/description keywords to match.
            min_salary: Minimum salary threshold.
            locations: Allowed locations (case-insensitive substring match).
        """
        self.keywords = [k.lower() for k in keywords] if keywords else []
        self.min_salary = min_salary
        self.locations = [l.lower() for l in locations] if locations else []

    def matches(self, job: Job) -> bool:
        """Check if job matches filter criteria."""
        # Check keywords
        if self.keywords:
            text_to_search = (
                f"{job.title} {job.description or ''}".lower()
            )
            if not any(kw in text_to_search for kw in self.keywords):
                return False

        # Check min salary
        if self.min_salary and job.salary_min:
            if job.salary_min < self.min_salary:
                return False

        # Check locations
        if self.locations and job.location:
            location_lower = job.location.lower()
            if not any(loc in location_lower for loc in self.locations):
                return False

        return True
