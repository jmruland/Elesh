import os
from config import SYSTEM_PROMPT_FILE, DEFAULT_SYSTEM_PROMPT
from utils.logger import logger

def get_system_prompt():
    try:
        if os.path.exists(SYSTEM_PROMPT_FILE):
            with open(SYSTEM_PROMPT_FILE, "r", encoding="utf-8") as f:
                text = f.read().strip()
                if text:
                    return text
    except Exception as e:
        logger.error(f"Error loading system prompt: {e}")
    return DEFAULT_SYSTEM_PROMPT

def set_system_prompt(new_text):
    try:
        with open(SYSTEM_PROMPT_FILE, "w", encoding="utf-8") as f:
            f.write(new_text)
        logger.info("Updated system prompt written to disk.")
    except Exception as e:
        logger.error(f"Error saving system prompt: {e}")