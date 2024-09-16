import logging
import time

import requests

from common import success_exit
from src.common import fail_exit

logger = logging.getLogger('dynip')


def get_ip_with_retry(url, config):
    """Gets the specified URL and retries if there's a timeout."""
    reqs_timeout = config["requests_timeout_seconds"]
    retry_limit = config["getreq_retry_limit"]
    tries = 0
    response = None
    while True:
        try:
            response = requests.get(url, timeout=reqs_timeout)
            break
        except (requests.exceptions.ReadTimeout, requests.exceptions.ConnectionError):
            tries += 1
            if tries < retry_limit:
                time.sleep(reqs_timeout)
                continue
            break
    return response


def get_wan_ip(config):
    """Gets the current wan IP."""
    pub_ip_urls = config["wan_ip_endpoints"]

    for url in pub_ip_urls:
        response = get_ip_with_retry(url, config)
        if (response is not None and
                response.status_code == 200 and
                response.headers["content-type"] == "text/plain"):
            return response.text

    logger.error("Could not find public IP")
    fail_exit()


def find_ip(config, startup_state):
    old_wan_ip = startup_state["wan_ip"]
    wan_ip = get_wan_ip(config)
    if wan_ip == old_wan_ip:
        logger.info("IP did not change: %s", wan_ip)
        success_exit()
