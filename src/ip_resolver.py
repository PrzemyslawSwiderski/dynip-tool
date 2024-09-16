import logging

from common import success_exit, get_with_retry
from src.common import fail_exit

logger = logging.getLogger('dynip')


def get_wan_ip(config):
    """Gets the current wan IP."""
    pub_ip_urls = config["wan_ip_endpoints"]

    for url in pub_ip_urls:
        wan_ip = get_with_retry(url, config, "wan_ip_endpoint").text
        return wan_ip

    logger.error("Could not find public IP")
    fail_exit()


def find_ip(config, startup_state):
    old_wan_ip = startup_state["wan_ip"]
    wan_ip = get_wan_ip(config)
    if wan_ip == old_wan_ip:
        logger.info("IP did not change: %s", wan_ip)
        success_exit()
