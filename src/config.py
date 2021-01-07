from prettyconf import config

AWS_REGION = config('AWS_REGION', default='eu-west-1')
COGNITO_APP_CLIENT_ID = config('COGNITO_APP_CLIENT_ID', default='')
COGNITO_USERPOOL_ID = config('COGNITO_USERPOOL_ID', default='')
TABLE_NAME = config('DYNAMO_TABLE_NAME', default='agw-auth-demo')
