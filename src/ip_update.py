#!/bin/python3
"""Update DNS records for dynamic IP."""

import logging
from datetime import datetime

from common import load_config, init_logger, get_state, success_exit
from ip_resolver import get_wan_ip
from src.gist_update import update_gist
from src.name_com_update import name_com_update

logger = logging.getLogger('dynip')


def main():
    """Main app execution code."""
    config = load_config()

    init_logger(config)

    startup_state = get_state()

    old_wan_ip = startup_state["wan_ip"]
    wan_ip = get_wan_ip(config)
    if wan_ip == old_wan_ip:
        logger.info("IP did not change: %s", wan_ip)
        success_exit()
    else:
        update_gist(config, wan_ip)

    name_com_update(config, wan_ip)

    logger.info("Updated IP to %s", wan_ip)

    success_exit(
        {
            "wan_ip": wan_ip,
            "last_ip_change": datetime.now().isoformat(),
        }
    )


if __name__ == "__main__":
    main()
