import logging
from sys import stdout
from src.utils.config.initialise_config import init_config
from src.utils.api.api import (
    mount_endpoint,
    define_headers,
    get_outages,
    get_site_info,
    post_results,
)
from src.utils.transformation.filter_outages import (
    filter_outages_by_datetime,
    filter_outages_by_site_info,
)
from src.utils.transformation.generate_result import produce_final_output

"""
To enable other people to run this application, adding environment functionality for config initialisation
In a normal working env. everyone should have access to the same AWS account for Parameter Store secret retreival - but obviously not the case here
Using env. variables will also allow for easier unit/integration test validation from their local machine
"""

# SSM flag - set to true if user wants to retreive secrets from SSM, otherwise use env. variables - see README.md
ssm_flag = True

# You can "print" logs to the console using stdout
logging.basicConfig(stream=stdout, level=logging.INFO)
# Instantiate logger for app.py using the "__name__" variable
logger = logging.getLogger(__name__)


def main():
    """
    Typically, we want our driver function (main()) to have as little boilerplate code & convoluted functionality as possible
    This enables people to understand the workflow from a High-Level & dive into business logic / implementation if required

    The entrypoint for our process is the 1st API call to ".../outages" -> only then do we have data to work with
    Thus, def main() takes no arguments - it is simply used for process orchestration when app.py is called
    We want to orchestrate our workflow & return a HTTP response from the final endpoint ".../site-info/{site-id}"

    Notes:

        - Omitting try/excepts in def main() as all utils functions have their own unique try/catch statements
        - To prevent secrets being exposed in code, I am using my PERSONAL AWS ACCOUNT & SSM Parameter Store for secret encryption
            * This could be prevented by setting secrets as env. variables using "os" library - but wanted to demonstate best practices where possible
    """

    # Initialise config
    API_URL, API_KEY = init_config(config_path="./config.yaml", ssm_flag=ssm_flag)

    # Initialise our requests session & re-try strategy (for potential 5xx errors) - can be re-used in API calls
    req_session = mount_endpoint()

    # Initialise authorisation headers - can be re-used in API calls
    headers = define_headers(api_key=API_KEY)

    # Get outages data - this returns response object
    outages_response = get_outages(
        api_endpoint_url=API_URL, headers=headers, requests_session=req_session
    )

    # Get site-info data - this returns response object
    site_info_response = get_site_info(
        api_endpoint_url=API_URL, headers=headers, requests_session=req_session
    )

    # Convert object responses into data for manipulation
    outages_data, site_info_data = outages_response.json(), site_info_response.json()

    # Filter for outages that occurred after "2022-01-01T00:00:00.000Z"
    filtered_outages_dt = filter_outages_by_datetime(outages=outages_data)

    # Filter for outages that only exist in "site_info_data" devices
    filtered_outages = filter_outages_by_site_info(
        filtered_outages_dt=filtered_outages_dt, site_info_data=site_info_data
    )

    # Now we can generate our final output to POST
    final_output = produce_final_output(
        filtered_outages=filtered_outages, site_info_data=site_info_data
    )

    # & we can post our results to the API endpoint, returning a response
    response = post_results(
        api_endpoint_url=API_URL,
        headers=headers,
        requests_session=req_session,
        data=final_output,
    )

    # Return the API response
    return response


# If app.py is executed, call main()
if __name__ == "__main__":
    logger.info("Loading application...")
    try:
        response = main()
        logger.info(
            f"Site-info POST request response: Status code = {response.status_code}."
        )
    except Exception as ex:
        # Final catch all, if something we have failed to catch has occurred, raise runtime error & exit
        logger.error(
            f"There has been an issue successfully running the application: {ex}."
        )
        raise RuntimeError
    finally:
        logger.info("Exiting application...")
