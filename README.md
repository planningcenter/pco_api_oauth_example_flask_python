# PCO API OAuth/OIDC Example - Flask + Python

This is an example Flask app for demonstrating how one might build an app to authenticate any PCO user
and then subsequently use that authentication to query the API.

You can learn more about Planning Center's API [here](https://developer.planning.center/docs).

## Setup

1. Create an app at [api.planningcenteronline.com](https://api.planningcenteronline.com/oauth/applications).

   Set the callback URL to be `http://localhost:5000/auth/complete`.

2. Install the required packages:

   ```bash
   pip install pipenv
   pipenv install
   ```

3. Set your Application ID and Secret in the environment and run the app:

   ```bash
   export OAUTH_APP_ID=abcdef0123456789abcdef0123456789abcdef012345789abcdef0123456789a
   export OAUTH_SECRET=0123456789abcdef0123456789abcdef012345789abcdef0123456789abcdef0
   export OAUTHLIB_INSECURE_TRANSPORT=1
   pipenv run flask run
   ```

   Note: the `OAUTHLIB_INSECURE_TRANSPORT` environment variable should only be used in development mode when testing locally.

4. Visit [localhost:5000](http://localhost:5000).

## Copyright & License

Copyright Ministry Centered Technologies. Licensed MIT.
