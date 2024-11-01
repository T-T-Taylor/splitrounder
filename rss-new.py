import feedparser
import requests
from bs4 import BeautifulSoup
import schedule
import time
from datetime import datetime, timedelta
import subprocess
import re
from requests.exceptions import ConnectionError, RequestException

# Initialize a set to store processed links
processed_links = set()

def fetch_rss_feed():
    global processed_links
    headers = {
        'User-Agent': 'Spilt_Rounder (Contact: split@splitrounder.com)',
        'Accept-Encoding': 'gzip, deflate',
        'Host': 'www.sec.gov'
    }
    rss_url = "https://www.sec.gov/cgi-bin/browse-edgar?action=getcurrent&CIK=&type=8-k&company=&dateb=&owner=include&start=0&count=100&output=atom"
    # Fetch the RSS feed using the 'requests' library and set the custom headers
    try:
        response = requests.get(rss_url, headers=headers)
        response.raise_for_status()
        # Check if the response is empty or invalid
        if response.status_code != 200:
            print("Failed to fetch the RSS feed. Status code:", response.status_code)
        else:
            feed_content = response.text
            rss_feed = feedparser.parse(feed_content)
            # Check if the response contains entries
            if not rss_feed.entries:
                return
            search_phrases = [
                "Item 5.03: Amendments to Articles of Incorporation or Bylaws; Change in Fiscal Year"
            ]
            for entry in rss_feed.entries:
                link = entry.link
                # Check if the link has been processed
                if link not in processed_links:
                    summary = entry.summary
                    soup = BeautifulSoup(summary, "html.parser")
                    summary_text = soup.get_text()
                    all_found = True
                    for phrase in search_phrases:
                        if phrase not in summary_text:
                            all_found = False
                            break
                    if all_found:
                        match = re.search(r'\((\d+)\)', entry.title)
                        if match:
                            extracted_value = match.group(1)
                            match = re.search(r'(\d{10}-\d{2}-\d{6})', link)
                            if match:
                                file_code = match.group(1)
                                subprocess.run(['python', '8-k.py', extracted_value, file_code], check=True)
                            else:
                                print("No match found.")
                        else:
                            print("No match found.")
                        # Add the link to the set of processed links
                        processed_links.add(link)
    except ConnectionError:
        print("Error: Unable to establish a connection. Please check your internet connection.")
    except RequestException as e:
        print(f"Error: {e}")

def fetch_rss_feed_var2():
    global processed_links
    headers = {
        'User-Agent': 'Spilt_Rounder (Contact: split@splitrounder.com)',
        'Accept-Encoding': 'gzip, deflate',
        'Host': 'www.sec.gov'
    }
    rss_url = "https://www.sec.gov/cgi-bin/browse-edgar?action=getcurrent&CIK=&type=8-k&company=&dateb=&owner=include&start=0&count=100&output=atom"
    # Fetch the RSS feed using the 'requests' library and set the custom headers
    try:
        response = requests.get(rss_url, headers=headers)
        response.raise_for_status()
        # Check if the response is empty or invalid
        if response.status_code != 200:
            print("Failed to fetch the RSS feed. Status code:", response.status_code)
        else:
            feed_content = response.text
            rss_feed = feedparser.parse(feed_content)
            # Check if the response contains entries
            if not rss_feed.entries:
                return
            search_phrases = [
                "Item 8.01: Other Events"
            ]
            for entry in rss_feed.entries:
                link = entry.link
                # Check if the link has been processed
                if link not in processed_links:
                    summary = entry.summary
                    soup = BeautifulSoup(summary, "html.parser")
                    summary_text = soup.get_text()
                    all_found = True
                    for phrase in search_phrases:
                        if phrase not in summary_text:
                            all_found = False
                            break
                    if all_found:
                        match = re.search(r'\((\d+)\)', entry.title)
                        if match:
                            extracted_value = match.group(1)
                            match = re.search(r'(\d{10}-\d{2}-\d{6})', link)
                            if match:
                                file_code = match.group(1)
                                subprocess.run(['python', '8-k.py', extracted_value, file_code], check=True)
                            else:
                                print("No match found.")
                        else:
                            print("No match found.")
                        # Add the link to the set of processed links
                        processed_links.add(link)
    except ConnectionError:
        print("Error: Unable to establish a connection. Please check your internet connection.")
    except RequestException as e:
        print(f"Error: {e}")

# Schedule the task to run every minute
schedule.every(1).minutes.do(fetch_rss_feed)
schedule.every(1).minutes.do(fetch_rss_feed_var2)

# Keep the script running to allow the scheduled tasks to execute
while True:
    schedule.run_pending()
    time.sleep(1)
