'''
Created by Aiden Chang

GUI pased off of the python tkinter package. Uses functionality from get_traces
Built for virtual environment. 

To start venv, cd into comps directory and type source bin/activate
Required packages:
    All the packages stated in requirements.txt

WARNING:
    Some m1 modules will Virtual environments might have issues with tkinter

Developed by: Aiden Chang, Jeylan Jones
Last Updated: 1/28/2022 at 12:00 PM by Aiden Chang
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





#importing trace functions
# from get_traces import *

current_path = os.path.dirname(os.path.abspath(__file__))
PLACEHOLDER = None
BACKGROUND_BUILT = False

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
        for F in (StartPage, InstructionsPage, BackgroundPage, ProfilePage, UploadTracePage, AboutPage, BuiltProfilePage):
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
        # frame.winfo_toplevel().geometry("")
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
        button5 = tk.Button(self, text="About", highlightbackground='black', height= 5, width=10,
                            command=lambda: controller.show_frame("AboutPage"))
        button6 = tk.Button(self, text="Quit", highlightbackground='black', height= 5, width=10, 
                            command=controller.destroy)
        # button5 = tk.Button(self, text="Exit", command=self.destroy)
        button1.pack()
        button2.pack()
        button3.pack()
        button4.pack()
        button7.pack()
        button5.pack(anchor="s", side="right")
        button6.pack(anchor="s", side="left")
        


class InstructionsPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        label = tk.Label(self, text="Instructions", font=controller.title_font)
        label.pack(side="top", fill="x", pady=10)
        button = tk.Button(self, text="Back to Start Page",
            highlightbackground='black', height= 5, width=12,
            command=lambda: controller.show_frame("StartPage"))
        button.pack(anchor="s", side="left")


class BackgroundPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.number_of_trace = 0 # need to get the correct number of these
        self.timeout = 60 # need to change this

        label = tk.Label(self, text="Tracing Computer Background", font=controller.title_font)
        label.pack(side="top", fill="x", pady=10)
        
        warning_label = tk.Label(self, text=f"WARNING please close all other apps and bluetooth for the best results", font="Times 20 bold", fg="dark red")
        warning_label.pack(side="top", fill="x", pady=10)

        dt_m = "Not built"
        if os.path.exists(f"{current_path}/ip_profiles/background.csv"):
            dt_m = datetime.datetime.fromtimestamp(os.path.getmtime(f"{current_path}/ip_profiles/background.csv"))
        self.last_background_built = tk.Label(self, text=f"Last Background Build: {dt_m}", font="Times 16 bold", fg="dark blue")
        self.last_background_built.pack(side="top", fill="x", pady=10)

        refresh_button = tk.Button(self, text="refresh",
            command=lambda:self.refresh())
        refresh_button.pack(side="top", pady=10)

        label = tk.Label(self, text=f"Enter timeout (recommended: {self.number_of_trace})")
        label.pack(side="top", fill="x", pady=10)
        self.inputtxt = tk.Text(self,
                        height = 3,
                        width = 20)
        
        self.inputtxt.pack()


        background_button = tk.Button(self, text="Start Background Trace",
            highlightbackground='black', height= 5, width=12,
            command=lambda:self.start_background_process())

        button = tk.Button(self, text="Back to Start Page",
            highlightbackground='black', height= 5, width=12,
            command=lambda: controller.show_frame("StartPage"))
        background_button.pack(side="top", pady=10)
        button.pack(anchor="s", side="left")

    
    def build_background_on_thread(self, timeout : int) -> None:

        self.label1 = tk.Label(self, text="Building background in process...")
        self.label1.pack(side="top", fill="x", pady=10)
        try:
            # install_chromedriver()
            # build_background_profile(timeout)
            # build_chrome_profile(timeout)
            global BACKGROUND_BUILT
            BACKGROUND_BUILT = True
            self.label1.config(text="Done Building Background Profile")
        except Exception as e:
            self.label1.config(text="Error in building background profile, please check error message")
            print(e)

    def start_background_process(self) -> None:
        inp = self.inputtxt.get(1.0, "end-1c")
        if inp and inp.isdigit():
            self.timeout = int(inp)
        newthread = threading.Thread(target=self.build_background_on_thread, args = (self.timeout,))
        newthread.start()
    
    def refresh(self) -> None:
        if os.path.exists(f"{current_path}/ip_profiles/background.csv"):
            dt_m = datetime.datetime.fromtimestamp(os.path.getmtime(f"{current_path}/ip_profiles/background.csv"))
            self.last_background_built.config(text = f"Last Background Build: {dt_m}")
        


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

        refresh_button = tk.Button(self, text="refresh",
            command=lambda:self.refresh())
        refresh_button.pack(side="top", pady=10)


        # TextBox Creation
        self.inputtxt = tk.Text(self,
                        height = 3,
                        width = 40)
        
        self.inputtxt.pack()

        # Button Creation
        printButton = tk.Button(self,
                                text = "Build website", 
                                command = lambda:self.build_website_background(), height= 5, width=12)
        printButton.pack(side="top", pady=10)

        
        self.lbl = tk.Label(self, text = "")
        self.lbl.pack()

        self.build_background_label = tk.Label(self, text="Please build background first")
        self.build_background_label.pack(side="top", fill="x", pady=10)
 
    
        button = tk.Button(self, text="Back to Start Page",
            highlightbackground='black', height= 5, width=12,
            command=lambda: controller.show_frame("StartPage"))
        button.pack(anchor="s", side="left")
    
    def refresh(self) -> None:
        if os.path.exists(f"{current_path}/ip_profiles/background.csv"):
            dt_m = datetime.datetime.fromtimestamp(os.path.getmtime(f"{current_path}/ip_profiles/background.csv"))
            self.last_background_built.config(text = f"Last Background Build: {dt_m}")


    def build_website_background(self) -> None:
        inp = self.inputtxt.get(1.0, "end-1c")
        self.lbl.config(text = "Selected Website: "+inp)
        domain = urlparse(inp).netloc
        if BACKGROUND_BUILT and inp and domain:
            try:
                self.build_background_label.config(text = f"Building website background for {inp}\nName: {domain}")

                # newthread = threading.Thread(target=build_profile_without_noise, args = (20,inp,domain))
                # newthread.start()
            except Exception as e:
                self.build_background_label.config(text = f"something went wrong in building website profile, please check log files")
                print(f"Failed with exception {e}")
        else:
            self.build_background_label.config(text = "Background not built yet")
            if BACKGROUND_BUILT:
                self.build_background_label.config(text = "Background is built, incorrect format with input website. Exmp: https://open.spotify.com/")






# #User uploads pcap and pcapng files to UploadTraces Page
# def UploadPcap(self, pkt=None) -> None:
#         filename = filedialog.askopenfilename(title="Choose a File...", filetypes=(('Pcap Files', '.pcap .pcapng' ),))
#     #get file pathway
#         global PLACEHOLDER
#         PLACEHOLDER = filename
#         label = tk.Label(self, text=f"Chosen: {filename}")
#         label.pack(side="top", fill="x", pady=10)
# #         file = open(str(filename), 'rb')
# #         print(str(file))
# #         translate = str(file)
# #         id1 = translate.index("=")
# #         id2 = translate.index("'>")
# #         path = ''
# #         for i in range(id1 + len("=") + 1, id2):
# #             path = path + translate[i]
# #     #open new directory for uploaded traces``
# #         if filename:
# #             NEWDIR = (f"Uploaded Traces")
# #             if not os.path.isdir(NEWDIR):
# #                 os.makedirs(NEWDIR)
# # #copies file from user's directory into Uploaded Traces folder
# #         with open(f"Uploaded Traces/{os.path.basename(str(filename))}",'w') as f:
# #             shutil.copy(path, NEWDIR)
# #         file_label = tk.Label(text=str(os.path.basename(str(filename))))
# #         file_label.place(relx = 0.5, rely = 0.5, anchor ='center')




class UploadTracePage(tk.Frame):
            
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        label = tk.Label(self, text="Upload Trace Here!", font=controller.title_font)
        label.pack(side="top", fill="x", pady=10)
        upload_button = tk.Button(self, text="Choose a File...", command=lambda:self.UploadPcap())
        upload_button.pack()

        report_button = tk.Button(self, text="Generate Report", command=lambda:self.UploadPcap())
        report_button.pack()

        back_button = tk.Button(self, text="Back to Start Page",
            highlightbackground='black', height= 5, width=12,
            command=lambda: controller.show_frame("StartPage"))
        back_button.pack(anchor="s", side="left")
        
     #def display_graph(self):
        #for graphs in os.listdir(f"{current_path}/bar_charts"):
            #newWindow = tk.Toplevel(self)
            #newWindow.title((current_path) + "/bar_charts/" + graphs)
            #newWindow.geometry("600x500")

            #pic = Image.open(os.path.join(f"{current_path}/bar_charts/", graphs))
            #resized = pic.resize((600, 450))
            #graph = ImageTk.PhotoImage(resized)

            #graph_label = tk.Label(newWindow, image = graph)
            #graph_label.image = graph
            #graph_label.place(anchor='center', relx=0.5, rely=0.5)

    #User uploads pcap and pcapng files to UploadTraces Page
    def UploadPcap(self, pkt=None) -> None:
            filename = filedialog.askopenfilename(title="Choose a File...", filetypes=(('Pcap Files', '.pcap .pcapng' ),))
            global PLACEHOLDER
            PLACEHOLDER = filename
            label = tk.Label(self, text=f"Chosen: {filename}")
            label.pack(side="top", fill="x", pady=10)
    
    def start_report(self) -> None:
        self.label1 = tk.Label(self, text="Building report in progress...")
        self.label1.pack(side="top", fill="x", pady=10)
        if PLACEHOLDER != None:
            newthread = threading.Thread(target=generateReport)
            newthread.start()
        else:
            self.label1.config(text="File not selected")



    def generateReport(self) -> None:
        for values in os.listdir(f"{current_path}/ip_profiles"):
            if values[-3:] == "csv":
                profile_name = values[:-4]
                matches = check_website_in_noisy_trace(PLACEHOLDER, profile_name)
                report = report_to_user(profile_name, matches)
                print(report)
        self.label1.config(text="Generated Report")





class AboutPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        label = tk.Label(self, text="About This Project", font=controller.title_font)
        label.pack(side="top", fill="x", pady=10)
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


        listbox = tk.Listbox(self, height = 10,
                  width = 25,
                  bg = "light grey",
                  activestyle = 'dotbox',
                  font = "Helvetica 25",
                  fg = "black")

        for values in os.listdir(f"{current_path}/ip_profiles"):
            if values[-3:] == "csv":
                listbox.insert(tk.END, values[:-4])

        listbox.pack()

        button = tk.Button(self, text="Back to Start Page",
            highlightbackground='black', height= 5, width=12,
            command=lambda: controller.show_frame("StartPage"))
        button.pack(anchor="s", side="left")



if __name__ == "__main__":
    app = SampleApp()
    app.geometry("800x500")
    app.mainloop()

