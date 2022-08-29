import datetime
import json
from bs4 import BeautifulSoup
import requests
from dataclasses import dataclass
from config import api_key


@dataclass
class Holiday:
    name: str
    date: datetime
    
    def __str__(self):
        return f"{self.name} ({self.date.__str__()})"

    def __gt__(self, other):
        return self.date > other.date
    
    def __ge__(self, other):
        return self.date >= other.date

    def __eq__(self, other):
        return self.date == other.date


class Holiday_List:
    def __init__(self):
       self.inner_holidays = []
   
    def add_holiday(self, holiday_inst):
        # Make sure holiday_inst is an Holiday object by checking the type
        if type(holiday_inst) == Holiday:
            # Use inner_holidays.append(holidayObj) to add holiday
            self.inner_holidays.append(holiday_inst)
            # print to the user that you added a holiday
            print(f"{holiday_inst} has been added to the list.\n")
        else:
            print(f"Invalid parameter, {holiday_inst} is not a Holiday object.\n")

    def json_read(self, file_location):
        # Read in things from json file location
        with open(file_location, "r") as json_file:
            read = json.load(json_file)
        hol_list = read['holidays']
        for hol in hol_list:
            hol_name = hol['name']
            hol_date_str = hol['date']
            hol_date = datetime.datetime.strptime(hol_date_str, '%Y-%m-%d').date()
            holiday = Holiday(hol_name, hol_date)
            # Use add_holiday function to add holidays to inner list
            self.add_holiday(holiday)
        print(f"Objects from the file '{file_location}' read successfully.")

    def json_save(self, file_location):
        hol_dict = {}
        for hol in self.inner_holidays:
            hol_dict[hol.name] = hol.date.__str__()
        dict_json = json.dumps(hol_dict)
        # Write out json file to selected file
        with open(file_location, "w") as save_file:
            save_file.write(dict_json)
        print(f"File location: '{file_location}'.")
        
    def scrape_holidays(self):
        # Scrape Holidays from https://www.timeanddate.com/holidays/us/ 
        months = {"Jan": "1", "Feb": "2", "Mar": "3", "Apr": "4", "May": "5", "Jun": "6", 
                    "Jul": "7", "Aug": "8", "Sep": "9", "Oct": "10", "Nov": "11", "Dec": "12"}
        for year in range(2020, 2025):
            url = f"https://www.timeanddate.com/holidays/us/{year}"
            res = requests.get(url)
            soup = BeautifulSoup(res.text, "html.parser")
            table = soup.find("section", attrs={"class":"table-data__table"}).find("tbody")
            rows = table.find_all("tr")
            for i in range(1, len(rows)):
                try:
                    name = rows[i].find("a").text
                    scraped_date = rows[i].find("th").text
                    space = scraped_date.find(" ")
                    scraped_month = scraped_date[:space]
                    month = scraped_month.replace(scraped_month, months[scraped_month])
                    day = scraped_date[space+1:]
                    date = datetime.date(year, int(month), int(day))
                    holiday = Holiday(name, date)
                    # Check to see if name and date of holiday is in inner_holidays array
                    if holiday not in self.inner_holidays:
                        # Add non-duplicates to inner_holidays
                        self.add_holiday(holiday)
                # Handle any exceptions
                except AttributeError:
                    pass

    def num_holidays(self):
        # Return the total number of holidays in inner_holidays
        num_hol = len(self.inner_holidays)
        return num_hol
    
    def filter_week(self, year, week_num):
        filt_year = list(filter(lambda hol: hol.date.isocalendar().year == year, self.inner_holidays))
        # Use a Lambda function to filter by week number and save this as holidays, use the filter on inner_holidays
        filt_week = filter(lambda hol: hol.date.isocalendar().week == week_num, filt_year)
        # Cast filter results as list
        holidays = list(filt_week)
        # return your holidays
        return holidays

    def display_week(self, holidays):
        # Use the value returned by filter_week() as a parameter
        # Output formated holidays in the week. 
        for holiday in range(len(holidays)):
            print(str(holidays[holiday]))

    def get_weather(self, year, week_num):
        # Convert week_num to range between two days
        week = f"{year}-W{week_num}"
        week_mon = datetime.datetime.strptime(week + '-1', "%Y-W%W-%w").date().__str__()
        week_sun = datetime.datetime.strptime(week + '-0', "%Y-W%W-%w").date().__str__()
        # Use Try / Except to catch problems
        # Query API for weather in that week range
        url = f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/Milwaukee/{week_mon}/{week_sun}?unitGroup=us&key={api_key}&contentType=json"
        json = requests.get(url).json()
        days = json['days']
        weather = {}
        for day in days:
            date = day['datetime']
            cond = day['conditions']
            weather[date] = cond
        # Format weather information and return weather list
        return weather

    def view_current_week(self):
        # Use the Datetime Module to look up current week and year
        today = datetime.date.today()
        curr_year = today.year
        curr_week = today.isocalendar().week
        # Use your filter_week function to get the list of holidays for the current week/year
        filt_hol = self.filter_week(curr_year, curr_week)
        # Ask user if they want to get the weather
        weather_prompt = input("Would you like to see this week's weather? [y/n]: ").lower().strip()
        print("\nThese are the holidays for this week: ")
        valid = 'n'
        while valid == 'n':  
            if weather_prompt == 'n':
                valid = 'y'
                # Use your display_week function to display the holidays in the week
                self.display_week(filt_hol)
            elif weather_prompt == 'y':
                valid = 'y'
                # If yes, use your get_weather function and display results
                weather = self.get_weather(curr_year, curr_week)
                for hol in filt_hol:
                    print(f"{str(hol)} - {weather[hol.date.__str__()]}")
            else:
                print("Invalid input, expecting 'y' or 'n'.")

def option_one(hol_list_list):
    print("\n\nAdd a Holiday\n=============")
    hol_name = input("Holiday Name: ").strip()
    valid = 'n'
    while valid == 'n':
        hol_date_inp = input(f"Date for {hol_name}: ")
        try:
            hol_date = datetime.datetime.strptime(hol_date_inp, '%Y-%m-%d').date()
            valid = 'y'
            print("\nSuccess:")
            hol_list_list.add_holiday(Holiday(hol_name, hol_date))
        except ValueError:
            print("\nError:\nInvalid date. Ensure that the proper format is followed (YYYY-MM-DD).\nPlease try again.\n")

def option_two(hol_list_list):
    print("\n\nRemove a Holiday\n================")
    found = 'n'
    while found == 'n':
        hol_name = input("Holiday Name: ").strip()
        print("")
        filt_hol = list(filter(lambda hol: hol.name == hol_name, hol_list_list))
        if filt_hol != []:
            found = 'y'
            for hol in filt_hol:
                clean = str(hol)
                print(clean)
            hol_year = int(input("\nHoliday Year: ").strip())
            chosen_hol = list(filter(lambda hol: hol.date.isocalendar().year == hol_year, filt_hol))
            index = hol_list_list.index(chosen_hol[0])
            hol_list_list.remove(hol_list_list[index])
            print(f"\nSuccess:\n{chosen_hol[0].name} has been removed from the list.\n")
        else:
            print(f"\nError:\n{hol_name} not found.\n")

def option_three(hol_list_inst):
    global saved
    print("\n\nSave Holiday List\n==================")
    confirm = input("Are you sure you want to save your changes [y/n]? ").lower().strip()
    valid = 'n'
    while valid =='n':
        if confirm == 'y':
            saved = 'y'
            valid = 'y'
            sf_name = input("Enter save file name: ").strip()
            hol_list_inst.json_save(f"{sf_name}.json")
            print("\nSuccess:\nYour changes have been saved.\n")
        elif confirm == 'n':
            valid = 'y'
            print("\nCancelled:\nHoliday list file save cancelled.\n")
        else:
            print("\nInvalid input, expecting a 'y' or 'n'.")

def option_four(hol_list_inst):
    print("\n\nView Holidays\n=================")
    year_inp = int(input("Which year? ").strip())
    if year_inp == datetime.date.today().year:
        valid = 'n'
        while valid == 'n':
            cyr_week_inp = input("Which week? [0-52, Leave blank for current week]: ").strip()
            if cyr_week_inp == "":
                valid = 'y'
                hol_list_inst.view_current_week()
            elif int(cyr_week_inp) >= 0 and int(cyr_week_inp) <= 52:
                valid = 'y'
                filt_week = hol_list_inst.filter_week(year_inp, cyr_week_inp)
                hol_list_inst.display_week(filt_week)
            else:
                print("\nInvalid input, expecting a value from 0 to 52, or no input.\n")
    else:
        valid = 'n'
        while valid == 'n':
            try:
                oyr_week_inp = int(input("Which week? [0-52]: ").strip())
                if oyr_week_inp >= 0 and oyr_week_inp <= 52:
                    valid = 'y'
                    filt_week = hol_list_inst.filter_week(year_inp, oyr_week_inp)
                    hol_list_inst.display_week(filt_week)
                else:
                    print("\nInvalid input, expecting a value from 0 to 52.\n")
            except ValueError:
                print("\nInvalid input, expecting integer.\n")

def option_five():
    global saved
    global finished
    print("\n\nExit\n====")
    valid = 'n'
    if saved == 'n':
        print("Are you sure you want to exit?\nYour changes will be lost.")
        confirm = input("[y/n] ")
        while valid == 'n':
            if confirm == 'y':
                valid = 'y'
                print("\nGoodbye!")
                finished = 'y'
            elif confirm == 'n':
                valid = 'y'
                print("\nGoing back to menu.\n")
            else:
                print("\nInvalid input, expecting 'y' or 'n'.\n")            
    if saved == 'y':
        confirm = input("Are you sure you want to exit? [y/n] ")
        while valid == 'n':
            if confirm == 'y':
                valid = 'y'
                print("\nGoodbye!")
                finished = 'y'
            elif confirm == 'n':
                valid = 'y'
                print("\nGoing back to menu.\n")
            else:
                print("\nInvalid input, expecting 'y' or 'n'.\n")

def main():
    global saved
    global finished
    # Initialize Holiday_List Object
    hol_list = Holiday_List()
    # Load JSON file via Holiday_List json_read function
    hol_list.json_read("holidays.json")
    # Scrape additional holidays using your Holiday_List scrape_holidays function
    hol_list.scrape_holidays()
    print(f"\nHoliday Management\n===================\nThere are {len(hol_list.inner_holidays)} holidays stored in the system.\n")
    # Create while loop for user to keep adding or working with the Calender
    saved = 'n'
    finished = 'n'
    while finished == 'n':
        # Display User Menu
        print("\nHoliday Menu\n================\n1. Add a Holiday\n2. Remove a Holiday\n3. Save Holiday List\n4. View Holidays\n5. Exit\n")
        # Takes user input for their action based on Menu and check the user input for errors
        choice = input("Make a selection: ")
        if choice == "1":
            option_one(hol_list.inner_holidays)
            saved = 'n'
        elif choice == "2":
            option_two(hol_list.inner_holidays)
            saved = 'n'
        elif choice == "3":
            option_three(hol_list)
        elif choice == "4":
            option_four(hol_list)
        elif choice == "5":
            option_five()
        else:
            print("Invalid input, exepecting an integer from a range of 1 to 5.")


if __name__ == "__main__":
    main()