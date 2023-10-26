# Read environment from SERVERENV environment variable
import os
import logging

logger = logging.getLogger(__name__)

env = os.environ.get('SERVERENV')
if not env:
    logger.error("SERVERENV environment variable not set.")
    raise EnvironmentError("SERVERENV environment variable not set.")

RESULTS_FILE = 'certificates_status.json'  # Define the results file name