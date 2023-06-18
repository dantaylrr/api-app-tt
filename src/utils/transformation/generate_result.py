import logging

# Instantiate logger at module level using the "__name__" variable
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def produce_final_output(filtered_outages: dict, site_info_data: dict):
    try:
        # We use our device list again so that we can match the "name" parameters
        devices = site_info_data.get("devices")

        """
        Avoiding using a list comprehension here as we are manipulating an existing list, not generating a new one
        Using a nested for loop is more readable that a list comprehension in this case
        In the spirit of FP & immutable data, we could construct a new list from scratch here - but not a requirement
        """
        # List through our filtered messages
        for outage in filtered_outages:
            # List through each device
            for device in devices:
                # If our ID exists in any of the device ID's we are looping through, append the device name to the original outage report
                if outage.get("id") in device.get("id"):
                    outage["name"] = device.get("name")
                else:
                    # Else, do nothing
                    pass

        # Return our output
        return filtered_outages

    except Exception as ex:
        logger.error(
            f"Failure to generate output JSON for POST request due to: {ex} - raising RuntimeError to prevent further downstream errors."
        )
        raise RuntimeError(
            f"Failure to generate output JSON for POST request due to: {ex}."
        )
