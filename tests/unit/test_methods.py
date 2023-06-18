import os
import json
import pytest
from src.utils.api.api import mount_endpoint, define_headers, get_outages, get_site_info, post_results
from src.utils.transformation.filter_outages import filter_outages_by_datetime, filter_outages_by_site_info
from src.utils.transformation.generate_result import produce_final_output

"""
We need to setup our request session before we attempt to test our methods
We also need to assign a correct & incorrect headers call using the valid & invalid API key below
"""

# Re-usable requests session for testing
@pytest.fixture
def requests_session():
    return mount_endpoint()

# Fixtures to use for API requests
@pytest.fixture
def invalid_api_url():
    return "https://google.com"

@pytest.fixture
def valid_api_url():
    return os.environ["KRAKEN_API_URL"]

@pytest.fixture
def invalid_api_key():
    return 123456789

@pytest.fixture
def valid_api_key():
    return os.environ["KRAKEN_API_KEY"]

# Re-usable valid & invalid headers using fixtures defined above
@pytest.fixture
def invalid_headers(invalid_api_key):
    return define_headers(api_key = invalid_api_key)

@pytest.fixture
def valid_headers(valid_api_key):
    return define_headers(api_key = valid_api_key)

"""
First transformation function to test is 'filter_outages_by_datetime'
"""

@pytest.fixture
def invalid_outages():
    with open("./tests/events/outages/invalid_outages.json", "rb") as f:
        # Read the contents of invalid_outages as a pytest fixture
        return json.loads(f.read())

@pytest.fixture
def valid_outages():
    with open("./tests/events/outages/valid_outages.json", "rb") as f:
        # Read the contents of valid_outages as a pytest fixture
        return json.loads(f.read())
    
"""
In order to test our 'filter_outages_by_site_info' function, we need a valid filtered outages list[dict] from 'filter_outages_by_datetime'
Invalid outages should never reach this function due to Runtime raising in 'filter_outages_by_datetime', thus we do not need to test for these scenarios
"""

@pytest.fixture
def valid_filtered_outages_dt(valid_outages):
    return filter_outages_by_datetime(outages = valid_outages)
    
@pytest.fixture
def invalid_site_info():
    with open("./tests/events/site-info/invalid_site_info.json", "rb") as f:
        # Read the contents of invalid_outages as a pytest fixture
        return json.loads(f.read())

@pytest.fixture
def valid_site_info():
    with open("./tests/events/site-info/valid_site_info.json", "rb") as f:
        # Read the contents of valid_outages as a pytest fixture
        return json.loads(f.read())
    
"""
In order to test our 'produce_valid_output' function, we need a valid filtered outages list[dict] from 'filter_outages_by_site_info'
"""

@pytest.fixture
def valid_filtered_outages(valid_filtered_outages_dt, valid_site_info):
    return filter_outages_by_site_info(filtered_outages_dt = valid_filtered_outages_dt, site_info_data = valid_site_info)

@pytest.fixture
def valid_final_output():
    with open("./tests/events/output/valid_output.json", "rb") as f:
        # Read the contents of valid_output as a pytest fixture
        return json.loads(f.read())


"""
We can then test our POST function using a both our expected output & a partial, invalid output
"""

@pytest.fixture
def invalid_final_output():
    with open("./tests/events/output/invalid_output.json", "rb") as f:
        # Read the contents of invalid_output as a pytest fixture
        return json.loads(f.read())

"""
API function test - outages endpoint
"""

def test_get_outages_invalid_api_url_and_invalid_key(invalid_api_url, invalid_headers, requests_session):
    # Try to issue a get request using the wrong API endpoint & API Key
    response = get_outages(api_endpoint_url = invalid_api_url, headers = invalid_headers, requests_session = requests_session)

    # We should get a 404 response, google.com/outages doesn't exist
    assert response.status_code == 404

def test_get_outages_valid_api_url_and_invalid_key(valid_api_url, invalid_headers, requests_session):
    # Try to issue a get request using the correct API endpoint & incorrect API Key
    response = get_outages(api_endpoint_url = valid_api_url, headers = invalid_headers, requests_session = requests_session)

    # We should get a 403 forbidden response, we are using the wrong API key
    assert response.status_code == 403

def test_get_outages_invalid_api_url_and_valid_key(invalid_api_url, valid_headers, requests_session):
    # Try to issue a get request using the incorrect API endpoint & correct API Key
    response = get_outages(api_endpoint_url = invalid_api_url, headers = valid_headers, requests_session = requests_session)

    # We should get a 404 response, google.com/outages doesn't exist
    assert response.status_code == 404

def test_get_outages_valid_api_url_and_valid_key(valid_api_url, valid_headers, requests_session):
    # Try to issue a get request using the correct API endpoint & correct API Key
    response = get_outages(api_endpoint_url = valid_api_url, headers = valid_headers, requests_session = requests_session)

    # We should get a 200 success response
    assert response.status_code == 200
    # Our data returned should also be populated
    assert len(response.json()) > 0

"""
API function test - site-info endpoint
"""

def test_get_site_info_invalid_api_url_and_invalid_key(invalid_api_url, invalid_headers, requests_session):
    # Try to issue a get request using the wrong API endpoint & API Key
    response = get_site_info(api_endpoint_url = invalid_api_url, headers = invalid_headers, requests_session = requests_session)

    # We should get a 404 response, google.com/site-info/norwich-pear-tree doesn't exist
    assert response.status_code == 404

def test_get_site_info_valid_api_url_and_invalid_key(valid_api_url, invalid_headers, requests_session):
    # Try to issue a get request using the wrong API endpoint & API Key
    response = get_site_info(api_endpoint_url = valid_api_url, headers = invalid_headers, requests_session = requests_session)

    # We should get a 403 forbidden response, we are using the wrong API key
    assert response.status_code == 403

def test_get_site_info_invalid_api_url_and_valid_key(invalid_api_url, valid_headers, requests_session):
    # Try to issue a get request using the wrong API endpoint & API Key
    response = get_site_info(api_endpoint_url = invalid_api_url, headers = valid_headers, requests_session = requests_session)

    # We should get a 404 response, google.com/site-info/norwich-pear-tree doesn't exist
    assert response.status_code == 404

def test_get_site_info_valid_api_url_and_valid_key(valid_api_url, valid_headers, requests_session):
    # Try to issue a get request using the wrong API endpoint & API Key
    response = get_site_info(api_endpoint_url = valid_api_url, headers = valid_headers, requests_session = requests_session)

    # We should get a 200 success response
    assert response.status_code == 200
    # Our data returned should also be populated
    assert len(response.json()) > 0

"""
Outages filter function - outage began after 2022-01-01T00:00:00.000Z
"""

def test_invalid_outages_filter_by_datetime(invalid_outages):
    with pytest.raises(RuntimeError) as ex_info:
        # Call the function
        filtered_outages_dt = filter_outages_by_datetime(outages = invalid_outages)

    # We want to assert a RuntimeError exception being raised
    assert ex_info
    # In this case, we want to assert the message of the RuntimeError as well, to ensure that we are getting the desired behaviour
    assert ex_info.value.args[0] == "Cannot perform successful filtering of outages data due to: strptime() argument 1 must be str, not None."

def test_valid_outages_filter_by_datetime(valid_outages, valid_filtered_outages_dt):
    # Call the function
    filtered_outages_dt = filter_outages_by_datetime(outages = valid_outages)

    # We can assert the correct responses - we know the outages data must be 58 data points long
    assert len(filtered_outages_dt) == 58

    # We can also call the pytest fixture directly to make sure the results match
    assert filtered_outages_dt == valid_filtered_outages_dt

"""
Site-info filter function - filter outages that do not exist in the site-info data
"""

def test_valid_outages_filter_with_invalid_site_info(valid_filtered_outages_dt, invalid_site_info):
    # Note - invalid outages will never reach this function, so we shouldn't get any actual RuntimeErrors raised in this function...
    # If device.get("id") doesn't exist, device.get("id") == None... thus the outage will filter out all outages without error
    filtered_outages = filter_outages_by_site_info(filtered_outages_dt = valid_filtered_outages_dt, site_info_data = invalid_site_info)

    # Due to behaviour outlined above, we have an easy assertion... our result should be a completely empty result set
    assert not filtered_outages
    assert len(filtered_outages) == 0

def test_valid_outages_filter_with_valid_site_info(valid_filtered_outages_dt, valid_site_info):
    # Call our function
    filtered_outages = filter_outages_by_site_info(filtered_outages_dt = valid_filtered_outages_dt, site_info_data = valid_site_info)

    # We can assert the correct responses - we know the outages data must be 10 data points long
    assert len(filtered_outages) == 10

"""
Producing our final output - 'producing_final_output' function
"""

def test_valid_output_with_valid_filtered_outages(valid_final_output, valid_filtered_outages, valid_site_info):
    # Call our function
    final_output = produce_final_output(filtered_outages = valid_filtered_outages, site_info_data = valid_site_info)

    # Assert that our output is the as we expect
    assert final_output == valid_final_output

"""
Testing final POST function
"""

def test_post_invalid_final_output(valid_api_url, valid_headers, requests_session, invalid_final_output):
    # Try to issue POST request with invalid final output
    response = post_results(api_endpoint_url = valid_api_url, headers = valid_headers, requests_session = requests_session, data = invalid_final_output)

    # We should 400 response, our payload isn't correct & won't be accepted
    assert response.status_code == 400
    # We should be able to assert the response message
    assert response.json()["message"] == "Unexpected outages received"

def test_post_valid_final_output(valid_api_url, valid_headers, requests_session, valid_final_output):
    # Try to issue POST request with invalid final output
    response = post_results(api_endpoint_url = valid_api_url, headers = valid_headers, requests_session = requests_session, data = valid_final_output)

    # We should 200 success response
    assert response.status_code == 200