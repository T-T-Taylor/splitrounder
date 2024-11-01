import pyotp
import robin_stocks.robinhood as r
import json
import requests
from requests.exceptions import ConnectionError, RequestException
import sys
import subprocess
import time
from tqdm import tqdm
from datetime import datetime, timedelta

if len(sys.argv) != 2:
    print("Usage: python script.py <companycode>")
    sys.exit(1)
# Get command-line arguments and assign them to variables
companycode = sys.argv[1]

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

def robinhood(contact_id):
    global ath_token
    global companycode
    url = f"https://services.leadconnectorhq.com/contacts/{contact_id}"
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
                        totp  = pyotp.TOTP(contactkey).now()
                        login = r.login(contactemail, contactpassword, mfa_code=totp, pickle_name = contact_id)
                        open_prices = r.stocks.get_fundamentals(companycode,info="open")
                        if open_prices and isinstance(open_prices[0], (int, float, str)):
                            open_price_float = float(open_prices[0])
                            if open_price_float < 1:
                                r.order_buy_market(companycode,1)
                        else:
                            print('Invalid or empty open price')
                        logout = r.logout()
                    except Exception as e:
                        error_message = str(e)
                        if "Unable to log in with provided credentials." in error_message:
                            print(f"Error: Unable to log in ({contact_id}). Please check your credidentails")
                        else:
                            print(f"Error: {error_message}")
                else:
                    print('Contact fails to qualify')
            except NameError as e:
                print(f"Error: {e} - One or more variables are not defined.")
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

def make_api_call(contact_id):
    global ath_token
    global companycode
    url = f"https://services.leadconnectorhq.com/contacts/{contact_id}"
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
                if 'splitfinder active subscriber' in contact_data['contact']['tags']:
                    robinhood(contact_id)
                    break
                else:
                    print('Not an Active Subscriber')
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

def add_to_purchased_list(companycode):
    json_date = datetime.now()
    data = {
    f"{companycode}": f"{json_date}"
    }
    try:
        with open('purchased.json', 'r') as json_file:
            existing_data = json.load(json_file)
    except FileNotFoundError:
        existing_data = {}
    # Update existing data with new data
    existing_data.update(data)
    # Writing updated data back to the JSON file
    with open('purchased.json', 'w') as json_file:
        json.dump(existing_data, json_file)

def within_past_thirty_days(date_string):
    date = datetime.strptime(date_string, '%Y-%m-%d %H:%M:%S.%f')
    thirty_days_ago = datetime.now() - timedelta(days=30)
    return date >= thirty_days_ago

def purchased_within_thirty_days():
    global companycode
    search_string = f'{companycode}'
    with open('purchased.json', 'r') as json_file:
        data = json.load(json_file)
    found = False
    for key, date_string in data.items():
        if search_string in key:
            if within_past_thirty_days(date_string):
                found = True
                break  # Exit loop if any matching pair is found
    if found:
        return True
    else:
        return False

def already_in_account(contact_id):
    global companycode
    global ath_token
    url = f"https://services.leadconnectorhq.com/contacts/{contact_id}"
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
                        totp  = pyotp.TOTP(contactkey).now()
                        login = r.login(contactemail, contactpassword, mfa_code=totp, pickle_name = contact_id)
                        holdings = r.account.build_holdings()
                        for key, value in holdings.items():
                            if companycode in key:
                                return True
                            else:
                                return False
                        logout = r.logout()
                    except Exception as e:
                        error_message = str(e)
                        if "Unable to log in with provided credentials." in error_message:
                            print(f"Error: Unable to log in ({contact_id}). Please check your credidentails")
                        else:
                            print(f"Error: {error_message}")
                else:
                    print('Contact fails to qualify')
            except NameError as e:
                print(f"Error: {e} - One or more variables are not defined.")
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

def main():
    refresh()
    global companycode
    if purchased_within_thirty_days():
        sys.exit()
    contacts = []
    # Read the JSON file
    with open('contact_ids.json', 'r') as file:
        for line in file:
            try:
                contact_info = json.loads(line)
                contacts.append(contact_info)
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON: {e}")
    # Iterate through each dictionary in the list
    for contact_info in tqdm(contacts, desc="Processing contacts", unit="contact"):
        contact_id = contact_info.get('ContactID')
        if contact_id:
            if already_in_account(contact_id):
                sys.exit()
            make_api_call(contact_id)
        else:
            print(f"Invalid contact info: {contact_info}")
    print(f"Purchase Loop Completed for {companycode}")
    add_to_purchased_list(companycode)
    command = ['python', '2.sell-it.py', companycode]
    subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

if __name__ == "__main__":
    main()
