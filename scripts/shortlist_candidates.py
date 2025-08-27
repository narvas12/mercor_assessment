import json
import logging
from utils.airtable_client import AirtableClient
from config import settings

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s [%(levelname)s] %(message)s")


def shortlist_candidates():
    client = AirtableClient()

    logging.info("Fetching applicants...")
    applicants = client.get_records(settings.APPLICANTS_TABLE)
    logging.debug("=== DEBUG: Fetched applicants ===\n%s", json.dumps(applicants, indent=2))

    shortlisted_count = 0

    for applicant in applicants:
        fields = applicant.get("fields", {})
        applicant_id = fields.get("Applicant ID")
        compressed_json_raw = fields.get("Compressed JSON")

        logging.info(f"Processing applicant: {applicant_id}")
        logging.debug("=== DEBUG: Applicant raw data ===\n%s", json.dumps(applicant, indent=2))

        if not compressed_json_raw:
            logging.warning(f"Skipping applicant {applicant_id} (no compressed JSON)")
            continue

        try:
            compressed_json = json.loads(compressed_json_raw)
        except json.JSONDecodeError:
            logging.error(f"Invalid JSON for applicant {applicant_id}")
            continue

        # Extract data from compressed JSON
        experience = compressed_json.get("experience", [])
        years_experience = len(experience)  # crude proxy count

        salary_info = compressed_json.get("salary", {})
        preferred_rate = salary_info.get("preferred_rate", 0)
        availability = salary_info.get("availability", 0)
        currency = salary_info.get("currency", ["USD"])[0]

        location = compressed_json.get("personal", {}).get("location", "")

        # Evaluation
        evaluation = {
            "total_experience": years_experience,
            "meets_compensation": preferred_rate <= settings.MAX_HOURLY_RATE,
            "eligible_location": any(loc.lower() in location.lower() for loc in settings.ELIGIBLE_LOCATIONS),
            "meets_availability": availability >= settings.MIN_AVAILABILITY,
        }

        logging.debug("=== DEBUG: Applicant %s evaluation ===\n%s",
                      applicant_id, json.dumps(evaluation, indent=2))

        # Shortlist decision
        if (
            evaluation["total_experience"] >= settings.MIN_EXPERIENCE
            and evaluation["meets_compensation"]
            and evaluation["eligible_location"]
            and evaluation["meets_availability"]
        ):
            score_reason = (
                f"{years_experience} yrs exp; "
                f"Rate {preferred_rate}{currency} OK; "
                f"Availability {availability}h/wk; "
                f"Location eligible"
            )

            record_data = {
                "Applicant ID": [applicant.get("id")],  # Airtable expects recId list
                "Compressed JSON": compressed_json_raw,
                "Score Reason": score_reason,
            }

            logging.debug("=== DEBUG: Applicant %s shortlist record ===\n%s",
                          applicant_id, json.dumps(record_data, indent=2))

            try:
                client.create_record(settings.SHORTLISTED_LEADS_TABLE, record_data)
                logging.info(f"Shortlisted applicant {applicant_id}")
                shortlisted_count += 1
            except Exception as e:
                logging.error(f"Error creating shortlist record for {applicant_id}: {e}")

        else:
            logging.info(f"Applicant {applicant_id} not shortlisted (fails criteria)")

    logging.info(f"Finished shortlisting. Total shortlisted: {shortlisted_count}")


if __name__ == "__main__":
    shortlist_candidates()
