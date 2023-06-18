import logging
import os
import boto3
from botocore.exceptions import HTTPClientError
from yaml import safe_load

# Instantiate logger at module level using the "__name__" variable
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


# We don't want secrets & URLs stored in plain code - AWS Parameter Store is an easy & safe way to store secrets
def _extract_config_values(config_path: str):
    try:
        with open(config_path, "r") as config_file:
            # We can load the contents of the yaml file into a dictionary object & parse through it
            contents = safe_load(config_file)

            # Parse the "contents" dictionary for our SSM API URL & Key secret names
            ssm_api_url = contents.get("prod").get("secrets").get("aws").get("api-url")
            ssm_api_key = contents.get("prod").get("secrets").get("aws").get("api-key")

        return ssm_api_url, ssm_api_key

    # AttributeError's are common when parsing dictionaries using .get() - we should aim to catch these
    except AttributeError as att_ex:
        logger.error(
            f"AttributeError occurred when extracting secret name values: {att_ex} - raising RunTime error to prevent further action being taken."
        )
        raise RuntimeError(
            "There has been an error parsing the configuration file 'config.yaml' - please investigate the logs, refactor & re-try."
        )
    # We still need to catch any other unexpected errors, e.g. wrong file path provided at entry point
    except Exception as ex:
        logger.error(
            f"Unexpected error occurred: {ex} - raising RunTime error to prevent further action being taken."
        )
        raise RuntimeError(
            "There has been an error reading configuration file 'config.yaml' - please investigate the logs, refactor & re-try."
        )


def _extract_ssm_values(ssm_api_url: str, ssm_api_key: str):
    # Instantiate SSM client so that we can interact with parameter store
    try:
        ssm_client = boto3.client("ssm")
    except HTTPClientError as ssm_err:
        # Raise RuntimeError so that we can establish connectivity to client before attempting to continue
        logger.error("Cannot establish boto3 SSM client - attempting to reprocess.")
        raise RuntimeError(
            "Cannot establish boto3 SSM client - attempting to reprocess."
        )

    try:
        # Secrets are encrypted at rest using my AWS accounts' default KMS key, my assumed user at run-time is authorised to use this KMS key
        # Typically a service role, i.e. lambda exec. role, ec2-user, will also have these permissions when deployed
        API_URL = ssm_client.get_parameter(Name=ssm_api_url, WithDecryption=True)[
            "Parameter"
        ]["Value"]

        API_KEY = ssm_client.get_parameter(Name=ssm_api_key, WithDecryption=True)[
            "Parameter"
        ]["Value"]

        # Return our raw values
        return API_URL, API_KEY

    except Exception as config_ex:
        # Raise RuntimeError so that we can successfully retrieve variables from SSM before we try to ping the API
        logger.error(
            f"Error exporting SSM parameters to global variables due to: {config_ex}."
        )
        raise RuntimeError(
            f"Error exporting SSM parameters to global variables due to: {config_ex}."
        )


# Orchestrating function - ensures our app.py script does not become convoluted with config init code
def init_config(config_path: str, ssm_flag: bool):
    if ssm_flag:
        # Call the _extract_config_values function
        ssm_api_url, ssm_api_key = _extract_config_values(config_path=config_path)

        # Call our SSM function
        API_URL, API_KEY = _extract_ssm_values(
            ssm_api_url=ssm_api_url, ssm_api_key=ssm_api_key
        )

        return API_URL, API_KEY

    else:
        try:
            API_URL = os.environ["KRAKEN_API_URL"]
            API_KEY = os.environ["KRAKEN_API_KEY"]

            return API_URL, API_KEY

        # Catch common os exceptions - env variable doesn't exist
        except KeyError as env_var_ex:
            logger.error(
                "Environment variables set incorrectly, please reset environment variables before continuing - raising Runtime error to prevent further action."
            )
            logger.error(f"{env_var_ex}.")
            raise RuntimeError(
                "Environment variables set incorrectly, please reset environment variables before continuing."
            )
