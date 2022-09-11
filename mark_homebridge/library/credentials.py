import json
import library.c_types as c_types
import os
import requests
import time
from settings import *


def get(name: str):
    cred_json = get_cred_json(name)

    # Check if token exists in data/tokens
    if not (name + "_token.json" in os.listdir(os.path.join(path(), "data", "creds"))):
        token = create_token(name, cred_json)

    else:
        # Get Token Modification Date
        m_time = os.path.getmtime(
            os.path.join(path(), "data", "creds", name + "_token.json")
        )

        # Check to see if token is valid
        if (m_time + 28300) > time.time():
            token = get_token(name)
        else:
            token = create_token(name, cred_json)

    auth_headers = get_auth_headers(token)
    return auth_headers


def get_cred_json(name: str):
    with open(os.path.join(path(), "data", "creds", name + ".json"), "r") as f:
        cred_json: c_types.Credentials = json.load(f)

    return cred_json


def create_token(name: str, cred_json: c_types.Credentials):
    creds = {
        "username": cred_json["username"],
        "password": cred_json["password"],
    }
    x = requests.post(cred_json["url"] + "auth/login", json=creds)
    token: dict[str, str] = x.json()

    # Write token to data/tokens
    with open(
        os.path.join(path(), "data", "creds", name + "_token.json"),
        "w",
    ) as f:
        json.dump(token, f)

    return token


def get_token(name: str):
    with open(
        os.path.join(path(), "data", "creds", name + "_token.json"),
        "r",
    ) as f:
        token: dict[str, str] = json.load(f)

    return token


def get_auth_headers(token: dict[str, str]):

    auth_headers = {
        "accept": "*/*",
        "Authorization": "Bearer " + str(token["access_token"]),
    }

    return auth_headers
