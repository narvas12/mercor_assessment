import os
import json
import requests
import time
from typing import List, Dict, Any, Optional
from requests.exceptions import RequestException

from config import settings

class AirtableClient:
    def __init__(self):
        self.api_key = settings.AIRTABLE_API_KEY
        self.base_id = settings.AIRTABLE_BASE_ID
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        self.base_url = f'https://api.airtable.com/v0/{self.base_id}'

    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None, params: Optional[Dict] = None):
        url = f'{self.base_url}/{endpoint}'
        
        for attempt in range(settings.MAX_RETRIES):
            try:
                response = requests.request(
                    method=method,
                    url=url,
                    headers=self.headers,
                    json=data,
                    params=params,
                    timeout=30
                )
                response.raise_for_status()
                return response.json()
            except RequestException as e:
                if attempt == settings.MAX_RETRIES - 1:
                    raise e
                time.sleep(min(settings.RETRY_BACKOFF ** attempt, 60))  # capped backoff
    
    def get_records(self, table_name: str, filter_formula: Optional[str] = None) -> List[Dict]:
        records = []
        params = {}
        
        if filter_formula:
            params['filterByFormula'] = filter_formula
            
        while True:
            response = self._make_request('GET', table_name, params=params)
            records.extend(response.get('records', []))
            
            if 'offset' in response:
                params['offset'] = response['offset']
            else:
                break
                
        return records

    def get_record(self, table_name: str, record_id: str) -> Dict:
        return self._make_request('GET', f'{table_name}/{record_id}')

    def create_record(self, table_name: str, data: Dict) -> Dict:
        return self._make_request('POST', table_name, data={'fields': data})

    def update_record(self, table_name: str, record_id: str, data: Dict) -> Dict:
        return self._make_request('PATCH', f'{table_name}/{record_id}', data={'fields': data})

    def delete_record(self, table_name: str, record_id: str) -> Dict:
        return self._make_request('DELETE', f'{table_name}/{record_id}')
    
    def find_record_by_field(self, table_name: str, field_name: str, field_value: str) -> Optional[Dict]:
        """Find the first record in a table where field_name == field_value"""
        formula = f"{{{field_name}}} = '{field_value}'"
        records = self.get_records(table_name, filter_formula=formula)
        return records[0] if records else None

    def get_applicant_data(self, applicant_id: str) -> Dict[str, Any]:
        # Applicant record
        applicant_records = self.get_records(
            settings.APPLICANTS_TABLE, 
            filter_formula=f"{{Applicant ID}} = '{applicant_id}'"
        )
        if not applicant_records:
            raise ValueError(f"Applicant with ID {applicant_id} not found")
            
        applicant_data = applicant_records[0]['fields']
        
        # Linked tables
        personal_details = {}
        personal_details_records = self.get_records(
            settings.PERSONAL_DETAILS_TABLE,
            filter_formula=f"{{Applicant ID}} = '{applicant_id}'"
        )
        if personal_details_records:
            personal_details = personal_details_records[0]['fields']
        
        work_experience_records = self.get_records(
            settings.WORK_EXPERIENCE_TABLE,
            filter_formula=f"{{Applicant ID}} = '{applicant_id}'"
        )
        work_experience = [record['fields'] for record in work_experience_records]
        
        salary_preferences = {}
        salary_preferences_records = self.get_records(
            settings.SALARY_PREFERENCES_TABLE,
            filter_formula=f"{{Applicant ID}} = '{applicant_id}'"
        )
        if salary_preferences_records:
            salary_preferences = salary_preferences_records[0]['fields']
        
        return {
            'applicant': applicant_data,
            'personal_details': personal_details,
            'work_experience': work_experience,
            'salary_preferences': salary_preferences
        }

    def update_applicant_json(self, applicant_id: str, compressed_json: Dict):
        applicant_records = self.get_records(
            settings.APPLICANTS_TABLE,
            filter_formula=f"{{Applicant ID}} = '{applicant_id}'"
        )
        
        if applicant_records:
            record_id = applicant_records[0]['id']
            self.update_record(
                settings.APPLICANTS_TABLE,
                record_id,
                {'Compressed JSON': json.dumps(compressed_json)}  # store as JSON string
            )
