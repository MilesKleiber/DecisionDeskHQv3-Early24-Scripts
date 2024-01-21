import requests
import json
import time
import os
# import ddhqauth

# This is a python script to use the bearer token provided from ddhqauth.py to pull election data from DecisionDeskHQ.
#
# YOU NEED YOUR OWN DDHQ CLIENT CREDS TO USE THESE SCRIPTS.


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

filteredfp = 'CaucusData/'
if not os.path.exists(filteredfp):
    os.makedirs(filteredfp)
    print(f"Directory '{filteredfp}' created successfully.")
else:
    print(f"Directory '{filteredfp}' already exists. Continuing.")

state_dir = filteredfp + setstate + '/'
if not os.path.exists(state_dir):
    os.makedirs(state_dir)
    print(f"Directory '{state_dir}' created successfully.")
else:
    print(f"Directory '{state_dir}' already exists. Continuing.")

state_deleg_dir = filteredfp + setstate + '_delegates/'
if not os.path.exists(state_deleg_dir):
    os.makedirs(state_deleg_dir)
    print(f"Directory '{state_deleg_dir}' created successfully.")
else:
    print(f"Directory '{state_deleg_dir}' already exists. Continuing.")

national_deleg_dir = filteredfp + 'national_delegates/'
if not os.path.exists(national_deleg_dir):
    os.makedirs(national_deleg_dir)
    print(f"Directory '{national_deleg_dir}' created successfully.")
else:
    print(f"Directory '{national_deleg_dir}' already exists. Continuing.")


def pull_data(url, categ):
    with open('bearer_token.txt', 'r') as token_val:
        token_val = token_val.read()
    headers = {
        'Accept': 'application/json',
        'Authorization': f"Bearer {token_val}"
    }
    print("Pulling data at: " + time.strftime("%Y-%m-%d %H:%M:%S"))
    response = requests.request("GET", url, headers=headers)
    if response.status_code == 200:
        if categ == "state":
            s_response_data = response.json()
            with open(state_dir + 'state_response_data.json', 'w') as s_response_file:
                json.dump(s_response_data, s_response_file, indent=4)
            print(f"State data was retrieved and written to '{state_dir}'state_response_data.json")
        elif categ == "deleg":
            d_response_data = response.json()
            with open(state_deleg_dir + 'deleg_response_data.json', 'w') as d_response_file:
                json.dump(d_response_data, d_response_file, indent=4)
            print(f"Delegate data was retrieved and written to '{state_deleg_dir}'deleg_response_data.json")
    else:
        print("GET request failed with status code:", response.status_code)


def state_filter():
    with open(state_dir + 'state_response_data.json', 'r') as s_response_file:
        s_response_data = json.load(s_response_file)

    cand_list = s_response_data['data'][0]['candidates']
    for candidates in cand_list:
        cand_name = candidates['last_name']
        cand_id = candidates['cand_id']
        total_votes = s_response_data['data'][0]['topline_results']['total_votes']
        cand_votes = s_response_data['data'][0]['topline_results']['votes'].get(str(cand_id))
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
            file.write(f"{cand_percent:.1f}")

    total_state_votes_in = s_response_data['data'][0]['topline_results']['total_votes']
    estimated_state_votes_high = s_response_data['data'][0]['topline_results']['estimated_votes']['estimated_votes_high']
    # precincts_totalf = 'precincts_total_count.txt'
    # precincts_total = s_response_data['data'][0]['topline_results']['precincts']['total']
    # with open(state_dir + precincts_totalf, 'w') as ptfile:
    #     ptfile.write(str(precincts_total))
    #
    # precincts_reportingf = 'precincts_reporting_count.txt'
    # precincts_reporting = s_response_data['data'][0]['topline_results']['precincts']['reporting']
    # with open(state_dir + precincts_reportingf, 'w') as prfile:
    #     prfile.write(str(precincts_reporting))

    precincts_reportingpf = 'precincts_reporting_percent.txt'
    if total_state_votes_in <= 0.0:
        precincts_reporting_percent = 0.0
    elif estimated_state_votes_high <= 0.0:
        precincts_reporting_percent = 0.0
    else:
        precincts_reporting_percent = float(total_state_votes_in / estimated_state_votes_high) * 100
    with open(state_dir + precincts_reportingpf, 'w') as prpfile:
        if precincts_reporting_percent == 100.0:
            prpfile.write("100")
        else:
            prpfile.write(f"{precincts_reporting_percent:.1f}")

        # UNCOMMENT FOR TEST PRINTOUT.
        # test_print(cand_name, cand_id, cand_votes, total_votes, cand_percent)


def delegate_filter():
    with open(state_deleg_dir + 'deleg_response_data.json', 'r') as d_response_file:
        d_response_data = json.load(d_response_file)

    state_delegate_republican_data = None
    national_delegate_republican_data = None
    for party_data in d_response_data['delegates']:
        if party_data['name'] == 'Republican':
            national_delegate_republican_data = party_data['national']
            for state_data in party_data['states']:
                if state_data['state_name'] == setstate:
                    state_delegate_republican_data = state_data['candidates']
                    state_delegate_vote_total = state_data['total']
                    break
    state_delegate_republican_ids = list(state_delegate_republican_data.keys())
    national_delegate_republican_ids = list(national_delegate_republican_data.keys())

    for candidate in d_response_data['candidates']:
        candidate_id = str(candidate['cand_id'])
        if candidate_id in national_delegate_republican_ids:
            cand_name = candidate['last_name']
            file_name = f"{cand_name}_national_delegate_votes.txt"
            with open(national_deleg_dir + file_name, 'w') as file:
                file.write(str(national_delegate_republican_data[candidate_id]))
        if candidate_id in state_delegate_republican_ids:
            cand_name = candidate['last_name']
            file_name = f"{cand_name}_{setstate}_delegate_votes.txt"
            with open(state_deleg_dir + file_name, 'w') as file:
                file.write(str(state_delegate_republican_data[candidate_id]))
            if state_delegate_vote_total <= 0.0:
                cand_percent = 0.0
            else:
                cand_percent = float(state_delegate_republican_data[candidate_id] / state_delegate_vote_total) * 100
            pfile_name = f"{cand_name}_{setstate}_delegate_percent.txt"
            with open(state_deleg_dir + pfile_name, 'w') as file:
                if cand_percent == 100.0:
                    file.write("100")
                else:
                    file.write(f"{cand_percent:.1f}")


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
    state_url = (f'https://resultsapi.decisiondeskhq.com/api/v3/races?limit=1&page=1&year=2024'
                 f'&state_name={setstate}&party_id=2')
    pull_data(state_url, categ='state')
    delegate_url = 'https://resultsapi.decisiondeskhq.com/api/v3/delegates/2024'
    pull_data(delegate_url, categ='deleg')
    state_filter()
    delegate_filter()
    time.sleep(interval)
