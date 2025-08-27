#!/usr/bin/env python3
"""
LLM Evaluation Script
Uses LLM to evaluate, enrich, and sanity-check each application
"""

import sys
import argparse
import json
from typing import Dict, Any

# Add the parent directory to the path to import modules
sys.path.append('../')

from utils.airtable_client import AirtableClient
from utils.llm_client import LLMClient
from config import settings


def evaluate_applicants():
    """Evaluate all applicants using LLM"""
    client = AirtableClient()
    llm_client = LLMClient()
    
    print("Fetching applicants from Airtable...")
    applicants = client.get_records(settings.APPLICANTS_TABLE)
    print(f"Retrieved {len(applicants)} applicants from Airtable")

    evaluated_count = 0
    
    for applicant in applicants:
        applicant_id = applicant['fields'].get('Applicant ID')
        print(f"\nProcessing applicant: {applicant_id}")

        if not applicant_id:
            print("Skipping record: No Applicant ID found")
            continue
        
        # Skip if already evaluated and JSON hasn't changed
        compressed_json = applicant['fields'].get('Compressed JSON')
        if (applicant['fields'].get('LLM Score') and 
            applicant['fields'].get('Compressed JSON') == compressed_json):
            print(f"⏭ Skipping applicant {applicant_id}: Already evaluated")
            continue
        
        # Get applicant data
        try:
            print(f"Fetching detailed applicant data for {applicant_id}...")
            applicant_data = client.get_applicant_data(applicant_id)
            compressed_json_str = applicant_data['applicant'].get('Compressed JSON', '{}')
            compressed_data = json.loads(compressed_json_str.replace("'", '"'))
            print(f"Applicant data loaded for {applicant_id}")
        except Exception as e:
            print(f"Error getting data for applicant {applicant_id}: {e}")
            continue
        
        # Evaluate with LLM
        try:
            print(f"Sending applicant {applicant_id} data to LLM for evaluation...")
            evaluation = llm_client.evaluate_applicant(compressed_data)

            # Build Airtable-safe payload
            update_payload = {
                'LLM Summary': str(evaluation.get('summary', '')),
                'LLM Score': float(evaluation.get('score', 0)),
                'LLM Follow-Ups': "\n".join(map(str, evaluation.get('follow_ups', [])))
            }

            # Debug log
            print(f"Updating Airtable record for {applicant_id} with: {update_payload}")
            
            # Update applicant record
            client.update_record(
                settings.APPLICANTS_TABLE,
                applicant['id'],
                update_payload
            )
            
            evaluated_count += 1
            print(f"Applicant {applicant_id} evaluated successfully - Score: {evaluation['score']}")
            
        except Exception as e:
            print(f"Error evaluating applicant {applicant_id}: {e}")
            continue
    
    print(f"\nFinished evaluating applicants. Total evaluated: {evaluated_count}")


def evaluate_single_applicant(applicant_id: str):
    """Evaluate a single applicant using LLM"""
    client = AirtableClient()
    llm_client = LLMClient()
    
    print(f"\nEvaluating single applicant: {applicant_id}")

    # Get applicant data
    try:
        print("Fetching applicant data...")
        applicant_data = client.get_applicant_data(applicant_id)
        compressed_json_str = applicant_data['applicant'].get('Compressed JSON', '{}')
        compressed_data = json.loads(compressed_json_str.replace("'", '"'))
        print(f"Loaded data for {applicant_id}")
    except Exception as e:
        print(f"Error getting data for applicant {applicant_id}: {e}")
        return
    
    # Evaluate with LLM
    try:
        print("Sending data to LLM for evaluation...")
        evaluation = llm_client.evaluate_applicant(compressed_data)

        # Build Airtable-safe payload
        update_payload = {
            'LLM Summary': str(evaluation.get('summary', '')),
            'LLM Score': float(evaluation.get('score', 0)),
            'LLM Follow-Ups': "\n".join(map(str, evaluation.get('follow_ups', [])))
        }

        print("Searching for Airtable record...")
        applicant_records = client.get_records(
            settings.APPLICANTS_TABLE,
            filter_formula=f"{{Applicant ID}} = '{applicant_id}'"
        )
        
        if applicant_records:
            print(f"Updating Airtable record for {applicant_id}: {update_payload}")
            client.update_record(
                settings.APPLICANTS_TABLE,
                applicant_records[0]['id'],
                update_payload
            )
            
            print(f"Applicant {applicant_id} evaluated successfully")
            print(f"Summary: {evaluation['summary']}")
            print(f"Issues: {evaluation['issues']}")
            print("Follow-ups:")
            for follow_up in evaluation['follow_ups']:
                print(f"  • {follow_up}")
                
        else:
            print(f"Applicant {applicant_id} not found in Airtable")
            
    except Exception as e:
        print(f"Error evaluating applicant {applicant_id}: {e}")


def main():
    parser = argparse.ArgumentParser(description='Evaluate applicants using LLM')
    parser.add_argument('--applicant-id', help='Evaluate a specific applicant')
    
    args = parser.parse_args()
    
    try:
        if args.applicant_id:
            evaluate_single_applicant(args.applicant_id)
        else:
            evaluate_applicants()
    except Exception as e:
        print(f"Fatal Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
