import json
from typing import Dict, Optional


def make_response(method_arn: str, claims: Optional[Dict]) -> Dict:
    if claims is None:
        effect = 'Deny'
        principal_id = None
        info = {}
    else:
        effect = 'Allow'
        principal_id = claims.get('cognito:username') or claims.get('caller_arn')
        info = {'username': principal_id,
                'groups': json.dumps(claims.get('cognito:groups'))}
    resource = f'{method_arn[:method_arn.index("/")]}/*/*'
    return {'principalId': principal_id, 'context': info,
            'policyDocument':
                {
                    'Version': '2012-10-17',
                    'Statement': {
                        'Sid': f'{effect}InvokeApi',
                        'Action': 'execute-api:Invoke',
                        'Effect': effect,
                        'Resource': resource
                    }
                }
            }
