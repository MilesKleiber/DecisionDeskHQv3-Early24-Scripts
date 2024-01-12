import requests
import json
import time
import os


# This is a python script to use the bearer token provided from ddhqauth.py to pull election data from DecisionDeskHQ.
#
# YOU NEED YOUR OWN DDHQ CLIENT CREDS TO USE THESE SCRIPTS.


dirRefData = 'referenceData/'
filteredfp = 'CaucusData/'

states = [
    "Iowa",
    "New Hampshire",
    "Nevada",
    "Michigan",
    "Idaho",
    "Missouri"
]
print("Select a state by entering the corresponding number:")
for i, state in enumerate(states, start=1):
    print(f"{i}. {state}")
while True:
    try:
        user_choice = int(input("Which state? "))
        if 1 <= user_choice <= len(states):
            setstate = states[user_choice - 1]
            print(f"You selected: {setstate}")
            break
        else:
            print("Invalid input. Please enter a valid number.")
    except ValueError:
        print("Invalid input. Please enter a valid number.")

state_dir = filteredfp + setstate + '/'
if not os.path.exists(state_dir):
    os.makedirs(state_dir)
    print(f"Directory '{state_dir}' created successfully.")
else:
    print(f"Directory '{state_dir}' already exists. Continuing.")


def pull_data(setstate):
    url = (f'https://resultsapi.decisiondeskhq.com/api/v3/races?limit=1&page=1&year=2024'
           f'&state_name={setstate}&party_id=2')
    with open('bearer_token.txt', 'r') as token_val:
        token_val = token_val.read()
    headers = {
        'Accept': 'application/json',
        'Authorization': f"Bearer {token_val}"
    }
    print("Pulling data at: " + time.strftime("%Y-%m-%d %H:%M:%S"))
    response = requests.request("GET", url, headers=headers)
    if response.status_code == 200:
        response_data = response.json()
        with open(state_dir + 'response_data.json', 'w') as response_file:
            json.dump(response_data, response_file, indent=4)
        print("Data was retrieved and written to response_data.json")
    else:
        print("GET request failed with status code:", response.status_code)


def data_filter():
    with open(state_dir + 'response_data.json', 'r') as response_file:
        response_data = json.load(response_file)

    cand_list = response_data['data'][0]['candidates']
    for candidates in cand_list:
        cand_name = candidates['last_name']
        cand_id = candidates['cand_id']
        total_votes = response_data['data'][0]['topline_results']['total_votes']
        cand_votes = response_data['data'][0]['topline_results']['votes'].get(str(cand_id))
        file_name = f"{cand_name}_{setstate}_votes.txt"
        with open(state_dir + file_name, 'w') as file:
            file.write(str(cand_votes))
        if cand_votes <= 0.0:
            cand_percent = 0.0
        elif total_votes <= 0.0:
            cand_percent = 0.0
        else:
            cand_percent = float(cand_votes / total_votes) * 100
        pfile_name = f"{cand_name}_{setstate}_percent.txt"
        with open(state_dir + pfile_name, 'w') as file:
            file.write(f"{cand_percent:.2f}%")

    precincts_totalf = 'precincts_total_count.txt'
    precincts_total = response_data['data'][0]['topline_results']['precincts']['total']
    with open(state_dir + precincts_totalf, 'w') as ptfile:
        ptfile.write(str(precincts_total))

    precincts_reportingf = 'precincts_reporting_count.txt'
    precincts_reporting = response_data['data'][0]['topline_results']['precincts']['reporting']
    with open(state_dir + precincts_reportingf, 'w') as prfile:
        prfile.write(str(precincts_reporting))

    precincts_reportingpf = 'precincts_reporting_percent.txt'
    if precincts_reporting <= 0.0:
        precincts_reporting_percent = 0.0
    elif precincts_total <= 0.0:
        precincts_reporting_percent = 0.0
    else:
        precincts_reporting_percent = float(precincts_reporting/precincts_total) * 100
    with open(state_dir + precincts_reportingpf, 'w') as prpfile:
        prpfile.write(f"{precincts_reporting_percent:.2f}%")

        # UNCOMMENT FOR TEST PRINTOUT.
        # test_print(cand_name, cand_id, cand_votes, total_votes, cand_percent)


def test_print(cand_name, cand_id, cand_votes, total_votes, cand_percent):
    print("Name: " + cand_name)
    print("ID: " + str(cand_id))
    print("cand_votes: " + str(cand_votes))
    print("Total votes: " + str(total_votes))
    print("Percentage: " + str(cand_percent))
    print("\n")


minterval = int(input("Set data refresh interval in minutes: "))
interval = minterval * 60
while True:
    pull_data(setstate)
    data_filter()
    time.sleep(interval)
