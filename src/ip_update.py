#!/bin/python3
"""Update DNS records for dynamic IP."""

import logging
from datetime import datetime

from common import load_config, init_logger, get_state, success_exit
from ip_resolver import find_ip
from name_com_update import name_com_update

logger = logging.getLogger('dynip')


def main():
    """Main app execution code."""
    config = load_config()

    init_logger(config)

    startup_state = get_state()

    wan_ip = find_ip(config, startup_state)

    name_com_config = config["dns_apis"]["NAME_COM"]
    # name_com_update(name_com_config, wan_ip)

    logger.info("Updated IP to %s", wan_ip)

    success_exit(
        {
            "wan_ip": wan_ip,
            "last_ip_change": datetime.now().isoformat(),
        }
    )


if __name__ == "__main__":
    main()
