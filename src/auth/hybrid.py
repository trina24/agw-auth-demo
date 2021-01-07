from typing import Any, Dict

from src.auth import make_response
from src.auth.iam import IamAuthorizer
from src.auth.token import TokenAuthorizer


def handler(event: Dict, context: Any) -> Dict:
    headers = event['headers']
    auth_header = headers.get('Authorization') or headers.get('authorization')
    is_token = (auth_header or '').startswith('Bearer ')
    if is_token:
        info = TokenAuthorizer(auth_header).claims
    else:
        info = IamAuthorizer(event['headers']).response
    return make_response(event['methodArn'], info)
