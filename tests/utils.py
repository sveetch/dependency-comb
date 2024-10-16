from os import getenv


API_ENABLED_ENVVAR = "COMB_TEST_API_ENABLED"


# Condition to enable API request depends from existing API key file and environment
# variable
skip_api_condition = getenv(API_ENABLED_ENVVAR, default="").strip().lower() != "true"
