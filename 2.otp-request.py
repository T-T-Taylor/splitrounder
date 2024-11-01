import requests
import schedule
import time
from datetime import datetime, timedelta
import pyotp
from requests.exceptions import ConnectionError, RequestException
import sys
import json

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

def fetch_opportunities():
    global previous_opportunity_ids
    global ath_token
    url = "https://services.leadconnectorhq.com/opportunities/search"
    querystring = {"location_id":"slyxLRE59hLFpE9hWKna","pipeline_id":"4mNesgQMjOI9UhgajVT0"}
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
                    contact_id = opportunity['contact']['id']
                    run_subproccess(contact_id, opportunity)
            # Update the set of previous opportunity IDs
            previous_opportunity_ids.update(new_opportunity_ids)
        else:
            print(f"Error: {response.status_code} - {response.text}")
    except ConnectionError:
        print("Error: Unable to establish a connection. Please check your internet connection.")
    except requests.exceptions.HTTPError as e:
        time.sleep(300)
        refresh()
    except RequestException as e:
        print(f"Error: {e}")

def contact_details(contact_data):
    existing_results = {}
    if 'firstName' in contact_data['contact']:
        firstName = contact_data['contact']['firstName']
    else:
        firstName = None
    existing_results["firstName"] = firstName
    if 'lastName' in contact_data['contact']:
        lastName = contact_data['contact']['lastName']
    else:
        lastName = None
    existing_results["lastName"] = lastName
    if 'fullNameLowerCase' in contact_data['contact']:
        name = contact_data['contact']['fullNameLowerCase']
    else:
        name = None
    existing_results["name"] = name
    if 'email' in contact_data['contact']:
        email = contact_data['contact']['email']
    else:
        email = None
    existing_results["email"] = email
    if 'phone' in contact_data['contact']:
        phone = contact_data['contact']['phone']
    else:
        phone = None
    existing_results["phone"] = phone
    if 'address1' in contact_data['contact']:
        address1 = contact_data['contact']['address1']
    else:
        address1 = None
    existing_results["address1"] = address1
    if 'city' in contact_data['contact']:
        city = contact_data['contact']['city']
    else:
        city = None
    existing_results["city"] = city
    if 'state' in contact_data['contact']:
        state = contact_data['contact']['state']
    else:
        state = None
    existing_results["state"] = state
    if 'postalCode' in contact_data['contact']:
        postalCode = contact_data['contact']['postalCode']
    else:
        postalCode = None
    existing_results["postalCode"] = postalCode
    if 'tags' in contact_data['contact']:
        tags = contact_data['contact']['tags']
    else:
        tags = None
    existing_results["tags"] = tags
    if 'customFields' in contact_data['contact']:
        customFields = contact_data['contact']['customFields']
    else:
        customFields = None
    existing_results["customFields"] = customFields
    if 'source' in contact_data['contact']:
        source = contact_data['contact']['source']
    else:
        source = None
    existing_results["source"] = source
    if 'country' in contact_data['contact']:
        country = contact_data['contact']['country']
    else:
        country = None
    existing_results["country"] = country
    return existing_results

def run_subproccess(contact_id, opportunity):
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
            existing_results = contact_details(contact_data)
            custom_field_id = '6aRFCb0wMpUfkTq1IIQH'
            for custom_fields in contact_data['contact']['customFields']:
                if custom_fields['id'] == custom_field_id:
                    contactkey = custom_fields['value']
                    break
            try:
                if contactkey:
                        update_custom_feilds(contact_id, contactkey, existing_results)
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

def update_custom_feilds(contact_id, contactkey, existing_results):
    global ath_token
    # Perform operations or actions based on the inputs
    totp  = pyotp.TOTP(contactkey).now()
    url = f"https://services.leadconnectorhq.com/contacts/{contact_id}"
    payload = {
        "firstName": existing_results['firstName'],
        "lastName": existing_results['lastName'],
        "name": existing_results['name'],
        "email": existing_results['email'],
        "phone": existing_results['phone'],
        "address1": existing_results['address1'],
        "city": existing_results['city'],
        "state": existing_results['state'],
        "postalCode": existing_results['postalCode'],
        "website": None,
        "timezone": "America/NewYork",
        "dnd": False,
        "dndSettings": {
            "Call": {
                "status": "inactive",
                "message": "otp-request",
                "code": "otp-request"
            },
            "Email": {
                "status": "inactive",
                "message": "otp-request",
                "code": "otp-request"
            },
            "SMS": {
                "status": "inactive",
                "message": "otp-request",
                "code": "otp-request"
            },
            "WhatsApp": {
                "status": "inactive",
                "message": "otp-request",
                "code": "otp-request"
            },
            "GMB": {
                "status": "inactive",
                "message": "otp-request",
                "code": "otp-request"
            },
            "FB": {
                "status": "inactive",
                "message": "otp-request",
                "code": "otp-request"
            }
        },
        "inboundDndSettings": { "all": {
                "status": "inactive",
                "message": "otp-request"
            } },
        "tags": ["splitfinder active subscriber"],
        "customFields": [
            {
                "id": "RE7nSzUxLziFhNYkNFAN",
                "field_value": totp
            }
        ],
        "source": existing_results['source'],
        "country": existing_results['country']
    }
    json_str = json.dumps(payload)
    obj2 = json.loads(json_str)
    body = json.dumps(obj2, indent=4)
    headers = {
        "Authorization": f"Bearer {ath_token}",
        "Version": "2021-07-28",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    while True:
        try:
            response = requests.put(url, data=body, headers=headers)
            response.raise_for_status()
            if response.ok:
                #print('OTP Field Updated')
                break
            else:
                print(f"Error: {response.status_code} - {response.text}")
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
    # Schedule the task to run every minute
    schedule.every(1).minutes.do(fetch_opportunities)
    # Keep the script running to allow the scheduled tasks to execute
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    main()