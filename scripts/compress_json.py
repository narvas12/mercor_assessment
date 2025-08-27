#!/usr/bin/env python3
"""
JSON Compression Script
Gathers data from linked tables and compresses into a single JSON object
"""

import sys
import json
import argparse
from typing import Dict, Any

# Add the parent directory to the path to import modules
sys.path.append('../')

from utils.airtable_client import AirtableClient
from config import settings


def compress_applicant_data(applicant_id: str) -> Dict[str, Any]:
    """Compress all applicant data into a single JSON object"""
    client = AirtableClient()

    # Get all data for the applicant
    applicant_data = client.get_applicant_data(applicant_id)

    # Build compressed JSON structure
    compressed_json = {
        "personal": {
            "full_name": applicant_data.get("personal_details", {}).get("Full Name"),
            "email": applicant_data.get("personal_details", {}).get("Email"),
            "location": applicant_data.get("personal_details", {}).get("Location"),
            "linkedin": applicant_data.get("personal_details", {}).get("LinkedIn"),
        },
        "experience": [],
        "salary": {
            "preferred_rate": applicant_data.get("salary_preferences", {}).get("Preferred Rate"),
            "minimum_rate": applicant_data.get("salary_preferences", {}).get("Minimum Rate"),
            "currency": applicant_data.get("salary_preferences", {}).get("Currency"),
            "availability": applicant_data.get("salary_preferences", {}).get("Availability"),
        },
    }

    # Add work experience safely
    for exp in applicant_data.get("work_experience", []):
        compressed_json["experience"].append(
            {
                "company": exp.get("Company"),
                "title": exp.get("Title"),
                "start": exp.get("Start Date"),   # Match Airtable field name
                "end": exp.get("End Date"),
                "technologies": exp.get("Technologies", []),
            }
        )

    # Update the applicant record with compressed JSON
    client.update_applicant_json(applicant_id, compressed_json)

    return compressed_json


def main():
    parser = argparse.ArgumentParser(description="Compress applicant data into JSON")
    parser.add_argument("applicant_id", help="Applicant ID to compress data for")

    args = parser.parse_args()

    try:
        compressed_json = compress_applicant_data(args.applicant_id)
        print(f"Successfully compressed data for applicant {args.applicant_id}")
        print(json.dumps(compressed_json, indent=2))
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
