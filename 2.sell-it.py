import pyotp
import robin_stocks.robinhood as r
import json
import requests
from requests.exceptions import ConnectionError, RequestException
import sys
import pandas as pd
from pandas_market_calendars import get_calendar
import time
from tqdm import tqdm

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

previous_opportunity_ids = set()
refresh()

def sell_stock(contact_id, companycode, variation):
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
                        if variation == 0:
                            holdings = r.account.build_holdings()
                            for key, value in holdings.items():
                                if companycode in key:
                                    quanity = float(value["quantity"])
                            r.order_sell_market(companycode, quanity, timeInForce='gfd')
                        if variation == 1:
                            r.order_sell_market(companycode,1, timeInForce='gfd')
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

def make_api_call(contact_id, companycode, variation):
    global ath_token
    #print("Action: Perform action using opportunity data")
    # Example: Print opportunity details
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
            if 'splitfinder active subscriber' in contact_data['contact']['tags']:
                custom_field_id = '63lEYSXP4udvhszg07g0'
                sell_stock(contact_id, companycode, variation)
                break
            else:
                break
        except ConnectionError:
            print("Error: Unable to establish a connection. Please check your internet connection.")
            time.sleep(300)
        except requests.exceptions.HTTPError as e:
            time.sleep(300)
            refresh()
        except RequestException as e:
            print(f"Error: {e}")

def is_nyse_open(date):
    nyse_calendar = get_calendar("XNYS")
    return nyse_calendar.valid_days(start_date=date, end_date=date).shape[0] == 1

def run_code(variation):
    global companycode
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
            make_api_call(contact_id, companycode, variation)
        else:
            print(f"Invalid contact info: {contact_info}")

def robinhood_manual_loggin(companycode):
    global ath_token
    url = f"https://services.leadconnectorhq.com/contacts/O5kbbgKb30DOdRFCFuKm"
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
                    while True:
                        try:
                            totp  = pyotp.TOTP(contactkey).now()
                            login = r.login(contactemail, contactpassword, mfa_code=totp, pickle_name = "O5kbbgKb30DOdRFCFuKm")
                            holdings = r.account.build_holdings()
                            logout = r.logout()
                            for key, value in holdings.items():
                                if companycode in key:
                                    #price = float(value["price"])
                                    quanity = float(value["quantity"])
                                    average_buy_price = float(value["average_buy_price"])
                                    if quanity < 1:
                                        run_code(0)
                                        break
                                    if average_buy_price == 0:
                                        run_code(1)
                                        break
                        except Exception as e:
                            error_message = str(e)
                            if "Unable to log in with provided credentials." in error_message:
                                print(f"Error: Unable to log in ({contact_id}). Please check your credidentails")
                            else:
                                print(f"Error: {error_message}")
                        time.sleep(24 * 60 * 60)
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

def wait_for_sell():
    global companycode
    while True:
        try:
            login = r.login()
            holdings = r.account.build_holdings()
            logout = r.logout()
            for key, value in holdings.items():
                if companycode in key:
                    #price = float(value["price"])
                    quanity = float(value["quantity"])
                    average_buy_price = float(value["average_buy_price"])
                    if quanity < 1:
                        run_code(0)
                        break
                    if average_buy_price == 0:
                        run_code(1)
                        break
        except Exception as e:
            error_message = str(e)
            if "Unable to log in with provided credentials." in error_message:
                print(f"Error: Unable to log in. Please check your creditentials.")
            elif "There was an issue loading pickle file. Authentication may be expired - logging in normally." in error_message:
                robinhood_manual_loggin(companycode)
                break
            else:
                print(f"Error: {error_message}")
        time.sleep(24 * 60 * 60)  # Wait for one day (24 hours) before checking again

if len(sys.argv) != 2:
    #print("Usage: python script.py <companycode>")
    sys.exit(1)
# Get command-line arguments and assign them to variables
companycode = sys.argv[1]

def main():
    robinhood_manual_loggin(companycode)

if __name__ == "__main__":
    main()

