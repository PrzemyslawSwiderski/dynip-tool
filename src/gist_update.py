import logging
import time

import requests

logger = logging.getLogger('dynip')


def update_gist(config, wan_ip):
    github_config = config["github_gist"]
    if not github_config["enabled"]:
        return

    url = github_config["gists_url"]
    gist_id = github_config["gist_id"]
    gist_url = f"{url}/{gist_id}"
    reqs_timeout = github_config["requests_timeout_seconds"]
    retry_limit = github_config["retry_limit"]
    api_token = github_config["api_token"]

    response = None
    tries = 0
    while True:
        try:
            response = requests.patch(gist_url,
                                      headers={"Authorization": f"Bearer {api_token}"},
                                      json={
                                          "public": "false",
                                          "files": {
                                              "wan_ip.txt": {"content": wan_ip}
                                          }
                                      },
                                      timeout=reqs_timeout)
            break
        except (requests.exceptions.ReadTimeout, requests.exceptions.ConnectionError):
            tries += 1
            if tries < retry_limit:
                time.sleep(reqs_timeout)
                continue
            logger.error("Error while publishing gist file.")
            break
    if (response is not None and
            response.status_code == 200):
        logger.info("Successfully updated gist file.")
    else:
        logger.error("Could not update gist file.")
