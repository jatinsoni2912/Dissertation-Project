import os
import re
import subprocess
import ollama
import psycopg2
from dotenv import load_dotenv

from database import get_ontology_mappings

from llm_pipeline import (
    extract_activity_terms,
    extract_location,
    validate_sql
)

load_dotenv()

