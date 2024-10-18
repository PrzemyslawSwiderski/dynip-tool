#!/bin/python3
"""Update DNS records for dynamic IP."""
import asyncio
import datetime as dt
import logging
from asyncio import CancelledError
from scheduler import SchedulerError
from scheduler.asyncio import Scheduler

from common import load_config, init_logger, get_state, success_exit
from gist_update import update_gist
from ip_resolver import get_wan_ip
from name_com_update import name_com_update

logger = logging.getLogger('dynip')


async def perform_update():
    config = load_config()
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
            "last_ip_change": dt.datetime.now().isoformat(),
        }
    )


async def try_update():
    try:
        await perform_update()
    except CancelledError:
        logger.info("IP is up to date, nothing to do.")
    except SchedulerError as err:
        logger.warning("Something went wrong: %s", err)


async def main():
    """Main app execution code."""
    config = load_config()
    init_logger(config)
    check_interval_in_minutes = config["check_interval_in_minutes"]
    logger.info("Starting the application and scheduling IP update in %s minutes.", check_interval_in_minutes)
    schedule = Scheduler()
    schedule.cyclic(dt.timedelta(minutes=check_interval_in_minutes), try_update)

    while True:
        await asyncio.sleep(1)


asyncio.run(main())
