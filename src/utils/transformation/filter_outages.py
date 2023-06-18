import logging
from datetime import datetime

# Instantiate logger at module level using the "__name__" variable
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def filter_outages_by_datetime(outages: list[dict]):
    try:
        # Apply a list comprehension filter on our outages list & return a filtered list
        filtered_outages_dt = [
            outage
            for outage in outages
            if datetime.strptime(outage.get("begin"), "%Y-%m-%dT%H:%M:%S.%fZ")
            >= datetime(2022, 1, 1, 0, 0, 0, 0)
        ]

        # Return the filtered outages
        return filtered_outages_dt
    except Exception as ex:
        logger.error(
            f"Failure to successfully filter the outages object for 'begin' datetimes <= 2022-01-01T00:00:00.000Z, due to: {ex}."
        )
        # We can raise a RuntimeError as the final result must be correct for the application to successfully finish
        raise RuntimeError(
            f"Cannot perform successful filtering of outages data due to: {ex}."
        )


def filter_outages_by_site_info(filtered_outages_dt: dict, site_info_data: dict):
    try:
        # We need the "devices" dictionary from our site-info response
        devices = site_info_data.get("devices")

        # Apply another filter to our filtered_outages
        filtered_outages = [
            outage
            for outage in filtered_outages_dt
            if outage.get("id") in (device.get("id") for device in devices)
        ]

        # Return the filtered outages
        return filtered_outages

    except Exception as ex:
        logger.error(
            f"Failure to successfully filter the outages object for ID's that exist in our site-info data, due to: {ex}."
        )
        # We can raise a RuntimeError as the final result must be correct for the application to successfully finish
        raise RuntimeError(
            f"Cannot perform successful filtering of outages data due to: {ex}."
        )
