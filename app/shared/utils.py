# app/shared/utils.py

import os
import re
import nltk
from nltk.tokenize import word_tokenize
from datetime import datetime
from typing import List

from app.config import settings

def get_list_from_comma_separated_string(values: str) -> List[str]:
    return [v.strip() for v in values.split(",") if v.strip()]

def format_datetime_to_iso_format(dt_obj: datetime) -> str:
    return dt_obj.strftime("%Y-%m-%dT%H:%M:%SZ")

def load_prompt_from_file(filename: str) -> str:
    base = settings.get_local_prompt_basepath()
    full_path = os.path.join(base, filename)
    if not os.path.isfile(full_path):
        raise FileNotFoundError(f"Prompt file not found: {full_path}")
    with open(full_path, "r", encoding="utf-8") as f:
        return f.read().strip()

def get_dummy_pdbe() -> dict:
    return {
        "case_id": "DUMMY123",
        "pdbe": (
            "Cx states getting memory full error. "
            "When was the first occurrence? Within...: 2025-04-23T16:14:21.127Z. "
            "How often is issue occurring?: First occurrence. "
            "Information to support the complaint handling process: "
            "Customer Function/Role: Technician/Sonographer. "
            "How was the device being used? No patient involved. "
            "Expected and actual behavior of the product: getting memory full error when it should not have errors. "
            "User Impact: Unable to use system due to issue. "
            "Patient Impact: 1 Patient having to wait for system to be able to take fluoroscopy exams. "
            "Current Software Version: 4."
        )
    }

def clean_text(text: str, stop_words: set = None) -> List[str]:
    text = str(text).lower().strip()
    text = re.sub(r"[^\w\s]", "", text)
    text = text.replace(",", "")
    tokens = word_tokenize(text, language="english", preserve_line=True)
    if stop_words:
        tokens = [t for t in tokens if t not in stop_words]
    return tokens

def initialize_nltk_stop_words(nltk_data_path: str) -> set:
    if not os.path.exists(nltk_data_path):
        os.makedirs(nltk_data_path)
    nltk.data.path.append(nltk_data_path)
    stopwords_dir = os.path.join(nltk_data_path, "corpora", "stopwords")
    english_stopwords_path = os.path.join(stopwords_dir, "english")
    if not os.path.exists(english_stopwords_path):
        nltk.download("stopwords", download_dir=nltk_data_path)
        for fname in os.listdir(stopwords_dir):
            fpath = os.path.join(stopwords_dir, fname)
            if fname != "english" and os.path.isdir(fpath):
                os.rmdir(fpath)
        zip_path = os.path.join(nltk_data_path, "corpora", "stopwords.zip")
        if os.path.exists(zip_path):
            os.remove(zip_path)
    from nltk.corpus import stopwords
    sw = set(stopwords.words("english"))
    sw.discard("no")
    sw.discard("not")
    return sw
