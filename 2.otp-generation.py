import requests
import schedule
import time
from datetime import datetime, timedelta
import pyotp
import json
from requests.exceptions import ConnectionError, RequestException
import subprocess

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

# Initialize a set to store the IDs of previously fetched submissions
previous_submission_ids = set()
refresh()

def fetch_submissions():
    global ath_token
    global previous_submission_ids
    script_path = 'getaccesstoken.py'
    current_date = datetime.now().strftime('%Y-%m-%d')
    url = "https://services.leadconnectorhq.com/forms/submissions"
    querystring = {"locationId":"slyxLRE59hLFpE9hWKna","limit":"20","formId":"cLRKzsE0wj9pt3gaZNIm","startAt":current_date}
    headers = {
        "Authorization": f"Bearer {ath_token}",
        "Version": "2021-07-28",
        "Accept": "application/json"
    }
    try:
        response = requests.get(url, headers=headers, params=querystring)
        response.raise_for_status()
        if response.status_code == 200:
            data = response.json()
            new_submissions = [submission for submission in data['submissions'] if submission['id'] not in previous_submission_ids]
            # Identify new submissions by comparing with previous submissions
            new_submission_ids = set(submission['id'] for submission in new_submissions)
            if new_submission_ids:
                #print(f"New submissions: {new_submission_ids}")
                # Perform action for each new submission
                for submission in new_submissions:
                    #print("Action: Attempt to connect to RH Account")
                    due_date = (datetime.now() + timedelta(days=1)).replace(hour=11, minute=0, second=0, microsecond=0)
                    formatted_due_date = due_date.strftime('%Y-%m-%dT%H:%M:%SZ')
                    key = submission.get('6aRFCb0wMpUfkTq1IIQH', '')
                    contactid = submission.get('contactId', '')
                    try:
                        totp = pyotp.TOTP(key).now()
                    except binascii.Error as e:
                        # Handling the specific error message
                        if str(e) == 'Non-base32 digit found':
                            # Handle the error gracefully
                            print("Error: Non-base32 digit found in the key.")
                        else:
                            # Handle other binascii errors or log them
                            print("Error:", e)
                    urlapi = f"https://services.leadconnectorhq.com/contacts/{contactid}/tasks"
                    payload = {
                        "title": "RH OTP Deliverability",
                        "body": totp,
                        "dueDate": formatted_due_date,
                        "completed": True,
                        "assignedTo": "ynSyUaOk3XULAjS2u6Ek"
                    }
                    headers = {
                        "Authorization": f"Bearer {ath_token}",
                        "Version": "2021-07-28",
                        "Content-Type": "application/json",
                        "Accept": "application/json"
                    }
                    while True:
                        try:
                            response = requests.post(urlapi, json=payload, headers=headers)
                            response.raise_for_status()
                            if response.ok:
                                task_data = response.json()
                                break
                                #print(f"Task created successfully. Task ID: {task_data['id']}")
                            else:
                                print(f"Error: {response.status_code} - {response.text}")
                                break
                        except ConnectionError:
                            print("Error: Unable to establish a connection. Please check your internet connection.")
                            time.sleep(300)
                        except requests.exceptions.HTTPError as e:
                            if e.response.status_code == 403:
                                print(f"Lost: {submission}")
                                break
                            else:
                                print(f"An HTTP error occured: {e}")
                                print(f"Lost: {submission}")
                                break
                        except RequestException as e:
                            print(f"Error: {e}")
                            print(f"Lost: {submission}")
                            break
            # Update the set of previous submission IDs
            previous_submission_ids.update(new_submission_ids)
        else:
            print(f"Error: {response.status_code} - {response.text}")
    except ConnectionError:
        print("Error: Unable to establish a connection. Please check your internet connection.")
    except requests.exceptions.HTTPError as e:
        subprocess.Popen(['python3', script_path])
    except RequestException as e:
        print(f"Error: {e}")

# Schedule the task to run every minute
schedule.every(1).minutes.do(fetch_submissions)

# Keep the script running to allow the scheduled tasks to execute
while True:
    schedule.run_pending()
    refresh()
    time.sleep(1)
