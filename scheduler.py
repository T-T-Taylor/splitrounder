import schedule
import time as tm
import subprocess
import sys
from datetime import datetime, timedelta
import datetime as dt
import pytz
from pandas_market_calendars import get_calendar
import requests

def find_previous_weekday(date):
    while date.weekday() >= 5:  # Monday to Friday (0 to 4)
        date -= timedelta(days=1)
    return date

def is_nyse_open(date):
    nyse = get_calendar("XNYS")
    return nyse.valid_days(start_date=date, end_date=date).size > 0

def remove_leading_zeros(num_str):
    return num_str.lstrip('0') or '0'

def find_ticker_by_cik_in_file(cik_to_find):
    # Function to find ticker from CIK
    def find_ticker_by_cik(cik, ticker_mapping):
        for ticker, cik_in_file in ticker_mapping.items():
            if cik_in_file == cik:
                return ticker
        return None
    # Read the ticker file from the URL
    headers = {
        'User-Agent': 'Split Rounder (Contact: split@splitrounder.com)',
        'Accept-Encoding': 'gzip, deflate',
        'Host': 'www.sec.gov'
    }
    ticker_file_url = "https://www.sec.gov/include/ticker.txt"
    response = requests.get(ticker_file_url, headers=headers)
    if response.status_code == 200:
        # Parse the file content and create a mapping between tickers and CIKs
        ticker_mapping = {}
        for line in response.text.split('\n'):
            if line.strip():
                ticker, cik = line.split('\t')
                ticker_mapping[ticker.lower()] = cik
        # Find the ticker associated with the given CIK
        found_ticker = find_ticker_by_cik(remove_leading_zeros(cik_to_find), ticker_mapping)
        if found_ticker:
            return found_ticker.upper()
        else:
            return f"No matching ticker found for CIK {cik_to_find}"
    else:
        return f"Failed to fetch ticker file. Status code: {response.status_code}"

def run_scheduled_script(target_date, company_code):
    script_path = '2.api.py'
    try:
        # Parse the target date provided as a command-line argument
        target_date_time_utc = datetime.strptime(target_date, "%Y-%m-%d")
    except ValueError:
        print("Invalid date format. Please use YYYY-MM-DD.")
        sys.exit(1)
    # Set the target time to 10:00 AM
    target_time = dt.datetime.strptime('10:00', '%H:%M').time()
    target_date_time_utc = datetime.combine(target_date_time_utc.date(), target_time)
    # Check if NYSE is open on the specified date
    while not is_nyse_open(target_date_time_utc):
        # If NYSE is closed, find the previous weekday
        target_date_time_utc = find_previous_weekday(target_date_time_utc)
        # If the previous weekday is in the past, reschedule for the next weekday
        if target_date_time_utc < datetime.utcnow():
            target_date_time_utc = target_date_time_utc.replace(hour=0, minute=0)
            target_date_time_utc += timedelta(days=1)
    # Convert the target date and time to the desired time zone
    target_date_time = target_date_time_utc.astimezone(pytz.timezone('America/New_York'))
    current_datetime = datetime.now(pytz.timezone('America/New_York'))
    current_date = datetime.now(pytz.timezone('America/New_York')).date()
    yesterday_date = datetime.now(pytz.timezone('America/New_York')).date() - timedelta(days=1)
    target_hour, target_minute = 16, 0 #4 PM
    closing_time = dt.time(target_hour, target_minute)
    if (
        target_date_time < current_datetime
        and target_date_time.date() == current_date
        and target_date_time.time() < closing_time  # 4:00 PM
    ):
        subprocess.Popen(['python', script_path, find_ticker_by_cik_in_file(company_code)])
        sys.exit()
    elif(
        target_date_time < current_datetime
        and target_date_time.date() == yesterday_date
        and target_date_time.time() < closing_time  # 4:00 PM
        and is_nyse_open(current_date)
    ):
        subprocess.Popen(['python', script_path, find_ticker_by_cik_in_file(company_code)])
        sys.exit()
    elif(target_date_time < current_datetime):
        print('Opportunity Missed')
    else:
        # Schedule the script to run at the specified date and time
        schedule.every().day.at(target_date_time.strftime('%H:%M:%S')).do(lambda: subprocess.Popen(['python', script_path, find_ticker_by_cik_in_file(company_code)]))
        print(f'{company_code} is scheduled to run at {target_date_time}')
        # Keep the scheduling script running
        while True:
            schedule.run_pending()
            current_datetime = datetime.now(pytz.timezone('America/New_York'))
            if current_datetime >= target_date_time:
                break
            tm.sleep(1)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python script.py <target_date> <company_code>")
        sys.exit(1)
    run_scheduled_script(sys.argv[1], sys.argv[2])
