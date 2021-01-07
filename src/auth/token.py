from time import time
from typing import Any, Dict, Optional

import requests
from jose import jwk, jwt
from jose.exceptions import JOSEError
from jose.utils import base64url_decode

from src.auth import make_response
from src.config import AWS_REGION, COGNITO_APP_CLIENT_ID, COGNITO_USERPOOL_ID


def handler(event: Dict, context: Any) -> Dict:
    token = event['authorizationToken']
    claims = TokenAuthorizer(token).claims
    return make_response(event['methodArn'], claims)


class TokenAuthorizer:
    idp_url = f'https://cognito-idp.{AWS_REGION}.amazonaws.com'
    keys = requests.get(f'{idp_url}/{COGNITO_USERPOOL_ID}/.well-known/jwks.json'
                        ).json()['keys']

    def __init__(self, token: str) -> None:
        self.token = token.replace('Bearer ', '')

    @property
    def claims(self):
        return self.verify_token(self.token)

    @classmethod
    def verify_token(cls, token: str) -> Optional[Dict]:
        try:
            kid = jwt.get_unverified_headers(token)['kid']
            key = next(key for key in cls.keys if key['kid'] == kid)
            public_key = jwk.construct(key)
            message, encoded_signature = str(token).rsplit('.', 1)
            decoded_signature = base64url_decode(encoded_signature.encode('utf-8'))
            if public_key.verify(message.encode('utf8'), decoded_signature):
                claims = jwt.get_unverified_claims(token)
                if time() <= claims['exp'] and claims['aud'] == COGNITO_APP_CLIENT_ID:
                    return claims
        except (StopIteration, JOSEError):
            return None
