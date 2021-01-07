import json
import re
import os
from typing import Any, Dict, List

import requests
from boto3 import session
from botocore.auth import SigV4Auth
from botocore.awsrequest import AWSRequest
from requests.auth import AuthBase
from requests_aws4auth import AWS4Auth

from src.config import AWS_REGION

API_URL = os.environ.get('API_URL')


class Signature(AuthBase):

    def __call__(self, req: requests.Request) -> requests.Request:
        signed_headers = self.get_signed_headers(self.prepare_aws_request(req))
        req.headers.update(signed_headers)
        return req

    @classmethod
    def get_signed_headers(cls, req: AWSRequest) -> Dict:
        SigV4Auth(session.Session().get_credentials(), 'execute-api', AWS_REGION).add_auth(req)
        headers_list = str(req.headers).split('\n')
        headers = {}
        for key in ('X-Amz-Security-Token', 'X-Amz-Date', 'Authorization'):
            value = next(h for h in headers_list if h.startswith(key)).replace(f'{key}: ', '')
            headers[key] = value
        return headers

    @classmethod
    def prepare_aws_request(cls, req: requests.Request) -> AWSRequest:
        headers = {'Host': cls.extract_host(req.url)}
        return AWSRequest(method='GET', url=f'{API_URL}/auth', headers=headers)

    @classmethod
    def extract_host(cls, url: str) -> str:
        return re.search('/[a-z0-9-.]+/', url).group(0).strip('/')


def get_new_books() -> List[Dict]:
    # Let's just imagine it's a call to an external API that returns some new books
    with open('src/imports/dataset.json') as f:
        return json.loads(f.read())


def handler(event: Any, context: Any) -> None:
    payload = get_new_books()
    response = requests.post(f'{API_URL}/books', auth=Signature(), json=payload)

    # Single DELETE request - just to demonstrate how to sign requests with standard IAM auth
    book_id = next(book['id'] for book in response.json())
    credentials = session.Session().get_credentials()
    awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, 'eu-west-1', 'execute-api',
                       session_token=credentials.token)
    requests.delete(f'{API_URL}/books/{book_id}', headers={'Content-Type': 'application/json'},
                    auth=awsauth).json()
