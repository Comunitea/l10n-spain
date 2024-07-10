# Copyright 2022 Tecnativa - David Vidal
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import logging
from urllib.parse import urljoin

import requests
import datetime

from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

ATLAS_API_DOMAINS = {
    "prod": "servicios.api.seur.io",
    "test": "servicios.apipre.seur.io",
}


def log_request(method):
    """Decorator to write raw request/response in the SEUR request object"""

    def wrapper(*args, **kwargs):
        res = method(*args, **kwargs)
        try:
            res = args[0].response
            args[0].last_request = (
                "{method} request to {url}\n".format(method=res.request.method, url=res.request.url),
                "Headers: {}\n".format(res.request.headers),
                "Body: {}".format(res.request.body)
            )
            args[0].last_response = (
                "{code} {reason} {url}\n".format(code=res.status_code, reason=res.reason, url=res.url),
                "Headers: {}\n".format(res.headers),
                "Response:\n{}".format(res.text)
            )
        # Allow the decorator to fail
        except Exception:
            return res
        return res

    return wrapper


@log_request
def seur_method(http_method):
    """Decorator to attach our request custom headers in the SEUR request object"""

    def decorator(method):
        def wrapper(*args, **kwargs):
            # Only allow supported methods
            if http_method not in ["GET", "POST"]:
                return
            self, *_ = args
            seur_method = method.__name__.replace("__", "/").replace("_", "-")
            request = {
                "method": http_method,
                "url": urljoin(self.api_url, "/pic/v1/{}".format(seur_method)),
                "headers": {"Authorization": "Bearer {}".format(self.token)},
            }
            if http_method == "POST":
                request["json"] = kwargs.get("payload", {})
            elif http_method == "GET":
                request["params"] = {**kwargs}
            self.response = requests.request(**request)
            if not self.response.ok:
                self.error = "\n".join(
                    [
                        "{title} ({status}): {details}".format(title=error['title'], status=error['status'], details=error['detail'])
                        for error in self.response.json().get("errors")
                    ]
                )
                raise UserError("SEUR ERROR: \n\n{}".format(self.error))
            res = method(*args, **kwargs)
            return res

        return wrapper

    return decorator


class SeurAtlasRequest:
    """Interface between SEUR Atlas API and the Odoo ORM. Abstracts Seur API Operations
    to connect them with the proper Odoo workflows.
    """

    def __init__(
        self, user, password, secret, client_id, acc_number, id_number, token= False, prod=False
    ):
        self.user = user
        self.password = password
        self.secret = secret
        self.client_id = client_id
        self.account_number = acc_number
        self.id_number = id_number
        self.last_request = False
        self.last_response = False
        self.response = False
        self.error = False
        self.token = token
        self.token_expiration = False
        self.api_url = "https://{}".format(ATLAS_API_DOMAINS['prod' if prod else 'test'])
        if not self.token:
            self._set_token()

    @log_request
    def _set_token(self):
        """In order to operate, we should gather a token from the API. This token
        lasts for 1 hour. After that, we must gather a new one"""
        self.response = requests.post(
            urljoin(self.api_url, "/pic_token"),
            data={
                "grant_type": "password",
                "client_id": self.client_id,
                "client_secret": self.secret,
                "username": self.user,
                "password": self.password,
            },
        )
        if not self.response.ok:
            self.error = self.response.json()
            return

        self.token = self.response.json()["access_token"]
        self.token_expiration = datetime.datetime.now() + datetime.timedelta(seconds=self.response.json()["expires_in"])

    # SEUR ATLAS API METHODS

    @seur_method("POST")
    def shipments(self, payload=None):
        return self.response.json()

    @seur_method("GET")
    def labels(self, **kw):
        return self.response.json()["data"]

    @seur_method("POST")
    def shipments__cancel(self, payload=None):
        return self.response.json()

    @seur_method("GET")
    def tracking_services__simplified(self, **kw):
        """Query the current shipping state for a given shipping reference"""
        return self.response.json()["data"][0]

    @seur_method("GET")
    def tracking_services__extended(self, **kw):
        """Query the current shipping state history  for a given shipping
        reference"""
        return self.response.json()["data"][0]["situations"]

    @seur_method("GET")
    def next_working_day(self, **kw):
        return self.response.json()["data"]["nextWorkingDay"]

    @seur_method("GET")
    def cities(self, **kw):
        return self.response.json()["data"][0]
