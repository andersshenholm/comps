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
Last Updated: 1/19/2022 at 12:00 PM by Anders Shenholm
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
Reads a csv file and returns four dictionaries. 
source_ip - a dic with unique ip's of the source and the count of each ip
dest_ip - a dic with unique ip's of the destination and the count of each ip
ipv6_source_ip - a dic with unique ipv6's of the source and the count of each ip
ipv6_dest_ip - a dic with unique ipv6's of the destination and the count of each ip
'''
def get_ips(filename):
    try:
        with open(filename, newline='') as csvfile:
            spamreader = csv.reader(csvfile, delimiter='\t', quotechar='|')
            next(spamreader)
            source_ip = {}
            dest_ip = {}
            ipv6_source_ip = {}
            ipv6_dest_ip = {}
            for row in spamreader:
                if row[1] not in source_ip:
                    source_ip[row[1]] = 1
                else:
                    source_ip[row[1]] += 1
                if row[2] not in dest_ip:
                    dest_ip[row[2]] = 1
                else:
                    dest_ip[row[2]] += 1
                if row[3] not in ipv6_source_ip:
                    ipv6_source_ip[row[3]] = 1
                else:
                    ipv6_source_ip[row[3]] += 1
                if row[4] not in ipv6_dest_ip:
                    ipv6_dest_ip[row[4]] = 1
                else:
                    ipv6_dest_ip[row[4]] += 1
            return source_ip, dest_ip, ipv6_source_ip, ipv6_dest_ip
    except Exception as e:
        print(f"Error in function get_ips: {e}")


'''
Reads a csv file and returns a list of unique ips
'''
def get_individual_ips(filename):
    return_list = []
    try:
        with open(filename, newline='') as csvfile:
            spamreader = csv.reader(csvfile)
            for row in spamreader:
                if row[0] not in return_list:
                    return_list.append(row[0])
        return return_list
    except Exception as e:
        print(f"Error in function get_individual_ips: {e}")


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
def sniff_website(trace_count, website, name, packet_count = 1000):
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
                subprocess.run(f"tshark -r traces/{name}/{name}_trace{i}.pcap \
                    -T fields -e frame.number -e ip.src -e ip.dst -e ipv6.src -e ipv6.dst".split(), stdout =f)
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
            ip_sets = get_individual_ips(write_path)

        csv_files = glob(f"{folder}/*")
        for file in csv_files:
            src_ip, dst_ip, ipv6_src_ip, ipv6_dst_ip = get_ips(file)
            for key in src_ip:
                if key and key not in ip_sets:
                    new_ips.append(key)
                    ip_sets.append(key)
            for key in dst_ip:
                if key and key not in ip_sets:
                    new_ips.append(key)
                    ip_sets.append(key)
            for key in ipv6_src_ip:
                if key and key not in ip_sets:
                    new_ips.append(key)
                    ip_sets.append(key)
            for key in ipv6_dst_ip:
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
    
    target_ips = get_individual_ips(f"ip_profiles/{target_website}.csv")
    filter_ips = get_individual_ips(f"ip_profiles/{filter_website}.csv")

    filtered_list = []
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
    sniff_website(trace_count, 0, "chrome")
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
    build_ip_profiles(name)
    filter_ips(name,"background")
    filter_ips(name,"chrome")
    print(f"Done with building {name}")
    
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
    MYDIRS = ["traces", "csv_files", "ip_profiles"]
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
        src_ip, dst_ip, ipv6_src_ip, ipv6_dst_ip = get_ips(f"csv_files/{website}/{file}")
        for key in src_ip: local_occurances[key] = 1
        for key in dst_ip: local_occurances[key] = 1
        for key in ipv6_src_ip: local_occurances[key] = 1
        for key in ipv6_dst_ip: local_occurances[key] = 1

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



def main():
    install_chromedriver()
    build_background_profile(30)
    build_chrome_profile(2)
    sniff_website(20, "https://spotify.com", "spotify")
    build_frequency_ip_profile("spotify")


main()

    
