# Overview

This repository contains code base complementary to presentation about Authentication & Authorization in AWS API Gateway.

It consists of a small REST API that communicates with DynamoDB table containing basic info about books (author, title, year of publishing).

Each resource/method is secured with different authorization mechanisms:

- `GET /books/{id}` - Cognito User Pool authorizer (with OKTA as SAML provider),
- `DELETE /books/{id}` - IAM authorizer,
- `GET /books` - Lambda authorizer,
- `POST /books` - combination of all above.


# Environment setup

## Prerequisites

Following tools should be installed:

- [Python 3.7](https://www.python.org/downloads/) (most likely versions >= 3.8 will work as well, although they were not tested)
- [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-install.html)
- [Serverless framework](https://www.serverless.com/framework/docs/providers/aws/guide/installation/)
- [Docker](https://docs.docker.com/get-docker/) for non-Linux users

Additionally you will need:

- AWS account (plus IAM role/user with administrator access),
- [OKTA](https://developer.okta.com/) free developer account.

## Plugins installation

In repository root folder run following commands:

```sh
sls plugin install -n serverless-python-requirements
sls plugin install -n serverless-wsgi
```

## Configuration file

In repository root folder create `aws-config.yml` file with following keys:
- `domainName`: domain prefix for Amazon Cognito domain, must be unique across the selected AWS Region and can only contain lower-case letters, numbers, and hyphens (example: `super-unique-domain-name`),
- `oktaMetadata`: leave it blank, you will fill it later,
- `region`: selected AWS Region (example: `eu-west-1`).

**Note:** to check domain prefix availability in your region, enter `https://<your-domain-prefix>.auth.<aws-region>.amazoncognito.com/` in a web browser. If you don't get any response, the domain is available.

## OKTA configuration & deployment to AWS

1. Follow the steps from [this guide](https://aws.amazon.com/premiumsupport/knowledge-center/cognito-okta-saml-identity-provider/), from `Sign up for an Okta developer account` to `Get the IdP metadata for your Okta application`. 

    **Important:** In `Configure SAML integration for your Okta app` step, point 5, you don't have user pool id yet, so you will replace `yourUserPoolId` placeholder later.
    
2. Copy the metadata URL from the last step and paste it into your `aws-config.yml` file.

3. In repository root folder use AWS CLI to assume your IAM role with administrator access.

4. In repository root folder run command `sls deploy --verbose`.

5. Copy `UserPoolId` from stack outputs.

6. Go back to your OKTA app. In `General` tab, edit `SAML Settings`. Replace `yourUserPoolId` placeholder in `Audience URI` field with user pool id obtained in previous step. Save the changes.

# Obtaining API token from Cognito user pool

## Constructing authorization URL

1. Copy `ClientId` from stack outputs (you can also find it in Cognito web console in `App client settings`).

2. Replace placeholders in following URL with your domain prefix, region and Cognito client id, respectively:

```
https://<your-domain-prefix>.auth.<aws-region>.amazoncognito.com/oauth2/authorize?response_type=token&client_id=<client-id>&redirect_uri=http://localhost:8080/login&scope=email+openid+profile
```

## Signing in

1. Enter the authorization URL from previous step in your web browser.

2. Use your OKTA credentials to log in.

3. You will be redirected to

```
http://localhost:8080/login#access_token=<access_token>&id_token=<id_token>&token_type=Bearer&expires_in=3600
```

Copy `id_token` and use it to authorize your API requests by adding header 

```
Authorization: Bearer <id_token>
```

**Note:** As there's no application running on localhost, the browser will display an error when you're redirected from OKTA. This is an expected behaviour for this demo.
