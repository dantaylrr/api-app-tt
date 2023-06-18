import logging
import requests
from requests.adapters import Retry, HTTPAdapter

# Instantiate logger at module level using the "__name__" variable
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


# Define a re-try strategy should we receive 5xx errors from the API
def _define_retry_strategy():
    return Retry(total=5, status_forcelist=[500, 501, 502, 503, 504])


# Mount our API endpoint onto our requests session - this allows us to pass the base session around functions
def mount_endpoint(retry_strategy: Retry = _define_retry_strategy()):
    try:
        # Initialise a session
        req_session = requests.Session()
        # Mount our retry strategy onto the session - we will use the https:// prefix for the most re-usability
        req_session.mount(
            prefix=f"https://", adapter=HTTPAdapter(max_retries=retry_strategy)
        )

        # Return the session for re-usability throughout code
        return req_session
    except Exception as ex:
        logger.warning(
            f"Failure to successfully mount endpoint with retry strategy: {ex} - allowing application to continue..."
        )


# Define authorisation headers to pass into each request
def define_headers(api_key: str):
    return {"x-api-key": f"{api_key}"}


# We can get the outages data from the API with a GET request
def get_outages(
    api_endpoint_url: str, headers: dict[str], requests_session: requests.Session
):
    # Using the requests library, we can issue get requests on API endpoints
    try:
        logger.info(f"Attempting to issue GET request to outages API endpoint...")
        # Ping the API endpoint using our session - returns a response Object
        response = requests_session.get(
            url=f"{api_endpoint_url}/outages", headers=headers
        )
        logger.info(
            f"Outages GET request response: Status code = {response.status_code}."
        )

        # Return the response as a JSON dictionary
        return response
    except Exception as ex:
        logger.error(
            f"Max retries exceeded on GET request to {api_endpoint_url}/outages - due to {ex}... raising RuntimeError."
        )
        raise RuntimeError(
            f"Max retries exceeded on GET request to {api_endpoint_url}/outages - due to {ex}... cannot continue without outages data!."
        )


# We can get the site-info data from the API with a separate GET request
def get_site_info(
    api_endpoint_url: str, headers: dict[str], requests_session: requests.Session
):
    # Using the requests library, we can issue get requests on API endpoints
    try:
        logger.info(f"Attempting to issue GET request to site-info API endpoint...")
        # Ping the API endpoint using our session - returns a response Object
        response = requests_session.get(
            url=f"{api_endpoint_url}/site-info/norwich-pear-tree", headers=headers
        )
        logger.info(
            f"Site-info GET request response: Status code = {response.status_code}."
        )

        # Return the response as a JSON dictionary
        return response
    except Exception as ex:
        logger.error(
            f"Max retries exceeded on GET request to {api_endpoint_url}/site-info/norwich-pear-tree - due to {ex}... raising RuntimeError."
        )
        raise RuntimeError(
            f"Max retries exceeded on GET request to {api_endpoint_url}/site-info/norwich-pear-tree - due to {ex}... cannot continue without site-info data!"
        )


# We can get the site-info data from the API with a separate GET request
def post_results(
    api_endpoint_url: str,
    headers: dict[str],
    requests_session: requests.Session,
    data: list[dict],
):
    # Using the requests library, we can issue get requests on API endpoints
    try:
        logger.info(
            f"Attempting to POST results to site-info/<site-id> API endpoint..."
        )
        # Ping the API endpoint using our session - returns a response Object
        response = requests_session.post(
            url=f"{api_endpoint_url}/site-outages/norwich-pear-tree",
            headers=headers,
            json=data,
        )

        # Return the response as a JSON dictionary
        return response
    except Exception as ex:
        logger.error(
            f"Max retries exceeded on POST request to {api_endpoint_url}/site-outages/norwich-pear-tree - due to {ex}... raising RuntimeError."
        )
        raise RuntimeError(
            f"Max retries exceeded on GET request to {api_endpoint_url}/site-outages/norwich-pear-tree - due to {ex}... cannot continue without site-info data!"
        )
