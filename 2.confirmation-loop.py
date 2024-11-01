import requests
import schedule
import time
import subprocess
import json
from requests.exceptions import ConnectionError, RequestException

previous_opportunity_ids = set()

def load_config(file_path):
    with open(file_path, 'r') as f:
        config = json.load(f)
    return config

ath_token = "token"

def refresh():
    global ath_token
    config_file_path = 'config.json'
    config = load_config(config_file_path)
    ath_token = config["access_token"]

refresh()

def delete_opportunites(opportunity_id):
    global ath_token
    url = f"https://services.leadconnectorhq.com/opportunities/{opportunity_id}"
    headers = {
        "Authorization": f"Bearer {ath_token}",
        "Version": "2021-07-28",
        "Accept": "application/json"
    }
    while True:
        try:
            response = requests.delete(url, headers=headers)
            response.raise_for_status()
            if response.ok:
                break
            else:
                print(f"Error: {response.status_code} - {response.text}")
        except ConnectionError:
            print("Error: Unable to establish a connection. Please check your internet connection.")
            time.sleep(300)
        except requests.exceptions.HTTPError as e:
            time.sleep(300)
            refresh()
        except RequestException as e:
            print(f"Error: {e}")
            break

def run_subproccess(ContactID, opportunity):
    global ath_token
    url = f"https://services.leadconnectorhq.com/contacts/{ContactID}"
    headers = {
        "Authorization": f"Bearer {ath_token}",
        "Version": "2021-07-28",
        "Accept": "application/json"
    }
    while True:
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            # Check if the request was successful (status code 2xx)
            if response.ok:
                contact_data = response.json()
            else:
                print(f"Error: {response.status_code} - {response.text}")
            custom_field_id = '63lEYSXP4udvhszg07g0'
            for custom_fields in contact_data['contact']['customFields']:
                if custom_fields['id'] == custom_field_id:
                    contactemail = custom_fields['value']
                    break
            custom_field_id = 'hDUzIJ2rbxaIFt6rlhvy'
            for custom_fields in contact_data['contact']['customFields']:
                if custom_fields['id'] == custom_field_id:
                    contactpassword = custom_fields['value']
                    break
            custom_field_id = '6aRFCb0wMpUfkTq1IIQH'
            for custom_fields in contact_data['contact']['customFields']:
                if custom_fields['id'] == custom_field_id:
                    contactkey = custom_fields['value']
                    break
            try:
                if contactemail and contactpassword and contactkey:
                    try:
                        subprocess.run(['python3', '2.login-confirmation.py', contactemail, contactpassword, contactkey, ContactID], check=True)
                    except subprocess.CalledProcessError as e:
                        print(f"Error: {e}")
                else:
                    print('Contact fails to qualify')
            except NameError as e:
                print(f"Error: {e} - One or more variables are not defined.")
            delete_opportunites(opportunity['id'])
            break
        except ConnectionError:
            print("Error: Unable to establish a connection. Please check your internet connection.")
            time.sleep(300)
        except requests.exceptions.HTTPError as e:
            time.sleep(300)
            refresh()
        except RequestException as e:
            print(f"Error: {e}")
            break

def fetch_opportunities():
    global previous_opportunity_ids
    global ath_token
    url = "https://services.leadconnectorhq.com/opportunities/search"
    querystring = {"location_id":"slyxLRE59hLFpE9hWKna","pipeline_id":"eJd3yIkoiPy7eYyBaxtq"}
    headers = {
        "Authorization": f"Bearer {ath_token}",
        "Version": "2021-07-28",
        "Accept": "application/json"
    }
    try:
        response = requests.get(url, headers=headers, params=querystring)
        response.raise_for_status()
        # Check if the request was successful (status code 2xx)
        if response.ok:
            opportunities_data = response.json()
            new_opportunities = [opportunity for opportunity in opportunities_data['opportunities'] if opportunity['id'] not in previous_opportunity_ids]
            # Identify new opportunities by comparing with previous opportunities
            new_opportunity_ids = set(opportunity['id'] for opportunity in new_opportunities)
            if new_opportunity_ids:
                # Perform action for each new opportunity
                for opportunity in new_opportunities:
                    # Example: Print opportunity details
                    ContactID = opportunity['contact']['id']
                    run_subproccess(ContactID, opportunity)
            # Update the set of previous opportunity IDs
            previous_opportunity_ids.update(new_opportunity_ids)
        else:
            print(f"Error: {response.status_code} - {response.text}")
    except ConnectionError:
        print("Error: Unable to establish a connection. Please check your internet connection.")
    except requests.exceptions.HTTPError as e:
        print("reconnecting to server")
        refresh()
    except RequestException as e:
        print(f"Error: {e}")

# Schedule the task to run every minute
schedule.every(1).minutes.do(fetch_opportunities)

# Keep the script running to allow the scheduled tasks to execute
while True:
    schedule.run_pending()
    time.sleep(1)
