import requests
import json


# This is a python script to pull the client creds in client_creds.json to retrieve a bearer token and use that
# as authentication for the request in ddhqdata.py.
#
# YOU NEED YOUR OWN DDHQ CLIENT CREDS TO USE THESE SCRIPTS.


print("Authenticating...")
with open('client_creds.json', 'r') as credentials:
    credentials = json.load(credentials)
authurl = "https://resultsapi.decisiondeskhq.com/oauth/token"
authpayload = credentials[0]
authheaders = {
    'Content-Type': 'application/x-www-form-urlencoded',
    'Accept': 'application/json'
}
response = requests.request("POST", authurl, headers=authheaders, data=authpayload)

if response.status_code == 200:
    response_data = response.json()
    bearer_token_val = response_data['access_token']
    with open('bearer_token.txt', 'w') as token_file:
        token_file.write(bearer_token_val)
    print("Authenticated. Token set to: " + str(bearer_token_val))
else:
    print("Failed to retrieve token data. Status code:", response.status_code)
