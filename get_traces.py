'''

Automation code to get traces from background, browser, and websites using Selenium ChromeDriver
Data is stored in the traces, csv, ip_profiles folders.
Built for virtual environment. 

To start venv, cd into comps directory and type source bin/activate
Required packages:
    Python 3.9
    selenium - automation of web browser interaction. Using chrome on this one
        Chrome driver version 106
    scapy - take the wireshark traces: documentation https://scapy.readthedocs.io/en/latest/usage.html

Developed by: Aiden Chang, Anders Shenholm
Last Updated: 3/12/2022 at 12:00 PM by Anders Shenholm
Please contact Aiden Chang for questions

'''

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from scapy.all import *
from scapy.utils import RawPcapReader
from glob import glob
import chromedriver_autoinstaller
import time
import random
import subprocess
import os
import csv
import sys
import datetime
from shutil import rmtree


# imports for graphs below:
import pandas as pd
import numpy as np
import chart_studio.plotly as py
import cufflinks as cf
import plotly.express as px
import plotly.graph_objects as go
import re

'''
Installs chromedriver
Required for any Selenium Chrome activity
'''
def install_chromedriver():
    print("Installing chromedriver")
    try:
        chromedriver_autoinstaller.install()
        return 0
    except Exception as e:
        print(f"Failed to download chromedriver with exception: {e}")
        return -1


'''
Reads a csv file and returns a dictionary with unique ip's 
that appear in the trace and a count of each ip
'''
def get_trace_ips(filename):
    try:
        with open(filename, newline='') as csvfile:
            spamreader = csv.reader(csvfile, delimiter='\t', quotechar='|')
            ips = {}
            for row in spamreader:
                for i in range(1, 5):
                    if row[i] not in ips:
                        ips[row[i]] = 1
                    else:
                        ips[row[i]] += 1
            return ips
    except Exception as e:
        print(f"Error in function get_trace_ips: {e}")


'''
Reads a csv file and returns a list of unique ips
'''
def get_profile_ips(filename, frequency = False):
    return_list = []
    try:
        with open(filename, newline='') as csvfile:
            spamreader = csv.reader(csvfile)
            for row in spamreader:
                if row[0] not in return_list:
                    if frequency:
                        return_list.append([row[0], row[1]])
                    else:
                        return_list.append(row[0])
        return return_list
    except Exception as e:
        print(f"Error in function get_profile_ips: {e}")


'''
Function: sniff_website
Sniffs count packets on a website and creates the csv file and the pcap file.

Parameters:
    trace_count - int, number of traces to take
    website - str, the website we are sniffing (ex: "www.google.com")
    name - str, the name we are using for the file (ex: "google")
    packet_count - int, number of packets sniffing, default to 1000
Returns:
    csv file under: csv_files/[name]/[name_trace][i].csv
    pcap file under: traces/[name]/[name_trace][i].pcap
    function returns nothing
Example usage:
    sniff_website(20, "https://www.google.com", "google", 500)
Notes:
    for the subprocess.open tshark command to work, you might need to link tshark 
    mine was done like this:
        tshark ln -s /Applications/Wireshark.app/Contents/MacOS/tshark /usr/local/bin/tshark
'''
def sniff_website(trace_count, website, name, packet_count = 1500):
    MYDIR = (f"traces/{name}")
    if not os.path.isdir(MYDIR):
        print(f"Folder {MYDIR} does not exist. Creating new....")
        os.makedirs(MYDIR)
    MYDIR = (f"csv_files/{name}")
    if not os.path.isdir(MYDIR):
        print(f"Folder {MYDIR} does not exist. Creating new....")
        os.makedirs(MYDIR)

    for i in range(1, trace_count + 1):
        browser = webdriver.Chrome()
        if website != 0:
            browser.get(website)
        capture = sniff(packet_count)
        wrpcap(f"traces/{name}/{name}_trace{i}.pcap", capture)
        browser.quit()
        try:
            with open(f'csv_files/{name}/{name}_trace{i}.csv','w') as f:
                shark_args = f"tshark -r traces/{name}/{name}_trace{i}.pcap \
                      -Y -T fields -e frame.number -e ip.src -e ip.dst -e ipv6.src -e ipv6.dst".split()
                shark_args.insert(4, "not (dns or mdns or arp or ssdp)")
                subprocess.run(shark_args, stdout =f)
        except Exception as e:
            print(f"Iteration in sniff_website: {i}\n error: {e}")



'''
Function: build_ip_profiles
Builds a csv file with all the possible unique ip address that the website represents
    
Parameters:
    website - str, the website we are profiling. This must be identical to the folder scanning. (ex: "google")
Returns:
    profile built in /ip_profiles/{website}.csv
    function returns nothing
Example usage:
    build_ip_profiles("google")
Notes:
    If the folder does not exist in csv files it will throw an error.
'''
def build_ip_profiles(website):
    csv_profile_list = glob("csv_files/*")
    folder = ""
    for name in csv_profile_list:
        if website in name:
            folder = name
            break
    if not folder:
        print(f"Error in build ip profile: no csv file built for website {website}")
    else:
        ip_sets = []
        new_ips = []
        write_type = "w"
        write_path = f"./ip_profiles/{website}.csv"
        if os.path.exists(write_path):
            write_type = "a"
            ip_sets = get_profile_ips(write_path)

        csv_files = glob(f"{folder}/*")
        for file in csv_files:
            trace_ips = get_trace_ips(file)
            for key in trace_ips:
                if key and key not in ip_sets:
                    new_ips.append(key)
                    ip_sets.append(key)
                    
        with open(write_path, write_type) as csv_writer:
            writer_object = csv.writer(csv_writer)
            for ip in new_ips:
                writer_object.writerow([ip])


'''
Function: filter_ips
Subtracts ips that exist in filter_website from target_website. 
    
Parameters:
    target_website - string, name of target website ip profile
    filter_website - string, name of filter website ip profile
Returns:
    profile built in /ip_profiles/{target_website}.csv
    function returns nothing
Example usage:
    build_background_trace_profile("spotify", "google")
Notes:
    This overwrites the existing profile for target_website
'''
def filter_ips(target_website, filter_website):
    if not os.path.exists(f"ip_profiles/{target_website}.csv"):
        print(f"Error in function filter_ips: target website does not exist: ip_profiles/{target_website}.csv")
        return -1
    if not os.path.exists(f"ip_profiles/{filter_website}.csv"):
        print(f"Error in function filter_ips: filter website does not exist: ip_profiles/{filter_website}.csv")
        return -1
    
    target_ips = get_profile_ips(f"ip_profiles/{target_website}.csv")
    filter_ips = get_profile_ips(f"ip_profiles/{filter_website}.csv")

    filtered_list = []
    #if we are filtering against the background or chrome compare to 24 bit ips
    if filter_website in ["background", "chrome"]:
        #create list of 24 bit ip addresses
        filter_ips_24 = []
        for ip in filter_ips:
            if ip == "":
                continue
            if ":" not in ip:
                new_filter_ip = ip.split(".")
                new_filter_ip_24 = new_filter_ip[0] + "." + new_filter_ip[1] + "." + new_filter_ip[2]
            else:   #keep full ipv6 address
                new_filter_ip_24 = ip
            filter_ips_24.append(new_filter_ip_24)

        #check the first 24 bits of target ips against the filter ips
        for ip in target_ips:
            if ip == "":
                continue
            elif ":" not in ip:
                new_target_ip = ip.split(".")
                new_target_ip_24 = new_target_ip[0] + "." + new_target_ip[1] + "." + new_target_ip[2]
            else:   #keep full ipv6 address
                new_target_ip_24 = ip
            
            if new_target_ip_24 not in filter_ips_24:
                filtered_list.append(ip) #add the entire 32 bit ip

    else:
        for ip in target_ips:
            if ip not in filter_ips:
                filtered_list.append(ip)

    with open(f"ip_profiles/{target_website}.csv", "r") as inp, open(f"ip_profiles/{target_website}_temp.csv", "w") as out:
        writer = csv.writer(out)
        for row in csv.reader(inp):
            if row[0] in filtered_list:
                writer.writerow(row)
    os.remove(f"ip_profiles/{target_website}.csv")
    os.rename(f"ip_profiles/{target_website}_temp.csv", f"ip_profiles/{target_website}.csv")
    return 0

'''
Function: build_background_profile
Builds a profile of background activity.
    
Parameters:
    time_limit - int, number of seconds to take trace
Returns:
    profile built in /ip_profiles/background.csv
    function returns nothing
Example usage:
    build_background_profile(30)
Notes:

'''

def build_background_profile(time_limit):
    print("Starting to build background profile")
    # If folders don't exist, then create them.
    MYDIR = (f"traces/background")
    if not os.path.isdir(MYDIR):
        print(f"Folder {MYDIR} does not exist. Creating new....")
        os.makedirs(MYDIR)
    MYDIR = (f"csv_files/background")
    if not os.path.isdir(MYDIR):
        print(f"Folder {MYDIR} does not exist. Creating new....")
        os.makedirs(MYDIR)

    capture = sniff(count=500000, timeout=time_limit)      
    wrpcap(f"traces/background/background_trace1.pcap", capture)
    try:
        with open(f'csv_files/background/background_trace1.csv','w') as f:
            subprocess.run(f"tshark -r traces/background/background_trace1.pcap \
                -T fields -e frame.number -e ip.src -e ip.dst -e ipv6.src -e ipv6.dst".split(), stdout =f)
    except Exception as e:
        print(f"Background trace error: {e}")
    
    build_ip_profiles("background")
    print("done building background profile")



'''
Function: check_website_in_noisy_trace
compares an uploaded trace to a built IP profile

Parameters:
    file - a file uploaded by the user to be compared to a profile
    name - the name of the profile to be compared to
Returns:
    two lists, one with matches for 32 bit IPs and one with matches for 24 bit IPs
Example usage:
    check_website_in_noisy_trace("noisy_trace", "spotify")
Notes:
    returns (-1, -1) when it encounters an error
    only written for IPV4 right now
'''
def check_website_in_noisy_trace(file, name):
    if not os.path.exists(f"ip_profiles/{name}.csv"):
        print(f"Error in function check_website_in_noisy_trace, file ip_profiles/{name} does not exist")
    else:
        try:
            profile_ip_list = get_profile_ips(f"ip_profiles/{name}.csv", frequency = True)

            with open(f'csv_files/compare_file.csv','w') as f:
                subprocess.run(f"tshark -r {file} \
                -T fields -e frame.number -e ip.src -e ip.dst -e ipv6.src -e ipv6.dst".split(), stdout =f)
        
            compare_ips = get_trace_ips(f"csv_files/compare_file.csv")

            return_list = []

            for ip in compare_ips:
                if ip == "":
                    continue

                for profile_ip in profile_ip_list:
                    if ip == profile_ip[0]:
                        in_return_list = False
                        for return_ip in return_list:
                            if ip == return_ip[0]:
                                in_return_list = True
                        if not in_return_list:
                            return_list.append(profile_ip)
                        
            
            return return_list

        except Exception as e:
            print(f"Error in check_website_in_noisy_trace error: {e}. Line {traceback.format_exc()}")
            return -1, -1

##################################################################################################
# After this section its the usage of the above functions.
##################################################################################################

'''
Function: build_chrome_profile
Builds a profile for google.com (chrome homepage)
    
Parameters:
    trace_count - int, number of traces to take
Returns:
    profile built in /ip_profiles/chrome.csv
    traces and raw ip data stored in traces and csv folders respectively
    function returns nothing
Example usage:
    build_chrome_profile(20)
Notes:
    Requires a background profile: ip_profiles/background.csv 
'''

def build_chrome_profile(trace_count):
    if not os.path.exists(f"ip_profiles/background.csv"):
        print(f"Error in function build_chrome_profile: \n No background profile exists. Use build_background_profile first")
        return -1
    print("Starting to build chrome profile")
    sniff_website(trace_count, "https://www.google.com", "chrome", 1500)
    build_ip_profiles("chrome")
    if filter_ips("chrome", "background") != 0:
        print("Failed in making chrome profile")
    print("Done with chrome profile")

'''
Function: build_profile_without_noise
Builds a profile for a given website with chrome and background profiles filtered out
    
Parameters:
    trace_count - int, number of traces to take
    website - string, full web address (i.e. "https://youtube.com")
    name - string, name for data stored in ip_profiles, traces, csv_files
Returns:
    profile built in /ip_profiles/{name}.csv
    traces and raw ip data stored in traces and csv_files folders respectively
    function returns nothing
Example usage:
    build_profile_without_noise(20, "https://youtube.com", "youtube")
Notes:
    Requires a background profile: ip_profiles/background.csv 
    Requires a chrome profile: ip_profiles/chrome.csv 
'''

def build_profile_without_noise(trace_count, website, name):
    err_msg = ""
    if not os.path.exists(f"ip_profiles/background.csv"):
        err_msg = f"{err_msg} No background profile exists. Use build_background_profile first \n"    
    if not os.path.exists(f"ip_profiles/background.csv"):
        err_msg = f"{err_msg} No chrome profile exists. Use build_chrome_profile first \n"
    if err_msg != "":
        print(f"Error(s) in function build_chrome_profile: \n{err_msg}")
        return -1

    print(f"Starting to build {name}")
    sniff_website(trace_count, website, name)
    build_frequency_ip_profile(name)
    filter_ips(name,"background")
    filter_ips(name,"chrome")
    print(f"Done with building {name}")
    check_duplicates(name)
    
    
'''
Function: reset_folders
empties dynamic folders, currently: traces, csv_files, ip_profiles

Parameters:
    none
Returns:
    deletes any existing content in folders MYDIRS
    function returns nothing
Example usage:
    reset_folders()
Notes:
    uses shutil.rmtree
    Potential change: take a specific list of websites to reset for

'''
def reset_folders():
    MYDIRS = ["traces", "csv_files", "ip_profiles","match_graphs","bar_charts"]
    for dir in MYDIRS:
        try:
            rmtree(dir)
            os.mkdir(dir)
        except Exception as e:
            print(f"Failed to reset {dir}. Reason: {e}")


'''
Function: build_frequency_ip_profile
Builds a csv file including all unique ip addresses found in a filtered website trace as well as their frequency across traces
    
Parameters:
    website - str, the website we are profiling. This must be identical to the folder scanning. (ex: "google")
Returns:
    profile built in /ip_profiles/{website}.csv
    function returns nothing
Example usage:
    build_ip_profiles("google")
Notes:
    Currently built to delete old profile and rewrite it
'''
def build_frequency_ip_profile(website):
    if website not in os.listdir("csv_files"):
        print(f"Error in build ip profile: no csv file trace(s) for website {website}")
        quit()

    total_occurances = {}       # frequency of occurances across files
    trace_files = os.listdir(f"csv_files/{website}")
    PROFILE_PATH = (f"ip_profiles/{website}.csv")
    trace_count = 0
    for file in trace_files:
        local_occurances = {}   # occurances within each file
        trace_ips = get_trace_ips(f"csv_files/{website}/{file}")
        for key in trace_ips: 
            local_occurances[key] = 1

        for key in local_occurances:
            if key in total_occurances:
                total_occurances[key] += 1
            else:
                total_occurances[key] = 1

        trace_count += 1

    total_occurances = dict(sorted(total_occurances.items(), key=lambda x: x[1], reverse=True))
    for key in total_occurances:
        total_occurances[key] = (f"{total_occurances[key]/trace_count:.2f}")

    if os.path.exists(PROFILE_PATH):
        os.remove(PROFILE_PATH)
    with open(PROFILE_PATH, "w") as profile:
        writer = csv.writer(profile)
        for key in total_occurances:
            writer.writerow([key, total_occurances[key]])


'''
Function: report_to_user
Reports our confidence that a profiled application is present in a noisy trace.
    
Parameters:
    website_name - string, the name of the webiste being compared
    matched_list_32 - a list of matched 32 bit IP addresses
    matched_list_24 - a list of matched 24 bit IP addresses
Returns:
    a string with a report of our confidence
Example usage:
    report_to_user("spotify", return_list_32
Notes:

'''

def report_to_user(website_name, matched_list_32):
    if matched_list_32 == []:
        return("We are very confident that " + website_name + " is not present in this trace as we did not observe any 32 bit IP address matches")
    else:
        match_count_100 = 0
        match_count_70_90 = 0
        match_count_40_60 = 0
        match_count_10_30 = 0
        for match in matched_list_32:
            if float(match[1]) == 1.00:
                match_count_100 += 1
            elif float(match[1]) > 0.60:
                match_count_70_90 += 1
            elif float(match[1]) > 0.30:
                match_count_40_60 += 1
            else:
                match_count_10_30 += 1

    if match_count_100 == 1:
        return("We are very confident that " + website_name + " is present in this trace as " + str(match_count_100) + " \nIP address in the noisy trace showed up in every trace when you profiled " + website_name + "\n\n Refer to the graph for more detailed information on IP matches")

    elif match_count_100 > 1:
        return("We are extremely confident that " + website_name + " is present in this trace as " + str(match_count_100) + " \nIP addresses in the noisy trace showed up in every trace when you profiled " + website_name + "\n\n Refer to the graph for more detailed information on IP matches")
            
    elif match_count_70_90 >= 1 and match_count_40_60 >= 1:
        return("We are pretty confident that " + website_name + " is present in this trace as there are both IP address matches \nthat showed up in more than 70-90 percent of the traces and less than 40-60 percent of the traces when you profiled " + website_name + "\n\n Refer to the graph for more detailed information on IP matches")

    elif match_count_70_90 >= 1 and match_count_40_60 == 0:
         return("We are moderately confident that " + website_name + " is present in this trace as there are " + str(match_count_70_90) + " \nIP address matches that showed up in 70-90% percent of the traces when you profiled " + website_name + "\n\n Refer to the graph for more detailed information on IP matches")

    elif match_count_70_90 == 0 and match_count_40_60 >= 1:
        return("It is plausible that " + website_name + " is present in this trace as there are " + str(match_count_40_60) + " IP \naddress matches that showed up in 40-60 percent of the traces when you profiled " + website_name + "\n\n Refer to the graph for more detailed information on IP matches")
    
    elif match_count_10_30 >= 1:
        return("While there is a slim chance that " + website_name + " is present in this trace as there are " + str(match_count_10_30) + " \nIP address matches that showed up in 10-30 percent of the traces when you profiled " + website_name + ", \nwe hypothesize that these matches are due to ad services running in your messy trace and in your profiled application" + "\n\n Refer to the graph for more detailed information on IP matches")





'''
Function: make_individual_charts
Generates a bar graph for a given website profile plotting the percentage of traces for which a given IP address was present.
Saves the graph under the directory "bar_charts"
    
Parameters:
    profile - string, the name of profile csv file
    log -
Returns:
    function returns nothing
    graph saved in /bar_charts/
Example usage:
    make_individual_charts("open.spotify.com.csv", log)
Notes:
'''
def make_individual_charts(profile, log):
    if not os.path.exists("bar_charts"):
        os.mkdir("bar_charts")
    exclusions = {"background.csv":None, "chrome.csv":None, "google.csv":None} 
    cols = ["ip_address", "frequency_percentage"]
    graph_name = re.sub(r'.csv', '', profile)
    if profile in exclusions:
        log.warning(f"Cannot build profile {profile}")
    else:
        df = pd.read_csv(f"ip_profiles/{profile}", names=cols, header=None)
        df.sort_values(by=df.columns[1], inplace=True, ascending=False)
        df = df.head(n=30)
        fig = px.bar(df, x="ip_address", y="frequency_percentage",
                    title=f"IP Address Frequency for {graph_name}",
                    labels={
                    "ip_address" : "IP Address",
                    "frequency_percentage" : "Frequency of Traces IP Address was Present"}
                    )
        # fig.update_xaxes(categoryorder='category ascending')
        fig.update_layout(xaxis = {'categoryorder' : 'total descending'})
        fig.update_layout(
            xaxis_tickangle=45,
            title={
                'text': f"IP Address Frequency for {graph_name}",
                'y':0.9,
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'top'
            })
        fig.show()
        fig.write_image(f"bar_charts/{profile}fig.jpeg")

'''
Function: make_noisy_match_graph
Generates a bar graph for plotting the percentage of matches for IP addresses in a profile in a messy trace.
Saves the graph in /match_graphs/
    
Parameters:
    matched_list - list of lists, a match pair list of an IP address and its associated frequency
    graph_name - string, name of the graph (decided when called)
    log
Returns:
    function returns nothing
    graph saved in /match_graphs/
Example usage:
    make_noisy_match_graph(spotify_matches, "Spotify", log)
Notes:
'''
def make_noisy_match_graph(matched_list, graph_name, log): 
    if not os.path.exists("match_graphs"): 
        log.info(f"Creating directory match_graphs in match_graphs/{graph_name}") 
        os.mkdir("match_graphs") 
    try: 
        df = pd.DataFrame(matched_list, columns=['ip_address', 'match_frequency']) 
        df['match_frequency'] = df['match_frequency'].astype(float)
        df.sort_values(by="match_frequency", inplace=True, ascending=False) 
        df = df.head(n=20)
        fig = px.bar(df, x="ip_address", y="match_frequency", 
                     title = f"Frequency of IP Address Match for {graph_name}", 
                     color = "match_frequency", 
                     labels={ 
                    "ip_address" : "IP Address", 
                    "match_frequency" : "Address Match Frequency" })
        # fig.update_xaxes(categoryorder='category ascending') 
        fig.update_layout(xaxis = {'categoryorder' : 'total descending'})
        fig.update_layout(xaxis_tickangle=45) 
        fig.update_yaxes(rangemode="tozero") 
        fig.write_image(f"match_graphs/{graph_name}fig.jpeg") 
        log.info(f"Success in generating graph located in match_graphs/{graph_name}fig.jpeg")
    except Exception as e:
        log.critical(f"Failed to generate graph {graph_name} with exception {e}")


'''
Function: update_duplicate_ips
Checks a new profile for ip addresses found in other profiles
    
Parameters:
    name - str, the website we are profiling. This must be identical to the folder scanning. (ex: "spotify.com")
Returns:
    updates ip_profiles/duplicate_ips.csv if a new dupliacte is found
Example usage:
    update_duplicate_ips("spotify.com")
Notes:
'''
def update_duplicate_ips(name):
    if not os.path.isfile('ip_profiles/all_websites.csv'):  #don't need to run if this is the first profile
        return
    
    profile_ips = {}
    all_website_ips = {}
    duplicate_ips = {}

    with open(f'ip_profiles/{name}.csv', 'r') as source_file:
        reader = csv.reader(source_file)
        for row in reader:
            profile_ips[row[0]] = 0

    with open(f'ip_profiles/all_websites.csv', 'r') as source_file:
        reader = csv.reader(source_file)
        for row in reader:
            all_website_ips[row[0]] = 0

    for ip in profile_ips:
        if ip in all_website_ips:
            duplicate_ips[ip] = 0

    with open(f'ip_profiles/duplicate_ips.csv', 'a') as dest_file:
        writer = csv.writer(dest_file)
        for ip in duplicate_ips:
            writer.writerow([ip])

'''
Function: filter_duplicates
    Filters all profiles for addresses found in multiple profiles
Parameters:
    none
Returns:
    updates ip_profiles
Notes:
    currently used every time a new profile is build
'''
def filter_duplicates():
    if not os.path.isfile('ip_profiles/duplicate_ips.csv'):  #don't need to run if this is the first profile
        return
    
    profiles = []
    for filename in os.listdir("ip_profiles"):
        if filename.endswith(".csv"):
            profiles.append(filename.replace(".csv",""))

    for profile in profiles:
        if profile not in ["duplicate_ips", "all_websites"]:
            filter_ips(profile, "duplicate_ips")

'''
Function: update_all_website_addresses
    adds new ip addresses to list of all addresses found
Parameters:
    name - str, the website we are profiling. This must be identical to the folder scanning. (ex: "spotify.com")
Returns:
    updates ip_profiles/all_websites.csv
Notes:
    currently used every time a new profile is built
'''
def update_all_website_addresses(name):
    with open(f'ip_profiles/{name}.csv', 'r') as source_file:
        reader = csv.reader(source_file)
        with open('ip_profiles/all_websites.csv', 'a', newline='') as dest_file:
            writer = csv.writer(dest_file)
            for row in reader:
                writer.writerow([row[0]])

'''
Function: check_duplicates
    wrapper for all functions that check for duplicates on a new profile
Parameters:
    name - str, the website we are profiling. This must be identical to the folder scanning. (ex: "spotify.com")
Returns:
    none
Notes:
    currently used every time a new profile is built
'''

def check_duplicates(name):
    update_duplicate_ips(name)
    update_all_website_addresses(name)
    filter_duplicates()

def main():
    pass
    
main()

    
