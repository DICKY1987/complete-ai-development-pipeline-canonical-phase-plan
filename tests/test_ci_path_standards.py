"""
Test file to demonstrate CI path standards check.
This file shows correct import patterns that should pass the CI check.
"""
# DOC_ID: DOC-TEST-TESTS-TEST-CI-PATH-STANDARDS-077
# DOC_ID: DOC-TEST-TESTS-TEST-CI-PATH-STANDARDS-038

# Correct imports that should pass:
from modules.core_state.m010003_db import init_db
from modules.error_engine.m010004_error_engine import ErrorEngine

print("Test file loaded")
