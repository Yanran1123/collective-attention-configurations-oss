import requests


def get_remaining_rest_RESTV3(headers):
    """
    Return the remaining and reset information of GitHub REST API v3
    :param headers: Including information of the token and others
    :return remaining, rest: The remaining and reset information in the response
    """
    url = "https://api.github.com/repos/tensorflow/tensorflow/topics"
    response = requests.get(url, headers=headers)

    remaining = int(response.headers["x-ratelimit-remaining"])
    reset = int(response.headers["x-ratelimit-reset"])

    return remaining, reset
