import json

import requests


def get_google_provider_cfg():
    """obtains google config data"""
    return requests.get(
        "https://accounts.google.com/.well-known/openid-configuration"
        ).json()