# llm_client.py

import os
import logging
import json
from openai import OpenAI

logger = logging.getLogger(__name__)


class LLMClient:
    """
    Wrapper around OpenAI GPT-4o for evaluating applicants.
    """

    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = "gpt-4o"
        logger.debug(f"Initializing LLMClient with OpenAI model: {self.model}")

    def evaluate_applicant(self, applicant: dict) -> dict:
        """
        Send applicant data to GPT-4o and return structured evaluation.
        """

        logger.debug(f"Starting evaluation for applicant: {applicant.get('id', 'unknown')}")
        logger.debug(f"Applicant data: {applicant}")

        # Build prompt
        prompt = f"""
You are a recruiter AI. Evaluate the following applicant:

{json.dumps(applicant, indent=2)}

Return ONLY a JSON object with the following fields:
- summary: A 2-3 sentence summary of the applicant
- score: A number from 0 to 100 evaluating applicant quality
- follow_ups: Suggested follow-up questions
"""
        logger.debug(f"Built prompt ({len(prompt)} chars): {prompt[:200]}...")

        # Query LLM with retries
        for attempt in range(3):
            try:
                logger.debug(f"Attempt {attempt+1}/3 - Sending to OpenAI...")

                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are a helpful recruiter AI."},
                        {"role": "user", "content": prompt},
                    ],
                    temperature=0.2,
                )

                reply = response.choices[0].message.content.strip()
                logger.debug(f"Raw LLM reply: {reply}")

                # Clean Markdown fences if present
                if reply.startswith("```"):
                    logger.debug("Detected code fences in reply, cleaning...")
                    reply = reply.strip("`")
                    reply = reply.replace("json\n", "", 1).replace("json\r\n", "", 1).strip()

                # Try parsing JSON
                try:
                    parsed = json.loads(reply)
                    logger.debug(f"Parsed JSON: {parsed}")

                    return {
                        "summary": parsed.get("summary", ""),
                        "score": float(parsed.get("score", 0)),
                        "follow_ups": parsed.get("follow_ups", ""),
                    }

                except Exception as e:
                    logger.error(f"Failed to parse LLM reply as JSON: {e}")
                    logger.debug(f"Returning fallback with raw reply.")
                    return {
                        "summary": reply,
                        "score": 0.0,
                        "follow_ups": "",
                    }

            except Exception as e:
                logger.error(f"Error on attempt {attempt+1}: {e}")

        # If all attempts fail
        logger.error("All attempts failed, returning fallback response")
        return {
            "summary": "Evaluation failed",
            "score": 0.0,
            "follow_ups": "",
        }
