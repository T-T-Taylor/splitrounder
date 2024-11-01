import pyotp
import robin_stocks.robinhood as r
import sys
import time
import requests
import json
from requests.exceptions import ConnectionError, RequestException

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

def error(error_message, contactid, contact_data):
    global ath_token
    existing_results = contact_details(contact_data)
    url = f"https://services.leadconnectorhq.com/contacts/{contactid}"
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
                "id": "M36mfogDKMQoVOphRcdm",
                "field_value": error_message
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
            response = requests.put(url, data=payload, headers=headers)
            response.raise_for_status()
            if response.ok:
                if "Unable to log in with provided credentials." in error_message:
                    #print("Error: Unable to log in. Please check your email, password, and MFA code.")
                    break
                else:
                    print(f"Error: {error_message}")
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

def main():
    refresh()
    global ath_token
    # Check if three command-line arguments are provided
    if len(sys.argv) != 5:
        #print("Usage: python script.py <email> <password> <code> <contactid> <contact_data>")
        sys.exit(1)
    # Get command-line arguments and assign them to variables
    email = sys.argv[1]
    password = sys.argv[2]
    code = sys.argv[3]
    contactid = sys.argv[4]
    # Perform operations or actions based on the inputs
    url = f"https://services.leadconnectorhq.com/contacts/{contactid}"
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
    existing_results = contact_details(contact_data)
    totp  = pyotp.TOTP(code).now()
    try:
        login = r.login(email, password, mfa_code=totp, pickle_name = contactid)
        url = f"https://services.leadconnectorhq.com/contacts/{contactid}"
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
                    "id": "M36mfogDKMQoVOphRcdm",
                    "field_value": "Confirmed"
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
                    #print('Account Connection Confirmed')
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
    except Exception as e:
        error_message = str(e)
        error(error_message, contactid, contact_data)

if __name__ == "__main__":
    main()
