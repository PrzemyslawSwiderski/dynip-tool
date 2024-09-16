import json
import logging

import requests

from common import get_with_retry, success_exit, timeout_abort, abort_on_failure

logger = logging.getLogger('dynip')


def name_com_update(config, wan_ip):
    record_api_url = (
        f"https://{config['api_host']}/v4/domains/"
        f"{config['domain_name']}/records/"
        f"{str(config['domain_id'])}"
    )
    auth_params = (config["username"], config["token"])
    get_resp = get_with_retry(config, "record_list_api", api_auth=auth_params)
    existing_record = get_resp.json()
    if existing_record["answer"] == wan_ip:
        logger.info("IP is already the same: %s", wan_ip)
        success_exit({"wan_ip": wan_ip})
    existing_record["answer"] = wan_ip
    # name.com enforces 5 minutes as the minimum.
    # Assert that minimum, since this is for a dynamic IP.
    existing_record["ttl"] = 300
    try:
        put_resp = requests.put(
            record_api_url,
            auth=auth_params,
            headers={"Content-Type": "application/json"},
            data=json.dumps(existing_record),
            timeout=config["requests_timeout_seconds"],
        )
    except requests.exceptions.ReadTimeout:
        timeout_abort(config, "UPDATERECORD", record_api_url)
    except requests.exceptions.ConnectionError:
        timeout_abort(config, "UPDATERECORD", record_api_url)
    abort_on_failure("UPDATERECORD", put_resp)
