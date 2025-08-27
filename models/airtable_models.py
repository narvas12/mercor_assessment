from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from datetime import datetime

@dataclass
class PersonalDetails:
    applicant_id: str
    full_name: str
    email: str
    location: str
    linkedin: Optional[str] = None
    record_id: Optional[str] = None

@dataclass
class WorkExperience:
    applicant_id: str
    company: str
    title: str
    start_date: str
    end_date: Optional[str] = None
    technologies: Optional[List[str]] = None
    record_id: Optional[str] = None

@dataclass
class SalaryPreferences:
    applicant_id: str
    preferred_rate: float
    minimum_rate: float
    currency: str
    availability: int
    record_id: Optional[str] = None

@dataclass
class Applicant:
    applicant_id: str
    compressed_json: Optional[Dict[str, Any]] = None
    shortlist_status: Optional[str] = None
    llm_summary: Optional[str] = None
    llm_score: Optional[int] = None
    llm_follow_ups: Optional[List[str]] = None
    record_id: Optional[str] = None

@dataclass
class ShortlistedLead:
    applicant_id: str
    compressed_json: Dict[str, Any]
    score_reason: str
    created_at: datetime
    record_id: Optional[str] = None

def applicant_from_dict(data: Dict[str, Any]) -> Applicant:
    return Applicant(
        applicant_id=data.get('Applicant ID'),
        compressed_json=data.get('Compressed JSON'),
        shortlist_status=data.get('Shortlist Status'),
        llm_summary=data.get('LLM Summary'),
        llm_score=data.get('LLM Score'),
        llm_follow_ups=data.get('LLM Follow-Ups'),
        record_id=data.get('id')
    )

def personal_details_from_dict(data: Dict[str, Any]) -> PersonalDetails:
    return PersonalDetails(
        applicant_id=data.get('Applicant ID')[0] if data.get('Applicant ID') else '',
        full_name=data.get('Full Name'),
        email=data.get('Email'),
        location=data.get('Location'),
        linkedin=data.get('LinkedIn'),
        record_id=data.get('id')
    )

def work_experience_from_dict(data: Dict[str, Any]) -> WorkExperience:
    return WorkExperience(
        applicant_id=data.get('Applicant ID')[0] if data.get('Applicant ID') else '',
        company=data.get('Company'),
        title=data.get('Title'),
        start_date=data.get('Start'),
        end_date=data.get('End'),
        technologies=data.get('Technologies'),
        record_id=data.get('id')
    )

def salary_preferences_from_dict(data: Dict[str, Any]) -> SalaryPreferences:
    return SalaryPreferences(
        applicant_id=data.get('Applicant ID')[0] if data.get('Applicant ID') else '',
        preferred_rate=data.get('Preferred Rate'),
        minimum_rate=data.get('Minimum Rate'),
        currency=data.get('Currency'),
        availability=data.get('Availability'),
        record_id=data.get('id')
    )