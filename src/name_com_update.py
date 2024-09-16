import json
import logging
import time

import requests

from common import success_exit, timeout_abort, abort_on_failure

logger = logging.getLogger('dynip')


def get_with_retry(url, config, api_auth):
    """Gets the specified URL and retries if there's a timeout."""
    label = "record_list_api"
    reqs_timeout = config["requests_timeout_seconds"]
    retry_limit = config["getreq_retry_limit"]
    tries = 0
    resp = None
    while True:
        try:
            resp = requests.get(url, auth=api_auth, timeout=reqs_timeout)
            break
        except (requests.exceptions.ReadTimeout, requests.exceptions.ConnectionError):
            tries += 1
            if tries < retry_limit:
                time.sleep(reqs_timeout)
                continue
            timeout_abort(label, url, config)

    abort_on_failure(label, resp)
    return resp


def name_com_update(config, wan_ip):
    name_com_config = config["dns_apis"]["NAME_COM"]
    record_api_url = (
        f"https://{name_com_config['api_host']}/v4/domains/"
        f"{name_com_config['domain_name']}/records/"
        f"{str(name_com_config['domain_id'])}"
    )
    auth_params = (name_com_config["username"], name_com_config["token"])
    get_resp = get_with_retry(record_api_url, config, auth_params)
    existing_record = get_resp.json()
    if existing_record["answer"] == wan_ip:
        logger.info("IP is already the same: %s", wan_ip)
        success_exit({"wan_ip": wan_ip})
    existing_record["answer"] = wan_ip
    # name.com enforces 5 minutes as the minimum.
    # Assert that minimum, since this is for a dynamic IP.
    existing_record["ttl"] = 300
    put_resp = None
    try:
        put_resp = requests.put(
            record_api_url,
            auth=auth_params,
            headers={"Content-Type": "application/json"},
            data=json.dumps(existing_record),
            timeout=config["requests_timeout_seconds"],
        )
    except (requests.exceptions.ReadTimeout, requests.exceptions.ConnectionError):
        timeout_abort(config, "UPDATERECORD", record_api_url)
    abort_on_failure("UPDATERECORD", put_resp)
