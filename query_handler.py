import json
import re
import streamlit as st

from database import execute_query, get_feature_locations_for_count
from app_utils import prepare_geojson_collection