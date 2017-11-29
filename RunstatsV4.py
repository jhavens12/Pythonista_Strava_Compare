import ui
import console
import requests
import json
import time
import datetime
from datetime import date
from dateutil.relativedelta import relativedelta, MO
from urllib.request import urlopen
from PIL import Image
import credentials

global token
token = credentials.smash_token

def get_monday():
    today = date.today()
    last_monday = today + relativedelta(weekday=MO(-1))
    last_monday_str = str(last_monday)
    monday = time.mktime(datetime.datetime.strptime(last_monday_str, "%Y-%m-%d").timetuple())
    monday_int = int(monday)
    monday_str = str(monday)
    return monday_int

def get_2017():
    year = 1483228800
    year_str = str(year)
    return year

def get_week():
    timestamp = int(time.time())
    week = timestamp - 604800
    week_str = str(week)
    return week

def get_month():
    timestamp = int(time.time())
    month = timestamp - 2592000
    return month

def get_yesterdays_month():
    timestamp = int(time.time())
    yesterday = timestamp - 86400
    yesterdays_month = yesterday - 2592000
    return yesterdays_month

def get_yesterday():
    timestamp = int(time.time())
    yesterday = timestamp - 86400
    return yesterday

def get_yesterdays_week():
    timestamp = int(time.time())
    yesterday = timestamp - 86400
    yesterdays_week = yesterday - 604800
    return yesterdays_week

def get_activities():
    global dataset
    url = 'https://www.strava.com/api/v3/activities/following'
    header = {'Authorization': 'Bearer '+credentials.api_key}
    param = {'per_page':200, 'page':1}
    dataset = requests.get(url, headers=header, params=param).json()
    return dataset

def get_my_activities():
    global my_dataset
    url = 'https://www.strava.com/api/v3/athlete/activities'
    header = {'Authorization': 'Bearer '+credentials.api_key}
    param = {'per_page':200, 'page':1}
    my_dataset = requests.get(url, headers=header, params=param).json()
    return my_dataset

# def get_smash_activities(time):
#     global my_smash_dataset
#     keys1 = []
#     values1 = []
#     url = "https://api.smashrun.com/v1/my/activities/search?fromDate={0}&access_token={1}".format(time,token)
#     data = requests.get(url)
#     data2 = data.json()
#     for i in data2:
#         keys1.append(i['startDateTimeLocal'])
#         values1.append(i['distance'])
#     #keys2 = convert_smash_timestamps(keys1)
#     new_dictionary = merge_lists(keys1,values1)
#     #print (new_dictionary)
#     return new_dictionary


def filter_by_username(dataset,user):
    #filters out strava by username, type and 0.0 distance removed
    keys1 = []
    values1 = []
    for i in dataset:
        if i['athlete']['username'] == user:
            if i['type'] == 'Run':
                if i['distance'] != 0.0:
                    keys1.append(i['start_date_local'])
                    values1.append(i['distance'])
    keys2 = convert_timestamps(keys1)
    new_dictionary = merge_lists(keys2,values1)
    return new_dictionary

def filter(dataset):
    #used for strava activites that do not require a username
    #return dictionary of time and mileage
    keys1 = []
    values1 = []
    for i in dataset:
        if i['type'] == 'Run':
            if i['distance'] != 0.0:
                keys1.append(i['start_date_local'])
                values1.append(i['distance'])
    keys2 = convert_timestamps(keys1)
    new_dictionary = merge_lists(keys2,values1)
    return new_dictionary

def convert_timestamps(time_list):
#convert to unix timestamp to compare
    time_list_unix = []
    for i in time_list:
        unix = time.mktime(datetime.datetime.strptime(i, "%Y-%m-%dT%H:%M:%SZ").timetuple())
        unix_int = int(unix)
        time_list_unix.append(unix_int)
    return time_list_unix

# def convert_smash_timestamps(time_list):
#     time_list_unix = []
#     for i in time_list:
#         unix = time.mktime(datetime.datetime.strptime(i, "%Y-%m-%dT%H:%M:%S").timetuple())
#         unix_int = int(unix)
#         time_list_unix.append(unix_int)
#     return time_list_unix

def merge_lists(keys,values):
    dictionary = dict(zip(keys, values))
    return dictionary

def purge_dictionary(dictionary,time):
    #compares strava dict to time to remove unwanted activities
    #returns miles for time
    for key in list(dictionary):
        if key < time:
            del dictionary[key]
    value_list = (dictionary.values())
    meters = sum(value_list)
    miles = meters_to_miles(meters)
    return miles

def purge_dictionary_double(dictionary,time1,time2):
#compares an older time and newer time to dictionary to remove values
#used for calculating yesterdays week or month etc
    if time1 > time2:
        newer_time = time1
        older_time = time2
    if time2 > time1:
        older_time = time1
        newer_time = time2
    for key in list(dictionary):
        if key < older_time:
            del dictionary[key]
    for key in list(dictionary):
        if key > newer_time:
            del dictionary[key]
    value_list = (dictionary.values())
    meters = sum(value_list)
    miles = meters_to_miles(meters)
    return miles

def smash_activities_to_miles(dictionary):
    #converst smash activites to miles - similar to purge_dictionary
    value_list = (dictionary.values())
    km = sum(value_list)
    miles = kilometers_to_miles(km)
    return miles

def meters_to_miles(meters):
    meters_int = int(meters)
    miles1 = meters_int * 0.000621371
    miles2 = ("{0:.2f}".format(miles1))
    return miles2

def kilometers_to_miles(kilometers):
    km_int = int(kilometers)
    miles1 = km_int*0.621371
    miles2 = ("{0:.2f}".format(miles1))
    return miles2

def difference(var1,var2):
    var1_flt = float(var1)
    var2_flt = float(var2)
    if var1_flt >= var2_flt:
        big_var = var1_flt
        small_var = var2_flt
    if var2_flt > var1_flt:
        big_var = var2_flt
        small_var = var1_flt
    new_var_int = big_var - small_var
    new_var_int_nice = ("{0:.2f}".format(new_var_int))
    new_var_str = str(new_var_int_nice)
    return new_var_str

def activity_count(dictionary):
    #counts amount of keys in dictionary
    amount = len(dictionary.keys())
    amount_str = str(amount)
    return amount_str

def compare_users(u1,week_miles_1,u2,week_miles_2):
    user3 = "TIE"
    var1_flt = float(week_miles_1)
    var2_flt = float(week_miles_2)
    if var1_flt > var2_flt:
        lead = u1
    if var1_flt < var2_flt:
        lead = u2
    if var1_flt == var2_flt:
        lead = user3
    lead2 = friendly_names(lead)
    return lead2

def friendly_names(name):
    if "cneistat" == name:
        new_name = "Casey"
    elif name == "jonathan_havens":
        new_name = "Jon"
    elif name == "dlcotnoir":
        new_name = "Danielle"
    else:
        new_name = name
        print()
    return new_name

def get_info():
    get_activities()
    get_my_activities()

#def main():

#get_info()
#main()
########################
########################
########################
user3 = credentials.user3
user2 = credentials.user2
user1 = credentials.user1

user1_name = credentials.user1_name
user2_name = credentials.user2_name
user3_name = credentials.user3_name

button_1_status = "na"
button_2_status = "na"
button_2_status_n = "na"
button_1_status_n = "na"

get_activities()
get_my_activities()

    # my_strava_dict = filter(my_dataset)
    # my_strava_miles = purge_dictionary(my_strava_dict,get_2017())
    # my_strava_count = activity_count(my_strava_dict)

def get_info_1(self):
    dict_user1 = filter_by_username(dataset,self)
    dict_user1_1 = dict_user1.copy()
    since_monday_miles_1 = purge_dictionary(dict_user1,get_monday())
    monday_count_1 = activity_count(dict_user1)
    week_miles_1 = purge_dictionary(dict_user1_1,get_week())
    week_count_1 = activity_count(dict_user1_1)
    dict_user1 = filter_by_username(dataset,self)
    dict_user1_1 = dict_user1.copy()
    user_1_yesterdays_week = purge_dictionary_double(dict_user1,get_yesterdays_week(),get_yesterday())
    user_1_yesterdays_week_count = activity_count(dict_user1)
    user_1_yesterdays_since_monday = purge_dictionary_double(dict_user1_1,get_monday(),get_yesterday())
    user_1_yesterdays_since_monday_count = activity_count(dict_user1_1)
    dict_user1 = filter_by_username(dataset,self)
    dict_user1_1 = dict_user1.copy()
    user_1_24_hour_miles = purge_dictionary(dict_user1,get_yesterday())
    user_1_24_hour_count = activity_count(dict_user1)

#Sets labels in gui
    # label1= v['label1']
    # label1.text = "Danielle"
    label27= v['label27']
    label27.text = since_monday_miles_1
    label2= v['label2']
    label2.text = monday_count_1
    label3= v['label3']
    label3.text = week_miles_1
    label4= v['label4']
    label4.text = week_count_1
    # label5= v['label5']
    # label5.text = user_1_yesterdays_week
    # label6= v['label6']
    # label6.text = user_1_yesterdays_week_count
    # label7= v['label7']
    # label7.text = user_1_yesterdays_since_monday
    # label8= v['label8']
    # label8.text = user_1_yesterdays_since_monday_count
    label9= v['label9']
    label9.text = user_1_24_hour_miles
    label10= v['label10']
    label10.text = user_1_24_hour_count

def get_info_2(self):
    dict_user2 = filter_by_username(dataset,self)
    dict_user2_1 = dict_user2.copy()
    since_monday_miles_2 = purge_dictionary(dict_user2,get_monday())
    monday_count_2 = activity_count(dict_user2)
    week_miles_2 = purge_dictionary(dict_user2_1,get_week())
    week_count_2 = activity_count(dict_user2_1)
    dict_user2 = filter_by_username(dataset,self)
    dict_user2_1 = dict_user2.copy()
    user_2_yesterdays_week = purge_dictionary_double(dict_user2,get_yesterdays_week(),get_yesterday())
    user_2_yesterdays_week_count = activity_count(dict_user2)
    user_2_yesterdays_since_monday = purge_dictionary_double(dict_user2_1,get_monday(),get_yesterday())
    user_2_yesterdays_since_monday_count = activity_count(dict_user2_1)
    dict_user2 = filter_by_username(dataset,self)
    dict_user2_1 = dict_user2.copy()
    user_2_24_hour_miles = purge_dictionary(dict_user2,get_yesterday())
    user_2_24_hour_count = activity_count(dict_user2)

    # label11= v['label11']
    # label11.text = self
    label28= v['label28']
    label28.text = since_monday_miles_2
    label12= v['label12']
    label12.text = monday_count_2
    label13= v['label13']
    label13.text = week_miles_2
    label14= v['label14']
    label14.text = week_count_2
    # label15= v['label15']
    # label15.text = user_2_yesterdays_week
    # label16= v['label16']
    # label16.text = user_2_yesterdays_week_count
    # label17= v['label17']
    # label17.text = user_2_yesterdays_since_monday
    # label18= v['label18']
    # label18.text = user_2_yesterdays_since_monday_count
    label19= v['label19']
    label19.text = user_2_24_hour_miles
    label20= v['label20']
    label20.text = user_2_24_hour_count

def compare_display(user1,user2):

    dict_user1 = filter_by_username(dataset,user1)
    dict_user1_1 = dict_user1.copy()
    since_monday_miles_1 = purge_dictionary(dict_user1,get_monday())
    monday_count_1 = activity_count(dict_user1)
    week_miles_1 = purge_dictionary(dict_user1_1,get_week())
    week_count_1 = activity_count(dict_user1_1)
    dict_user1 = filter_by_username(dataset,user1)
    dict_user1_1 = dict_user1.copy()
    user_1_yesterdays_week = purge_dictionary_double(dict_user1,get_yesterdays_week(),get_yesterday())
    user_1_yesterdays_week_count = activity_count(dict_user1)
    user_1_yesterdays_since_monday = purge_dictionary_double(dict_user1_1,get_monday(),get_yesterday())
    user_1_yesterdays_since_monday_count = activity_count(dict_user1_1)
    dict_user1 = filter_by_username(dataset,user1)
    dict_user1_1 = dict_user1.copy()
    user_1_24_hour_miles = purge_dictionary(dict_user1,get_yesterday())
    user_1_24_hour_count = activity_count(dict_user1)

    dict_user2 = filter_by_username(dataset,user2)
    dict_user2_1 = dict_user2.copy()
    since_monday_miles_2 = purge_dictionary(dict_user2,get_monday())
    monday_count_2 = activity_count(dict_user2)
    week_miles_2 = purge_dictionary(dict_user2_1,get_week())
    week_count_2 = activity_count(dict_user2_1)
    dict_user2 = filter_by_username(dataset,user2)
    dict_user2_1 = dict_user2.copy()
    user_2_yesterdays_week = purge_dictionary_double(dict_user2,get_yesterdays_week(),get_yesterday())
    user_2_yesterdays_week_count = activity_count(dict_user2)
    user_2_yesterdays_since_monday = purge_dictionary_double(dict_user2_1,get_monday(),get_yesterday())
    user_2_yesterdays_since_monday_count = activity_count(dict_user2_1)
    dict_user2 = filter_by_username(dataset,user2)
    dict_user2_1 = dict_user2.copy()
    user_2_24_hour_miles = purge_dictionary(dict_user2,get_yesterday())
    user_2_24_hour_count = activity_count(dict_user2)

    compare_running_week = difference(week_miles_1,week_miles_2)
    running_week_lead = compare_users(user1,week_miles_1,user2,week_miles_2)
    compare_since_monday = difference(since_monday_miles_1,since_monday_miles_2)
    monday_lead = compare_users(user1,since_monday_miles_1,user2,since_monday_miles_2)
    compare_24_hours = difference(user_1_24_hour_miles,user_2_24_hour_miles)
    compare_24_lead = compare_users(user1,user_1_24_hour_miles,user2,user_2_24_hour_miles)

    label21= v['label21']
    label21.text = compare_running_week
    if compare_running_week == button_1_status_n:
        label21.text_color = 'red'
    elif compare_running_week== button_2_status_n:
        label21.text_color = 'blue'

    label22= v['label22']
    label22.text = running_week_lead
    if running_week_lead == button_1_status_n:
        label22.text_color = 'red'
    elif running_week_lead == button_2_status_n:
        label22.text_color = 'blue'

    label23= v['label23']
    label23.text = compare_since_monday
    if compare_since_monday== button_1_status_n:
        label23.text_color = 'red'
    elif compare_since_monday == button_2_status_n:
        label23.text_color = 'blue'

    label24= v['label24']
    label24.text = monday_lead
    if monday_lead == button_1_status_n:
        label24.text_color = 'red'
    elif monday_lead == button_2_status_n:
        label24.text_color = 'blue'

    label25= v['label25']
    label25.text = compare_24_hours
    if compare_24_hours == button_1_status_n:
        label25.text_color = 'red'
    elif compare_24_hours == button_2_status_n:
        label25.text_color = 'blue'

    label26= v['label26']
    label26.text = compare_24_lead
    if compare_24_lead == button_1_status_n:
        label26.text_color = 'red'
    elif compare_24_lead == button_2_status_n:
        label26.text_color = 'blue'

    #v['imageview1'].image = ui.Image.named('casey_circle.png')
#   v['imageview2'].image = ui.Image.named('jon_circle.png')

def refresh_week(self):
    miles = get_miles(get_week())
    runs = get_run_count(get_week())
    milesstr = str(miles)
    runsstr = str(runs)
    label1= v['label1']
    label1.text = runsstr
    label2= v['label2']
    label2.text = milesstr


def refresh_month(self):
    miles = get_miles(get_month())
    runs = get_run_count(get_month())
    milesstr = str(miles)
    runsstr = str(runs)
    label1= v['label1']
    label1.text = runsstr
    label2= v['label2']
    label2.text = milesstr

def button_action_1(sender):
    global button_1_status
    global button_1_status_n
    if button1.selected_index == 0:
        v['label1'].text = 'Danielle'
        #runs script with user one, changes labels in script
        get_info_1(user1)
        #sets global button_1_status variable
        button_1_status = user1
        #sets another global variable that will not be changed to friendly name
        button_1_status_n = friendly_names(user1)
        #compares two current global variables and changes labels
        compare_display(button_1_status,button_2_status)
    if button1.selected_index == 1:
        v['label1'].text ='Jon'
        get_info_1(user2)
        button_1_status = user2
        button_1_status_n = friendly_names(user2)
        compare_display(button_1_status,button_2_status)
    elif button1.selected_index == 2:
        v['label1'].text ='Casey'
        get_info_1(user3)
        button_1_status = user3
        button_1_status_n = friendly_names(user3)
        compare_display(button_1_status,button_2_status)

def button_action_2(sender):
    global button_2_status
    global button_2_status_n
    if button2.selected_index == 0:
        v['label11'].text = 'Danielle'
        get_info_2(user1)
        button_2_status = user1
        button_2_status_n = friendly_names(user1)
        compare_display(button_1_status,button_2_status)
    if button2.selected_index == 1:
        v['label11'].text ='Jon'
        get_info_2(user2)
        button_2_status = user2
        button_2_status_n = friendly_names(user2)
        compare_display(button_1_status,button_2_status)
    elif button2.selected_index == 2:
        v['label11'].text ='Casey'
        get_info_2(user3)
        button_2_status = user3
        button_2_status_n = friendly_names(user3)
        compare_display(button_1_status,button_2_status)
#####



# starts gui
v = ui.load_view()
v.background_color = "black"

button1 = v['segmentedcontrol1']
button1.action = button_action_1
button2 = v['segmentedcontrol2']
button2.action = button_action_2


v.present(style='sheet', hide_title_bar=True)


# populates initially
#get_info_1(user1)
#get_info_2(user2)
