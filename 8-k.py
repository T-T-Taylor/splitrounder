from sec_edgar_downloader import Downloader
import os
import re
from datetime import datetime, timedelta
import sys
import subprocess
from bs4 import BeautifulSoup
import platform
import shutil

def get_current_month():
    # Get the current date
    current_date = datetime.now()
    # Format the current month as a string
    current_month_str = current_date.strftime("%B")
    return current_month_str

def get_next_month():
    # Get the current date
    current_date = datetime.now()
    # Calculate the first day of the next month
    first_day_of_next_month = (current_date.replace(day=1) + timedelta(days=32)).replace(day=1)
    # Format the next month as a string
    next_month_str = first_day_of_next_month.strftime("%B")
    return next_month_str

def extract_date(file_path, search_phrase):
    backup_phrase = "Eastern Time on"
    try:
        with open(file_path, 'r', encoding='latin-1') as file:
            content = file.read()
            soup = BeautifulSoup(content, 'html.parser')
            # Search for the primary phrase
            primary_match = soup.find(string=re.compile(search_phrase))
            if primary_match:
                print(f"Found '{search_phrase}': {primary_match}")
                # Extract the date using a regular expression
                try:
                    match = re.search(r' (\w+\s\d{1,2},?\s\d{4})', str(primary_match))
                    if match:
                        return match.group(1)
                    else:
                        current_month = get_current_month()
                        secondary_search_phrase = f"{search_phrase} {current_month}"
                        secondary_match = soup.find(string=re.compile(secondary_search_phrase))
                        match = re.search(r' (\w+\s\d{1,2},?\s\d{4})', str(secondary_match))
                        if match:
                            return match.group(1)
                        else:
                            next_month = get_next_month()
                            third_search_phrase = f"{search_phrase} {next_month}"
                            third_match = soup.find(string=re.compile(third_search_phrase))
                            match = re.search(r' (\w+\s\d{1,2},?\s\d{4})', str(third_match))
                            if match:
                                return match.group(1)
                except Exception as e:
                    print (f"{e}")
            # If the primary search phrase is not found, try the backup phrase
            backup_match = soup.find(string=re.compile(backup_phrase))
            if backup_match:
                print(f"Found Backup '{backup_phrase}': {backup_match}")
                # Extract the date using a regular expression
                match = re.search(r' (\w+\s\d{1,2},?\s\d{4})', str(backup_match))
                if match:
                    return match.group(1)
                else:
                    current_month = get_current_month()
                    secondary_search_phrase = f"{backup_phrase} {current_month}"
                    secondary_match = soup.find(string=re.compile(secondary_search_phrase))
                    match = re.search(r' (\w+\s\d{1,2},?\s\d{4})', str(secondary_match))
                    if match:
                        return match.group(1)
                    else:
                        next_month = get_next_month()
                        third_search_phrase = f"{backup_phrase} {next_month}"
                        third_match = soup.find(string=re.compile(third_search_phrase))
                        match = re.search(r' (\w+\s\d{1,2},?\s\d{4})', str(third_match))
                        if match:
                            return match.group(1)
            # If both search phrases are not found, return None or raise an exception as needed
            return None
    except FileNotFoundError:
        print(f"File '{file_path}' not found.")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def find_first_preceding_weekday(input_date):
    weekday_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    weekday_number = input_date.weekday()
    for i in range(1, 8):
        delta = timedelta(days=i)
        preceding_date = input_date - delta
        if preceding_date.weekday() < 5:
            return preceding_date, weekday_names[preceding_date.weekday()]

def add_to_scedule (companycode, preceding_weekday):
    export_date = preceding_weekday.strftime("%Y-%m-%d")
    subprocess.run(['python', 'scheduler.py', export_date, companycode], check=True)

def delete_folders(companycode, file_path, current_directory):
    folder_path_win = f"{current_directory}\sec-edgar-filings\{companycode}"
    folder_path_lin = f"{current_directory}/sec-edgar-filings/{companycode}"
    system = platform.system()
    if system == 'Windows':
        folder_path = folder_path_win
    elif system == 'Linux':
        folder_path = folder_path_lin
    else:
        print('Unsupported OS')
    if folder_path:
        search_text = "split"
        try:
            with open(file_path, 'r') as file:
                line_number = 0
                found = False
                for line in file:
                    line_number += 1
                    if search_text in line:
                        found = True
                        return(True)
        except FileNotFoundError:
            print(f"File '{file_path}' not found.")
        except Exception as e:
            print(f"An error occurred: {e}")
        try:
            shutil.rmtree(folder_path)
        except OSError as e:
            print(f"Error: {e}")

def not_in_otc_marketplace(file_path):
    search_text = "OTC Marketplace"
    try:
        with open(file_path, 'r') as file:
            line_number = 0
            found = False
            for line in file:
                line_number += 1
                if search_text in line:
                    found = True
                    return(False)
            if not found:
                return(True)
    except FileNotFoundError:
        print(f"File '{file_path}' not found.")
        sys.exit()
    except Exception as e:
        print(f"An error occurred: {e}")

def entitled_to_receive_a_whole_share(file_path, companycode):
    search_text = "entitled to receive a whole share"
    try:
        with open(file_path, 'r') as file:
            line_number = 0
            found = False
            for line in file:
                line_number += 1
                if search_text in line:
                    found = True
                    search_phrase = "Eastern Time on"
                    result = extract_date(file_path, search_phrase)
                    if result:
                        try:
                            date = datetime.strptime(result, "%B %d, %Y")
                        except ValueError as e:
                            print(f"Error: {e}")
                        preceding_weekday_info = find_first_preceding_weekday(date)
                        if preceding_weekday_info is not None:
                            preceding_weekday, weekday_name = preceding_weekday_info
                            formatted_preceding_weekday = preceding_weekday.strftime("%Y-%m-%dT%H:%M:%S%z")
                            add_to_scedule(companycode, preceding_weekday)
                            return True
                        else:
                            print("No preceding weekday found.")
            if not found:
                return False
    except FileNotFoundError:
        print(f"File '{file_path}' not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

def will_be_rounded_up_to_the_nearest_whole_share(file_path, companycode):
    search_text = "will be rounded up to the nearest whole share"
    try:
        with open(file_path, 'r') as file:
            line_number = 0  # To keep track of the line number
            found = False  # To check if the text is found
            for line in file:
                line_number += 1
                if search_text in line:
                    found = True
                    search_phrase = "Stock Split on"
                    result = extract_date(file_path, search_phrase)
                    if result:
                        try:
                            date = datetime.strptime(result, "%B %d, %Y")
                        except ValueError as e:
                            print(f"Error: {e}")
                        preceding_weekday_info = find_first_preceding_weekday(date)
                        if preceding_weekday_info is not None:
                            preceding_weekday, weekday_name = preceding_weekday_info
                            formatted_preceding_weekday = preceding_weekday.strftime("%Y-%m-%dT%H:%M:%S%z")
                            add_to_scedule (companycode, preceding_weekday)
                            return(True)
                        else:
                            print("No preceding weekday found.")
            if not found:
                return(False)
    except FileNotFoundError:
        print(f"File '{file_path}' not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

def entitled_to_the_rounding_up_of_the_fractional_share(file_path, companycode):
    search_text = "entitled to the rounding up of the fractional share"
    try:
        with open(file_path, 'r') as file:
            line_number = 0
            found = False
            for line in file:
                line_number += 1
                if search_text in line:
                    found = True
                    search_phrase = "ET on"
                    result = extract_date(file_path, search_phrase)
                    if result:
                        try:
                            date = datetime.strptime(result, "%B %d, %Y")
                        except ValueError as e:
                            print(f"Error: {e}")
                        preceding_weekday_info = find_first_preceding_weekday(date)
                        if preceding_weekday_info is not None:
                            preceding_weekday, weekday_name = preceding_weekday_info
                            formatted_preceding_weekday = preceding_weekday.strftime("%Y-%m-%dT%H:%M:%S%z")
                            add_to_scedule (companycode, preceding_weekday)
                            return(True)
                        else:
                            print("No preceding weekday found.")
            if not found:
                return(False)
    except FileNotFoundError:
        print(f"File '{file_path}' not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

def whole_share_in_lieu_of_the_issuance_of_any_fractional_share(file_path, companycode):
    search_text = "whole share in lieu of the issuance of any fractional share"
    try:
        with open(file_path, 'r') as file:
            line_number = 0
            found = False
            for line in file:
                line_number += 1
                if search_text in line:
                    found = True
                    search_phrase = "On"
                    result = extract_date(file_path, search_phrase)
                    if result:
                        try:
                            date = datetime.strptime(result, "%B %d, %Y")
                        except ValueError as e:
                            print(f"Error: {e}")
                        preceding_weekday_info = find_first_preceding_weekday(date)
                        if preceding_weekday_info is not None:
                            preceding_weekday, weekday_name = preceding_weekday_info
                            formatted_preceding_weekday = preceding_weekday.strftime("%Y-%m-%dT%H:%M:%S%z")
                            add_to_scedule (companycode, preceding_weekday)
                            return(True)
                        else:
                            print("No preceding weekday found.")
            if not found:
                return(False)
    except FileNotFoundError:
        print(f"File '{file_path}' not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

def a_full_share_in_lieu_of_such_fractional_share(file_path, companycode):
    search_text = "a full share in lieu"
    try:
        with open(file_path, 'r') as file:
            line_number = 0
            found = False
            for line in file:
                line_number += 1
                if search_text in line:
                    found = True
                    search_phrase = "Eastern Time, on"
                    result = extract_date(file_path, search_phrase)
                    if result:
                        try:
                            date = datetime.strptime(result, "%B %d, %Y")
                        except ValueError as e:
                            print(f"Error: {e}")
                        preceding_weekday_info = find_first_preceding_weekday(date)
                        if preceding_weekday_info is not None:
                            preceding_weekday, weekday_name = preceding_weekday_info
                            formatted_preceding_weekday = preceding_weekday.strftime("%Y-%m-%dT%H:%M:%S%z")
                            add_to_scedule (companycode, preceding_weekday)
                            return(True)
                        else:
                            print("No preceding weekday found.")
            if not found:
                return(False)
    except FileNotFoundError:
        print(f"File '{file_path}' not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

def one_whole_share(file_path, companycode):
    search_text = "one whole share of Common Stock in lieu of such fractional share"
    try:
        with open(file_path, 'r') as file:
            line_number = 0
            found = False
            for line in file:
                line_number += 1
                if search_text in line:
                    found = True
                    search_phrase = "split-adjusted basis on"
                    result = extract_date(file_path, search_phrase)
                    if result:
                        try:
                            date = datetime.strptime(result, "%B %d, %Y")
                        except ValueError as e:
                            print(f"Error: {e}")
                        preceding_weekday_info = find_first_preceding_weekday(date)
                        if preceding_weekday_info is not None:
                            preceding_weekday, weekday_name = preceding_weekday_info
                            formatted_preceding_weekday = preceding_weekday.strftime("%Y-%m-%dT%H:%M:%S%z")
                            add_to_scedule (companycode, preceding_weekday)
                            return(True)
                        else:
                            print("No preceding weekday found.")
            if not found:
                return(False)
    except FileNotFoundError:
        print(f"File '{file_path}' not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

def post_Reverse_Stock_Split_common_stock(file_path, companycode):
    search_text = "one whole share of the post-Reverse Stock Split common stock to any shareholder who otherwise would have received a fractional share"
    try:
        with open(file_path, 'r') as file:
            line_number = 0
            found = False
            for line in file:
                line_number += 1
                if search_text in line:
                    found = True
                    search_phrase = "open of business on"
                    result = extract_date(file_path, search_phrase)
                    if result:
                        try:
                            date = datetime.strptime(result, "%B %d, %Y")
                        except ValueError as e:
                            print(f"Error: {e}")
                        preceding_weekday_info = find_first_preceding_weekday(date)
                        if preceding_weekday_info is not None:
                            preceding_weekday, weekday_name = preceding_weekday_info
                            formatted_preceding_weekday = preceding_weekday.strftime("%Y-%m-%dT%H:%M:%S%z")
                            add_to_scedule (companycode, preceding_weekday)
                            return(True)
                        else:
                            print("No preceding weekday found.")
            if not found:
                return(False)
    except FileNotFoundError:
        print(f"File '{file_path}' not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

def rounded_up_to_the_next_higher_whole_share(file_path, companycode):
    search_text = "rounded up to the next higher whole share"
    try:
        with open(file_path, 'r') as file:
            line_number = 0
            found = False
            for line in file:
                line_number += 1
                if search_text in line:
                    found = True
                    search_phrase = "will become effective on"
                    result = extract_date(file_path, search_phrase)
                    if result:
                        try:
                            date = datetime.strptime(result, "%B %d, %Y")
                        except ValueError as e:
                            print(f"Error: {e}")
                        preceding_weekday_info = find_first_preceding_weekday(date)
                        if preceding_weekday_info is not None:
                            preceding_weekday, weekday_name = preceding_weekday_info
                            formatted_preceding_weekday = preceding_weekday.strftime("%Y-%m-%dT%H:%M:%S%z")
                            add_to_scedule (companycode, preceding_weekday)
                            return(True)
                        else:
                            print("No preceding weekday found.")
            if not found:
                return(False)
    except FileNotFoundError:
        print(f"File '{file_path}' not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

def will_issue_one_additional_whole_share_of_the_post_reverse_split(file_path, companycode):
    search_text = "will issue one additional whole share of the post-Reverse Split"
    try:
        with open(file_path, 'r') as file:
            line_number = 0
            found = False
            for line in file:
                line_number += 1
                if search_text in line:
                    found = True
                    search_phrase = "Eastern Standard Time on"
                    result = extract_date(file_path, search_phrase)
                    if result:
                        try:
                            date = datetime.strptime(result, "%B %d, %Y")
                        except ValueError as e:
                            print(f"Error: {e}")
                        preceding_weekday_info = find_first_preceding_weekday(date)
                        if preceding_weekday_info is not None:
                            preceding_weekday, weekday_name = preceding_weekday_info
                            formatted_preceding_weekday = preceding_weekday.strftime("%Y-%m-%dT%H:%M:%S%z")
                            add_to_scedule (companycode, preceding_weekday)
                            return(True)
                        else:
                            print("No preceding weekday found.")
            if not found:
                return(False)
    except FileNotFoundError:
        print(f"File '{file_path}' not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

def rounded_up_to_the_nearest_whole_share_of_common_stock(file_path, companycode):
    search_text = "rounded up to the nearest whole share of Common Stock"
    try:
        with open(file_path, 'r') as file:
            line_number = 0
            found = False
            for line in file:
                line_number += 1
                if search_text in line:
                    found = True
                    search_phrase = "Eastern Standard Time on"
                    result = extract_date(file_path, search_phrase)
                    if result:
                        try:
                            date = datetime.strptime(result, "%B %d, %Y")
                        except ValueError as e:
                            print(f"Error: {e}")
                        preceding_weekday_info = find_first_preceding_weekday(date)
                        if preceding_weekday_info is not None:
                            preceding_weekday, weekday_name = preceding_weekday_info
                            formatted_preceding_weekday = preceding_weekday.strftime("%Y-%m-%dT%H:%M:%S%z")
                            add_to_scedule (companycode, preceding_weekday)
                            return(True)
                        else:
                            print("No preceding weekday found.")
            if not found:
                return(False)
    except FileNotFoundError:
        print(f"File '{file_path}' not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

def shall_be_rounded_up_to_the_next_higher_whole_share(file_path, companycode):
    search_text = "shall be rounded up to the next higher whole share"
    try:
        with open(file_path, 'r') as file:
            line_number = 0
            found = False
            for line in file:
                line_number += 1
                if search_text in line:
                    found = True
                    search_phrase = "Split-adjusted basis on"
                    result = extract_date(file_path, search_phrase)
                    if result:
                        try:
                            date = datetime.strptime(result, "%B %d, %Y")
                        except ValueError as e:
                            print(f"Error: {e}")
                        preceding_weekday_info = find_first_preceding_weekday(date)
                        if preceding_weekday_info is not None:
                            preceding_weekday, weekday_name = preceding_weekday_info
                            formatted_preceding_weekday = preceding_weekday.strftime("%Y-%m-%dT%H:%M:%S%z")
                            add_to_scedule (companycode, preceding_weekday)
                            return(True)
                        else:
                            print("No preceding weekday found.")
            if not found:
                return(False)
    except FileNotFoundError:
        print(f"File '{file_path}' not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

def rounded_up_to_the_next_whole_number(file_path, companycode):
    search_text = "rounded up to the next whole number"
    try:
        with open(file_path, 'r') as file:
            line_number = 0
            found = False
            for line in file:
                line_number += 1
                if search_text in line:
                    found = True
                    search_phrase = "effective as of 9:30 a.m. (Eastern Time) on"
                    result = extract_date(file_path, search_phrase)
                    if result:
                        try:
                            date = datetime.strptime(result, "%B %d, %Y")
                        except ValueError as e:
                            print(f"Error: {e}")
                        preceding_weekday_info = find_first_preceding_weekday(date)
                        if preceding_weekday_info is not None:
                            preceding_weekday, weekday_name = preceding_weekday_info
                            formatted_preceding_weekday = preceding_weekday.strftime("%Y-%m-%dT%H:%M:%S%z")
                            add_to_scedule (companycode, preceding_weekday)
                            return(True)
                        else:
                            print("No preceding weekday found.")
            if not found:
                return(False)
    except FileNotFoundError:
        print(f"File '{file_path}' not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

def fractional_shares_rounded_up_to_the_next_whole_share(file_path, companycode):
    search_text = "fractional shares rounded up to the next whole share"
    try:
        with open(file_path, 'r') as file:
            line_number = 0
            found = False
            for line in file:
                line_number += 1
                if search_text in line:
                    found = True
                    search_phrase = "Eastern Time on"
                    result = extract_date(file_path, search_phrase)
                    if result:
                        try:
                            date = datetime.strptime(result, "%B %d, %Y")
                        except ValueError as e:
                            print(f"Error: {e}")
                        preceding_weekday_info = find_first_preceding_weekday(date)
                        if preceding_weekday_info is not None:
                            preceding_weekday, weekday_name = preceding_weekday_info
                            formatted_preceding_weekday = preceding_weekday.strftime("%Y-%m-%dT%H:%M:%S%z")
                            add_to_scedule (companycode, preceding_weekday)
                            return(True)
                        else:
                            print("No preceding weekday found.")
            if not found:
                return(False)
    except FileNotFoundError:
        print(f"File '{file_path}' not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

def rounded_up_to_the_nearest_whole_share(file_path, companycode):
    search_text = "rounded up to the nearest whole share"
    try:
        with open(file_path, 'r') as file:
            line_number = 0
            found = False
            for line in file:
                line_number += 1
                if search_text in line:
                    found = True
                    search_phrase = "Eastern Time on"
                    result = extract_date(file_path, search_phrase)
                    if result:
                        try:
                            date = datetime.strptime(result, "%B %d, %Y")
                        except ValueError as e:
                            print(f"Error: {e}")
                        preceding_weekday_info = find_first_preceding_weekday(date)
                        if preceding_weekday_info is not None:
                            preceding_weekday, weekday_name = preceding_weekday_info
                            formatted_preceding_weekday = preceding_weekday.strftime("%Y-%m-%dT%H:%M:%S%z")
                            add_to_scedule (companycode, preceding_weekday)
                            return(True)
                        else:
                            print("No preceding weekday found.")
            if not found:
                return(False)
    except FileNotFoundError:
        print(f"File '{file_path}' not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

def have_their_fractional_interest_rounded_up_to_the_next_whole_share(file_path, companycode):
    search_text = "rounded up to the next whole share"
    try:
        with open(file_path, 'r') as file:
            line_number = 0
            found = False
            for line in file:
                line_number += 1
                if search_text in line:
                    found = True
                    search_phrase = "Eastern Time on"
                    result = extract_date(file_path, search_phrase)
                    if result:
                        try:
                            date = datetime.strptime(result, "%B %d, %Y")
                        except ValueError as e:
                            print(f"Error: {e}")
                        preceding_weekday_info = find_first_preceding_weekday(date)
                        if preceding_weekday_info is not None:
                            preceding_weekday, weekday_name = preceding_weekday_info
                            formatted_preceding_weekday = preceding_weekday.strftime("%Y-%m-%dT%H:%M:%S%z")
                            add_to_scedule (companycode, preceding_weekday)
                            return(True)
                        else:
                            print("No preceding weekday found.")
            if not found:
                return(False)
    except FileNotFoundError:
        print(f"File '{file_path}' not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

def round_up_to_the_next_whole_post_Reverse_Stock(file_path, companycode):
    search_text = "round up to the next whole post-Reverse Stock"
    try:
        with open(file_path, 'r') as file:
            line_number = 0
            found = False
            for line in file:
                line_number += 1
                if search_text in line:
                    found = True
                    search_phrase = "On"
                    result = extract_date(file_path, search_phrase)
                    if result:
                        try:
                            date = datetime.strptime(result, "%B %d, %Y")
                        except ValueError as e:
                            print(f"Error: {e}")
                        preceding_weekday_info = find_first_preceding_weekday(date)
                        if preceding_weekday_info is not None:
                            preceding_weekday, weekday_name = preceding_weekday_info
                            formatted_preceding_weekday = preceding_weekday.strftime("%Y-%m-%dT%H:%M:%S%z")
                            add_to_scedule (companycode, preceding_weekday)
                            return(True)
                        else:
                            print("No preceding weekday found.")
            if not found:
                return(False)
    except FileNotFoundError:
        print(f"File '{file_path}' not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

def rounded_up_to_the_next_whole_number(file_path, companycode):
    search_text = "rounded up to the next whole number"
    try:
        with open(file_path, 'r') as file:
            line_number = 0
            found = False
            for line in file:
                line_number += 1
                if search_text in line:
                    found = True
                    search_phrase = "(Eastern Time) on"
                    result = extract_date(file_path, search_phrase)
                    if result:
                        try:
                            date = datetime.strptime(result, "%B %d, %Y")
                        except ValueError as e:
                            print(f"Error: {e}")
                        preceding_weekday_info = find_first_preceding_weekday(date)
                        if preceding_weekday_info is not None:
                            preceding_weekday, weekday_name = preceding_weekday_info
                            formatted_preceding_weekday = preceding_weekday.strftime("%Y-%m-%dT%H:%M:%S%z")
                            add_to_scedule (companycode, preceding_weekday)
                            return(True)
                        else:
                            print("No preceding weekday found.")
            if not found:
                return(False)
    except FileNotFoundError:
        print(f"File '{file_path}' not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

def one_full_share_of_Common_Stock_will_be_issued(file_path, companycode):
    search_text = "one full share of Common Stock will be issued"
    try:
        with open(file_path, 'r') as file:
            line_number = 0
            found = False
            for line in file:
                line_number += 1
                if search_text in line:
                    found = True
                    search_phrase = "markets open on"
                    result = extract_date(file_path, search_phrase)
                    if result:
                        try:
                            date = datetime.strptime(result, "%B %d, %Y")
                        except ValueError as e:
                            print(f"Error: {e}")
                        preceding_weekday_info = find_first_preceding_weekday(date)
                        if preceding_weekday_info is not None:
                            preceding_weekday, weekday_name = preceding_weekday_info
                            formatted_preceding_weekday = preceding_weekday.strftime("%Y-%m-%dT%H:%M:%S%z")
                            add_to_scedule (companycode, preceding_weekday)
                            return(True)
                        else:
                            print("No preceding weekday found.")
            if not found:
                return(False)
    except FileNotFoundError:
        print(f"File '{file_path}' not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

def rounded_up_to_the_nearest_whole_share(file_path, companycode):
    search_text = "rounded up to the nearest whole share"
    try:
        with open(file_path, 'r') as file:
            line_number = 0
            found = False
            for line in file:
                line_number += 1
                if search_text in line:
                    found = True
                    search_phrase = "per share on"
                    result = extract_date(file_path, search_phrase)
                    if result:
                        try:
                            date = datetime.strptime(result, "%B %d, %Y")
                        except ValueError as e:
                            print(f"Error: {e}")
                        preceding_weekday_info = find_first_preceding_weekday(date)
                        if preceding_weekday_info is not None:
                            preceding_weekday, weekday_name = preceding_weekday_info
                            formatted_preceding_weekday = preceding_weekday.strftime("%Y-%m-%dT%H:%M:%S%z")
                            add_to_scedule (companycode, preceding_weekday)
                            return(True)
                        else:
                            print("No preceding weekday found.")
            if not found:
                return(False)
    except FileNotFoundError:
        print(f"File '{file_path}' not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

def main():
    if len(sys.argv) != 3:
        print("Usage: python script.py <companycode> <file_code>")
        sys.exit(1)
    # Get command-line arguments and assign them to variables
    companycode = sys.argv[1]
    file_code =sys.argv[2]
    current_directory = os.getcwd()
    dl = Downloader("Split Rounder", "split@splitrounder.com", current_directory)
    dl.get("8-K", companycode, limit=1)
    file_path_win = f"{current_directory}\sec-edgar-filings\{companycode}\\8-K\\{file_code}\\full-submission.txt"
    file_path_lin = f"{current_directory}/sec-edgar-filings/{companycode}/8-K/{file_code}/full-submission.txt"
    system = platform.system()
    if system == 'Windows':
        file_path = file_path_win
    elif system == 'Linux':
        file_path = file_path_lin
    else:
        print('Unsupported OS')
    if not_in_otc_marketplace(file_path):
        while True:
            if entitled_to_receive_a_whole_share(file_path, companycode):
                break
            if will_be_rounded_up_to_the_nearest_whole_share(file_path, companycode):
                break
            if entitled_to_the_rounding_up_of_the_fractional_share(file_path, companycode):
                break
            if whole_share_in_lieu_of_the_issuance_of_any_fractional_share(file_path, companycode):
                break
            if a_full_share_in_lieu_of_such_fractional_share(file_path, companycode):
                break
            if one_whole_share(file_path, companycode):
                break
            if post_Reverse_Stock_Split_common_stock(file_path, companycode):
                break
            if rounded_up_to_the_next_higher_whole_share(file_path, companycode):
                break
            if will_issue_one_additional_whole_share_of_the_post_reverse_split(file_path, companycode):
                break
            if rounded_up_to_the_nearest_whole_share_of_common_stock(file_path, companycode):
                break
            if shall_be_rounded_up_to_the_next_higher_whole_share(file_path, companycode):
                break
            if fractional_shares_rounded_up_to_the_next_whole_share(file_path, companycode):
                break
            if rounded_up_to_the_nearest_whole_share(file_path, companycode):
                break
            if have_their_fractional_interest_rounded_up_to_the_next_whole_share(file_path, companycode):
                break
            if round_up_to_the_next_whole_post_Reverse_Stock(file_path, companycode):
                break
            if rounded_up_to_the_next_whole_number(file_path, companycode):
                break
            if one_full_share_of_Common_Stock_will_be_issued(file_path, companycode):
                break
            if rounded_up_to_the_nearest_whole_share(file_path, companycode):
                beak
            else:
                break
    else:
        print("Ignore: Part of the OTC Marketplace")
    delete_folders(companycode, file_path, current_directory)

if __name__ == "__main__":
    main()
