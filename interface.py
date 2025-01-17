'''
Created by Aiden Chang

GUI pased off of the python tkinter package. Uses functionality from get_traces
Built for virtual environment. 

To start venv, cd into comps directory and type source bin/activate
Required packages:
    All the packages stated in requirements.txt

WARNING:
    Some m1 modules will Virtual environments might have issues with tkinter
    Please reinstall your virtual environment if tkinter is giving issues

Developed by: Aiden Chang, Jeylan Jones
Last Updated: 2/22/2023 at 7:33 PM by Aiden Chang
Please contact Aiden Chang for questions

To activate GUI, type:
    $ python3 interface.py

'''


import tkinter as tk                # python 3
from tkinter import font as tkfont  # python 3
from tkinter import filedialog # python 3
import time
import os
import shutil
import threading
from urllib.parse import urlparse
import datetime
import logging as log





#importing trace functions
from get_traces import *

log.basicConfig(filename='log.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')
log.getLogger().setLevel(log.INFO)
log.info("-"*10)
log.info("Starting Log file")
current_path = os.path.dirname(os.path.abspath(__file__))
PLACEHOLDER = None
BACKGROUND_BUILT = False
install_chromedriver()

def test_function1():
    print("In test function 1!")
    time.sleep(10)
def test_function2():
    print("In test function 2!")

class SampleApp(tk.Tk):

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        self.title_font = tkfont.Font(family='Helvetica', size=25, weight="bold", slant="italic")
        self.sub_title_font = tkfont.Font(family='Helvetica', size=15)

        # the container is where we'll stack a bunch of frames
        # on top of each other, then the one we want visible
        # will be raised above the others
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        if os.path.exists(f"{current_path}/ip_profiles/background.csv"):
            global BACKGROUND_BUILT
            BACKGROUND_BUILT = True


        self.frames = {}
        for F in (StartPage, InstructionsPage, BackgroundPage, ProfilePage, UploadTracePage, AboutPage, BuiltProfilePage, WarningPage):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame
            # put all of the pages in the same location;
            # the one on the top of the stacking order
            # will be the one that is visible.
            frame.grid(row=0, column=0, sticky="nsew")
        
        self.show_frame("StartPage")


        
    def show_frame(self, page_name : str) -> None:
        '''Show a frame for the given page name'''
        frame = self.frames[page_name]
        frame.event_generate("<<ShowFrame>>")
        frame.tkraise()



class StartPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        label = tk.Label(self, text="Trace Analyzer", font=controller.title_font)
        label.pack(side="top", fill="x", pady=10)
        sub_label = tk.Label(self, text="Please read the instructions to get started!", font=controller.sub_title_font)
        sub_label.pack(side="top", fill="x", pady=10)

        button1 = tk.Button(self, text="Instructions", highlightbackground='black', height= 2, width=15, padx=10, pady=10,
                            command=lambda: controller.show_frame("InstructionsPage"))
        button2 = tk.Button(self, text="Build Background Profile", highlightbackground='black', height= 2, width=15 ,padx=10, pady=10,
                            command=lambda: controller.show_frame("BackgroundPage"))
        button3 = tk.Button(self, text="Build Profile for a Website",highlightbackground='black', height= 2, width=15 ,padx=10, pady=10,
                            command=lambda: controller.show_frame("ProfilePage"))
        button4 = tk.Button(self, text="Upload Your Own Trace", highlightbackground='black', height=2, width=15 ,padx=10, pady=10,
                            command=lambda: controller.show_frame("UploadTracePage"))
        button7 = tk.Button(self, text="Check Built Profiles", highlightbackground='black', height=2, width=15 ,padx=10, pady=10,
                            command=lambda: controller.show_frame("BuiltProfilePage"))
        clear_button = tk.Button(self, text="Clear Folders", highlightbackground='black', height=2, width=15 ,padx=10, pady=10,
                            command=lambda: controller.show_frame("WarningPage"))
        button5 = tk.Button(self, text="About", highlightbackground='black', height= 5, width=10,
                            command=lambda: controller.show_frame("AboutPage"))
        button6 = tk.Button(self, text="Quit", highlightbackground='black', height= 5, width=10, 
                            command=controller.destroy)

        button1.pack()
        button2.pack()
        button3.pack()
        button4.pack()
        button7.pack()
        clear_button.pack()
        button5.pack(anchor="s", side="right")
        button6.pack(anchor="s", side="left")
        


class InstructionsPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        label = tk.Label(self, text="Instructions", font=controller.title_font)
        label.pack(side="top", fill="x", pady=10)
        
        label2 = tk.Label(self, text="\n1. Make sure you're connected to the internet.\n\n2. Shut down any apps or browsers running on your computer and turn off Bluetooth.\n\n3. Build a background profile.\n\n4. Build website profiles for websites you want to identify in your network traffic.\n\n5. Upload a network traffic trace (.pcap or .pcapng) then click"+ '"generate report"'+" to see which of your profiled\nwebsites were identified in the trace.",justify='left')
        label2.pack(padx=.06, pady=10)
        label3 = tk.Label(self, text="To generate network traffic traces, we recommend using Wireshark: www.wireshark.org/download.html",justify='left', font='Times 16 bold')
        label3.pack(padx=.06, pady=10)
        
        button = tk.Button(self, text="Back to Start Page",
            highlightbackground='black', height= 5, width=12,
            command=lambda: controller.show_frame("StartPage"))
        button.pack(anchor="s", side="left")


class BackgroundPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.background_built = False
        self.controller = controller
        self.number_of_traces = 10 
        self.timeout = 600 

        label = tk.Label(self, text="Tracing Computer Background", font=controller.title_font)
        label.pack(side="top", fill="x", pady=10)
        
        warning_label = tk.Label(self, text=f"WARNING please close all other apps and bluetooth for the best results", font="Times 20 bold", fg="dark red")
        warning_label.pack(side="top", fill="x", pady=10)

        dt_m = "Not built"
        if not os.path.exists(f"{current_path}/ip_profiles"):
            os.mkdir(f"{current_path}/ip_profiles")
        if os.path.exists(f"{current_path}/ip_profiles/background.csv"):
            dt_m = datetime.datetime.fromtimestamp(os.path.getmtime(f"{current_path}/ip_profiles/background.csv"))
        self.last_background_built = tk.Label(self, text=f"Last Background Build: {dt_m}", font="Times 16 bold", fg="dark blue")
        self.last_background_built.pack(side="top", fill="x", pady=10)

        label = tk.Label(self, text=f"Enter timeout (recommended: {self.timeout})")
        label.pack(side="top", fill="x", pady=10)
        self.inputtxt = tk.Text(self,
                        height = 3,
                        width = 20, borderwidth=1, relief='solid')
        
        self.inputtxt.pack()


        background_button = tk.Button(self, text="Start Background Trace",
            highlightbackground='black', height= 5, width=15,
            command=lambda:self.start_background_process())
        self.label1 = tk.Label(self, text="")
        self.label1.pack(side="top", fill="x", pady=10)

        button = tk.Button(self, text="Back to Start Page",
            highlightbackground='black', height= 5, width=12,
            command=lambda: controller.show_frame("StartPage"))
        background_button.pack(side="top", pady=10)
        button.pack(anchor="s", side="left")
    
    
    

    
    def build_background_on_thread(self, timeout : int) -> None:

        log.info("Building background in process...")
        self.label1.config(text="Building background in process...")

        try:
            install_chromedriver()
            build_background_profile(timeout)
            build_chrome_profile(self.number_of_traces)
            global BACKGROUND_BUILT
            BACKGROUND_BUILT = True
            dt_m = datetime.datetime.fromtimestamp(os.path.getmtime(f"{current_path}/ip_profiles/background.csv"))
            self.last_background_built.config(text = f"Last Background Build: {dt_m}")
            self.label1.config(text="Done Building Background Profile")
            log.info("Done Building Background Profile in ./traces/background")
        except Exception as e:
            self.label1.config(text="Error in building background profile, please check log file")
            log.critical(f"Failed building background profile with exception {e}")
        self.background_built = False

    def start_background_process(self) -> None:
        inp = self.inputtxt.get(1.0, "end-1c")
        if inp and inp.isdigit():
            self.timeout = int(inp)
        if self.background_built == False:
            self.background_built = True
            newthread = threading.Thread(target=self.build_background_on_thread, args = (self.timeout,))
            newthread.start()
    
        


class ProfilePage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        label = tk.Label(self, text="Building a Web Profile", font=controller.title_font)
        label.pack(side="top", fill="x", pady=10)

        dt_m = "Not built"
        if os.path.exists(f"{current_path}/ip_profiles/background.csv"):
            dt_m = datetime.datetime.fromtimestamp(os.path.getmtime(f"{current_path}/ip_profiles/background.csv"))
        self.last_background_built = tk.Label(self, text=f"Last Background Build: {dt_m}", font="Times 16 bold", fg="dark blue")
        self.last_background_built.pack(side="top", fill="x", pady=10)


        # TextBox Creation
        self.inputtxt = tk.Text(self,
                        height = 3,
                        width = 40, borderwidth=1, relief='solid')
        
        self.inputtxt.pack()

        # Button Creation
        printButton = tk.Button(self,
                                text = "Build website", 
                                command = lambda:self.build_website_background(), height= 5, width=12)
        printButton.pack(side="top", pady=10)

        self.bind("<<ShowFrame>>", self.on_show_frame)
        self.lbl = tk.Label(self, text = "")
        self.lbl.pack()

        self.build_background_label = tk.Label(self, text="Please build background first")
        self.build_background_label.pack(side="top", fill="x", pady=10)
 
    
        button = tk.Button(self, text="Back to Start Page",
            highlightbackground='black', height= 5, width=13,
            command=lambda: controller.show_frame("StartPage"))
        button.pack(anchor="s", side="left")
    

    def on_show_frame(self, event):
        if os.path.exists(f"{current_path}/ip_profiles/background.csv"):
            dt_m = datetime.datetime.fromtimestamp(os.path.getmtime(f"{current_path}/ip_profiles/background.csv"))
            self.last_background_built.config(text = f"Last Background Build: {dt_m}")


    def start_build_profile(self, traces, inp, domain):
        try:
            build_profile_without_noise(traces,inp,domain)
            self.build_background_label.config(text = f"Done building website profile")
            log.info(f"Built profile for website: {inp}")
        except Exception as e:
            self.build_background_label.config(text = f"something went wrong in building website profile, please check log files")
            log.critical(f"Failed to build {inp} profile with exception {e}")


    def build_website_background(self) -> None:
        inp = self.inputtxt.get(1.0, "end-1c")
        self.lbl.config(text = "Selected Website: "+inp)
        log.info(f"Requesting a build for website: {inp}")
        domain = urlparse(inp).netloc
        if domain == "google.com" or domain == "www.google.com":
            domain = None
            inp = None
            self.build_background_label.config(text = "Google profiles cannot be built using this program")
        else:
            if BACKGROUND_BUILT and inp and domain:
                self.build_background_label.config(text = f"Building website background for {inp}\nName: {domain}")
                newthread = threading.Thread(target=self.start_build_profile, args = (10,inp,domain))
                newthread.start()

            else:
                self.build_background_label.config(text = "Background not built yet")
                if BACKGROUND_BUILT:
                    self.build_background_label.config(text = "Background is built, incorrect format with input website. Exmp: https://open.spotify.com/")
                log.warning("Failed to build background profile with unsatisfied prerequisites")




class UploadTracePage(tk.Frame):
            
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        label = tk.Label(self, text="Upload Trace Here!", font=controller.title_font)
        label.pack(side="top", fill="x", pady=10)
        upload_button = tk.Button(self, text="Choose a File...", command=lambda:self.UploadPcap())
        upload_button.pack()

        report_button = tk.Button(self, text="Generate Report", highlightbackground='black', height= 5, width=12,command=lambda:self.start_report())
        report_button.pack(pady=50)
        
        self.file_label = tk.Label(self, text="")
        self.file_label.pack(side="top", fill="x", pady=10)

        self.generated_file_path = tk.Label(self, text="")
        self.generated_file_path.pack(side="top", fill="x", pady=10)


        back_button = tk.Button(self, text="Back to Start Page",
            highlightbackground='black', height= 5, width=12,
            command=lambda: controller.show_frame("StartPage"))
        back_button.pack(anchor="s", side="left")
        

    def UploadPcap(self, pkt=None) -> None:
            filename = filedialog.askopenfilename(title="Choose a File...", filetypes=(('Pcap Files', '.pcap .pcapng' ),))
            global PLACEHOLDER
            PLACEHOLDER = filename
            self.file_label.config( text=f"Chosen: {filename}")
            
    
    def start_report(self) -> None:
        log.info(f"Building report with filename chosen: {PLACEHOLDER}")
        self.file_label.config(text="Building report in progress...")
        if PLACEHOLDER != None:
            newthread = threading.Thread(target=self.generateReport)
            newthread.start()
        else:
            self.file_label.config(text="File not selected")



    def generateReport(self) -> None:
        full_report = ''
        for values in os.listdir(f"{current_path}/ip_profiles"):
            if values[-3:] == "csv":
                profile_name = values[:-4]
                if profile_name != "background" and profile_name != "chrome":
                    try:
                        matches = check_website_in_noisy_trace(PLACEHOLDER, profile_name)
                        report = report_to_user(profile_name, matches)  
                        full_report = full_report + f"{report}\n here are the matched ip addresses from our messy trace in profile and their respective frequency. Format: [IP, frequency]:::: {matches}\n\n\n"        
                        make_noisy_match_graph(matches, profile_name, log)
                        self.generated_file_path.config(text="Report generated in full_report.txt\nGraphs generated in match_graphs directory")
                        log.info("Report generated in full_report.txt")
                    except Exception as e:
                        log.critical(f"Failed to generate report on file: {PLACEHOLDER}, with profile {profile_name}\n Exception: {e}")
                        self.generated_file_path.config(text="Failed to generate report please check log files")
        with open('full_report.txt', 'w') as f:
            f.write(full_report)
        self.file_label.config(text="Generated Report")
        log.info(f"Generated report with file: {PLACEHOLDER}")





class AboutPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        label = tk.Label(self, text="About This Project", font=controller.title_font)
        label.pack(side="top", fill="x", pady=10)
        
        label2 = tk.Label(self, text="The Trace Analyzer was built by 5 senior CS students at Carleton College: Aiden Chang, Anders Shenholm,\n Jeylan Jones, Luke Mager, and Shaun Baron-Furuyama. Our goal was to design a system for determining which\nwebsites are present in a network traffic trace.\n\nAfter taking and examining many network traces, we concluded that 24-bit filtering of IP addresses would be the\nmost reliable and broadly-applicable method for profiling web applications. Our project offers insight into how\na malicious actor (i.e. person-in-the-middle) could gather information about one's online activity even from\nencrypted network traffic. We also hope that it's a fun, accessible tool that people can use to learn about the\ninternet.\n\n\nFor questions or feedback, please don't hesitate to contact us!")
        label2.pack(side="top", fill="x", pady=10)
        
        button = tk.Button(self, text="Back to Start Page",
            highlightbackground='black', height= 5, width=12,
            command=lambda: controller.show_frame("StartPage"))
        button.pack(anchor="s", side="left")

class BuiltProfilePage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        label = tk.Label(self, text="Built Profiles", font=controller.title_font)
        label.pack(side="top", fill="x", pady=10)

        label2 = tk.Label(self, text="Double click a built profile to generate graph.\n Note: You will not be able to select chrome and background")
        label2.pack(side="top", fill="x", pady=10)
        
        self.bind("<<ShowFrame>>", self.on_show_frame)

        self.listbox = tk.Listbox(self, height = 10,
                  width = 25,
                  bg = "light grey",
                  activestyle = 'dotbox',
                  font = "Helvetica 25",
                  fg = "black")


        self.listbox.bind('<Double-1>', self.go)
        self.listbox.pack()

        button = tk.Button(self, text="Back to Start Page",
            highlightbackground='black', height= 5, width=12,
            command=lambda: controller.show_frame("StartPage"))
        button.pack(anchor="s", side="left")
    
    def on_show_frame(self, event):
        self.listbox.delete(0,tk.END)
        for values in os.listdir(f"{current_path}/ip_profiles"):
            if values[-3:] == "csv":
                self.listbox.insert(tk.END, values[:-4])

    def go(self, event):
        cs = self.listbox.curselection()
        # Updating label text to selected option
        selected_name = f"{self.listbox.get(cs)}.csv"
        log.info(f"Making graph for profile: {selected_name}")
        make_individual_charts(selected_name, log)
        
class WarningPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        warning_label = tk.Label(self, text=f"WARNING this action will delete all your prior data\nThis action will delete your profiles and graphs", font="Times 20 bold", fg="dark red")
        warning_label.pack(side="top", fill="x", pady=10)
        
        report_button = tk.Button(self, text="Reset Folders", highlightbackground='black', height= 5, width=12,command=lambda: reset_folders())
        report_button.pack(pady=50)


        button = tk.Button(self, text="Back to Start Page",
            highlightbackground='black', height= 5, width=12,
            command=lambda: controller.show_frame("StartPage"))
        button.pack(anchor="s", side="left")

if __name__ == "__main__":
    app = SampleApp()
    app.geometry("800x550")
    app.mainloop()

