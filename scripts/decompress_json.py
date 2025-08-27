#!/usr/bin/env python3
"""
JSON Decompression Script
Reads compressed JSON and updates child tables to match JSON state
"""

import sys
import json
import argparse
from typing import Dict, Any

# Add the parent directory to the path to import modules
sys.path.append('../')

from utils.airtable_client import AirtableClient
from config import settings


def decompress_json(applicant_auto_id: str, compressed_json: Dict[str, Any]):
    """Decompress JSON and update child tables"""
    client = AirtableClient()

    # Find the actual Airtable record ID for this applicant
    applicant_record = client.find_record_by_field(
        settings.APPLICANTS_TABLE,
        "Applicant ID",
        applicant_auto_id
    )
    if not applicant_record:
        raise ValueError(f"Applicant with Applicant ID={applicant_auto_id} not found")

    applicant_rec_id = applicant_record["id"]

    # --- PERSONAL DETAILS ---
    personal_details = compressed_json["personal"]

    personal_records = client.get_records(
        settings.PERSONAL_DETAILS_TABLE,
        filter_formula=f"{{Applicant ID}} = '{applicant_rec_id}'"
    )

    personal_payload = {
        "Full Name": personal_details["full_name"],
        "Email": personal_details["email"],
        "Location": personal_details["location"],
        "LinkedIn": personal_details.get("linkedin", ""),
        "Applicant ID": [applicant_rec_id],
    }

    if personal_records:
        client.update_record(
            settings.PERSONAL_DETAILS_TABLE,
            personal_records[0]["id"],
            personal_payload,
        )
    else:
        client.create_record(settings.PERSONAL_DETAILS_TABLE, personal_payload)

    # --- WORK EXPERIENCE ---
    work_exp_records = client.get_records(
        settings.WORK_EXPERIENCE_TABLE,
        filter_formula=f"{{Applicant ID}} = '{applicant_rec_id}'"
    )
    for record in work_exp_records:
        client.delete_record(settings.WORK_EXPERIENCE_TABLE, record["id"])

    for exp in compressed_json["experience"]:
        exp_payload = {
            "Company": exp["company"],
            "Title": exp["title"],
            "Start": exp["start"],
            "End": exp.get("end", ""),
            "Technologies": exp.get("technologies", []),
            "Applicant ID": [applicant_rec_id],
        }
        client.create_record(settings.WORK_EXPERIENCE_TABLE, exp_payload)

    # --- SALARY PREFERENCES ---
    salary_prefs = compressed_json["salary"]

    salary_records = client.get_records(
        settings.SALARY_PREFERENCES_TABLE,
        filter_formula=f"{{Applicant ID}} = '{applicant_rec_id}'"
    )

    salary_payload = {
        "Preferred Rate": salary_prefs["preferred_rate"],
        "Minimum Rate": salary_prefs["minimum_rate"],
        "Currency": salary_prefs["currency"],
        "Availability": salary_prefs["availability"],
        "Applicant ID": [applicant_rec_id],
    }

    if salary_records:
        client.update_record(
            settings.SALARY_PREFERENCES_TABLE,
            salary_records[0]["id"],
            salary_payload,
        )
    else:
        client.create_record(settings.SALARY_PREFERENCES_TABLE, salary_payload)

    print(f"✅ Successfully decompressed JSON for applicant {applicant_auto_id} → recId {applicant_rec_id}")


def main():
    parser = argparse.ArgumentParser(description="Decompress JSON and update child tables")
    parser.add_argument("applicant_id", help="Applicant ID (autoNumber, from Applicants table)")
    parser.add_argument("--json-file", help="Path to JSON file (if not using Airtable stored JSON)")

    args = parser.parse_args()

    try:
        if args.json_file:
            with open(args.json_file, "r") as f:
                compressed_json = json.load(f)
        else:
            client = AirtableClient()
            applicant_record = client.find_record_by_field(
                settings.APPLICANTS_TABLE,
                "Applicant ID",
                args.applicant_id
            )
            if not applicant_record:
                raise ValueError(f"Applicant ID {args.applicant_id} not found")

            compressed_json_str = applicant_record["fields"].get("Compressed JSON", "{}")
            compressed_json = json.loads(compressed_json_str)

        decompress_json(args.applicant_id, compressed_json)

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
