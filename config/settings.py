# config/settings.py
from decouple import config, Csv
from datetime import datetime
import os

# Airtable Configuration
AIRTABLE_API_KEY = config('AIRTABLE_API_KEY', default='')
AIRTABLE_BASE_ID = config('AIRTABLE_BASE_ID', default='')

# Table Names (use exact names or IDs)
APPLICANTS_TABLE = 'tbl1dM90vNx9iWU5c'   # Applicants (Main Table)
PERSONAL_DETAILS_TABLE = 'tbliQIuyagwYx85I2'
WORK_EXPERIENCE_TABLE = 'tblC7e5XeQT22Lc9q'
SALARY_PREFERENCES_TABLE = 'tbltZZEsH06HwUcVH'
SHORTLISTED_LEADS_TABLE = 'tblmNFvsGEVYyRgHY'


# LLM Configuration
LLM_PROVIDER = config('LLM_PROVIDER', default='openai')  # openai, anthropic, gemini
OPENAI_API_KEY = config('OPENAI_API_KEY', default='')


# Shortlisting Criteria
TIER_1_COMPANIES = config('TIER_1_COMPANIES', default='Google,Meta,OpenAI,Microsoft,Apple,Amazon,Netflix', cast=Csv())
ELIGIBLE_LOCATIONS = config('ELIGIBLE_LOCATIONS', default='US,USA,United States,Canada,UK,United Kingdom,Germany,India', cast=Csv())
MAX_HOURLY_RATE = config('MAX_HOURLY_RATE', default=100, cast=int)  # USD
MIN_AVAILABILITY = config('MIN_AVAILABILITY', default=20, cast=int)  # hours/week
MIN_EXPERIENCE = config('MIN_EXPERIENCE', default=4, cast=int)  # years

# API Settings
MAX_RETRIES = config('MAX_RETRIES', default=3, cast=int)
RETRY_BACKOFF = config('RETRY_BACKOFF', default=2, cast=int)  # seconds

# Debug settings
DEBUG = config('DEBUG', default=False, cast=bool)