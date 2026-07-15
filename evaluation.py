import argparse
import time
import re
import sys
import json
import os
import csv
from collections import defaultdict
from datetime import datetime

from evaluation_queries import (ALL_QUERIES, ALL_EXTENDED_QUERIES, EXPLICIT_DISTANCE_QUERIES, LANDMARK_PROXIMITY_QUERIES, SPORT_DEPRIVATION_QUERIES)
from database import execute_query
from llm_client import (PROVIDER_OLLAMA, PROVIDER_BEDROCK,  DEFAULT_OLLAMA_MODEL, DEFAULT_BEDROCK_MODEL)
from pure_llm_pipeline import generate_sql_pure_llm, generate_sql_pure_llm_using_bedrock
from llm_pipeline import generate_sql
from mcp_pipeline import generate_sql_with_mcp