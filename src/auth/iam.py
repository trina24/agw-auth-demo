import os
from typing import Dict, Optional

import requests


class IamAuthorizer:

    def __init__(self, headers: Dict) -> None:
        self.headers = {key: headers.get(key) or headers.get(key.lower())
                        for key in ('Authorization', 'X-Amz-Security-Token', 'X-Amz-Date')}

    @property
    def response(self):
        return self.verify_headers()

    def verify_headers(self) -> Optional[Dict]:
        response = requests.get(f'{os.environ.get("API_URL")}/auth',
                                headers=self.headers)
        if response.status_code == 200:
            body = response.json()
            if body.get('caller_arn').startswith(
                    f'arn:aws:sts::{os.environ.get("ACCOUNT_ID")}:assumed-role/'):
                return body
