import logging
from asyncio import CancelledError
from datetime import datetime
from os.path import exists
from pathlib import Path

import yaml
from scheduler import SchedulerError

BLANK_STATE = {
    "wan_ip": "127.0.0.1",
    "last_ip_change": datetime.now().isoformat(),
    "last_successful_run": datetime.now().isoformat(),
    "last_failed_run": "1970-01-01T00:00:00.000000",
    "last_fatal_mail_sent": "1970-01-01T00:00:00.000000",
}
CONFIGS_PATH = Path(__file__).resolve().parent.parent.joinpath("configs")
CONFIG_PATH = Path(CONFIGS_PATH).joinpath("config.yaml")
STATE_PATH = Path(CONFIGS_PATH).joinpath("state.yaml")

logger = logging.getLogger('dynip')


def load_config():
    if not exists(CONFIG_PATH):
        logger.error("Could not find %s", CONFIG_PATH)
        fail_exit()

    with open(CONFIG_PATH, encoding="utf-8") as file_handle:
        return yaml.safe_load(file_handle)


def init_logger(config):
    logging.basicConfig(
        format=config["log_format"],
        datefmt=config["log_datefmt"],
        level=logging.getLevelName(config["log_level"]),
    )
    logger.debug('Running dynip with config file: %s', CONFIG_PATH)


def get_state():
    """Gets the state object from disk."""
    if not exists(STATE_PATH):
        state = BLANK_STATE
    else:
        with open(STATE_PATH, encoding="utf-8") as file_handle:
            state = yaml.safe_load(file_handle)
        if state is None or not state:
            state = BLANK_STATE
    return state


def write_state(state):
    """Writes state object to disk."""
    with open(STATE_PATH, mode="wt", encoding="utf-8") as state_file:
        yaml.dump(state, state_file)


def abort_on_failure(label, resp):
    """Abort this script completely if the response is non 200 status."""
    if resp is not None and resp.status_code != 200:
        logger.error("FATAL HTTP ERROR...")
        logger.warning(f"Non-200 status code from {label} api.")
        logger.warning(f"url: {resp.url}")
        logger.warning(f"status_code: {resp.status_code}")
        logger.warning(f"elapsed: {resp.elapsed}")
        logger.warning(f"resp body: {resp.text}")
        fail_exit()


def timeout_abort(config, label, url):
    """Abort this script and log it as a timeout error."""
    reqs_timeout = config["requests_timeout_seconds"]
    logger.error("FATAL TIMEOUT ERROR...")
    logger.warning("Timeout from %s api.", label)
    logger.warning("url: %s", url)
    logger.warning("timeout seconds: %s", reqs_timeout)
    logger.warning("retries: %s", config["getreq_retry_limit"])
    fail_exit()


def success_exit(new_states=None):
    """Updates state yaml and exits with OK exit code."""
    state = get_state()
    if new_states is not None:
        for key in new_states:
            state[key] = new_states[key]
    state["last_successful_run"] = datetime.now().isoformat()
    write_state(state)
    raise CancelledError("All good")


def fail_exit():
    """Updates state yaml and exits with error exit code."""
    state = get_state()
    state["last_failed_run"] = datetime.now().isoformat()
    write_state(state)
    raise SchedulerError("Failed exit")
