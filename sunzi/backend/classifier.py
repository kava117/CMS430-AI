import json
import os
import logging
from openai import OpenAI
from dotenv import load_dotenv
from character import CLASSIFIER_SYSTEM_PROMPT

load_dotenv()

logger = logging.getLogger(__name__)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

VALID_CLASSIFICATIONS = {
    "understanding", "confusion", "insight",
    "clarification", "evasion", "off_topic"
}


def classify_input(user_input: str, current_topic: str, current_stage: str) -> str:
    """
    Classify user input into one of six categories.
    Returns the classification string, defaulting to 'confusion' on error.
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": CLASSIFIER_SYSTEM_PROMPT},
                {"role": "user", "content": f"Topic: {current_topic}\nStage: {current_stage}\nStudent input: {user_input}"}
            ],
            max_tokens=50,
            temperature=0
        )
        result = json.loads(response.choices[0].message.content)
        classification = result.get("classification", "")
        if classification not in VALID_CLASSIFICATIONS:
            logger.warning(f"Invalid classification returned: {classification!r}, defaulting to 'confusion'")
            return "confusion"
        return classification
    except Exception as e:
        logger.error(f"Classifier error: {e}")
        return "confusion"
