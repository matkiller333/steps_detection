import tkinter as tk
import tkinter.ttk as ttk
import subprocess
from tkinter import filedialog as fd
from PIL import Image, ImageTk
from moviepy.editor import *
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from calculations import *


def Process(path, csv=0):       # Command that is executed to launch the video processing
    start = str(app.main_box.frame['VideoFrame'].start_time.get())  # gets start time from the sliders in video frame
    end = str(app.main_box.frame['VideoFrame'].end_time.get())  # same with end time
    print(path)

    command = 'python commands.py --process --write_graph' + ' --start ' + start + ' --end ' + end  # base command
    if csv:         # If this option is activated, it will write the keypoints as a CSV
        command = command + ' --write_csv '

    command = command + ' ' + path  # Adds the path at the end
    print(command)                  # For test purposes
    subprocess.call(command)
    Switch_to('graphs')


def Switch_to(location):            # makes sure all concerned frames are switched
    if location == 'graphs':
        app.main_box.Switch_frame(frame_class=GraphsFrame)
        app.side.Switch_frame(frame_class=SideGraphMenu)
    elif location == 'video':
        app.main_box.Switch_frame(frame_class=VideoFrame)
        app.side.Switch_frame(frame_class=SideVideoMenu)


def Load_video(path):
    Switch_to('video')         # Makes sure the video frame is initialized
    clip = VideoFileClip(path)  # loads clip
    max_time = int(clip.duration)
    frames = []
    for i in range(max_time):
        clip.save_frame('assets\\temp_frame.png', t=i)  # saves the frame at time i as a png
        frames.append(tk.PhotoImage(file='assets\\temp_frame.png'))  # loads said png
    # sends the resulting frames to a receiver function in VideoFrame
    app.main_box.frame["VideoFrame"].Receiver(frames, max_time)


# Main window containing everything
class MainWindow(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.side = Display(self, SideVideoMenu, SideGraphMenu)
        self.side.grid(row=2, column=2)
        self.main_box = Display(self, VideoFrame, GraphsFrame)
        self.main_box.grid(row=2, column=0)
        self.top_menu = TopMenu(self)
        self.top_menu.grid(row=0, column=0, columnspan=5, sticky=tk.EW)

        ttk.Separator(self, orient=tk.VERTICAL).grid(row=1, column=1, sticky=tk.NS)
        ttk.Separator(self, orient=tk.HORIZONTAL).grid(row=1, column=0, columnspan=2, sticky=tk.EW)


# Display template with the option to change frame
class Display(tk.Frame):
    def __init__(self, master, start_class, *args):
        tk.Frame.__init__(self, master) # The master is the window in which the object (of class display) will be packed
        start_name = str(start_class).split('.')[1].split("'")[0]
        self.frame = {start_name: start_class(self)}  # Declare self.frame as a dict. so you can access the wanted
        self.frame[start_name].grid(row=0, column=0)  # frame depending on the name provided for the switch_frame
                                                      # function
        for i in args:  # Initialises all menus other than start_class
            name = str(i).split('.')[1].split("'")[0]       # Gets the name of the desired class for the frame
            self.frame[name] = i(self)
            self.frame[name].grid(row=0, column=0)
#        for key, values in self.frame.items():
#            print('key: ', key, 'value: ', values)
        self.Switch_frame(start_class)

    def Switch_frame(self, frame_class):
        name = str(frame_class).split('.')[1].split("'")[0]
        self.frame[name].tkraise()


# Frame option for the side menu which contains the options for processing the video/data
class SideVideoMenu(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master, bg='#3C3F41', width=305, height=720)
        self.grid_propagate(0)

        # Video path section
        tk.Label(self, bg='#3C3F41', fg='white', text='Enter the video path').grid(row=0, column=0, columnspan=2)
        self.directory = tk.StringVar()
        self.path = tk.Entry(self, bg='grey', fg='white', width=47, textvariable=self.directory)  # text box
        self.path.grid(row=1, column=0, columnspan=2, sticky=tk.W)
        tk.Button(self, bg='grey', fg='white', text='load',
                  command=lambda: Load_video(self.directory.get())).grid(row=2, column=1)  # load button
        tk.Button(self, bg='grey', fg='white', text='auto fill',  # auto fill button
                  command=lambda: self.Set_text('..\\examples\\personal\\video_test2.mp4')).grid(row=2, column=0)
        self.photo = tk.PhotoImage(file='assets\\icons\\folder.png').subsample(50, 50)
        tk.Button(self, image=self.photo, command=lambda: self.Open_file()).grid(row=1, column=2, sticky=tk.SE)

        # Options section
        ttk.Separator(self, orient=tk.HORIZONTAL).grid(row=3, column=0, columnspan=3, sticky=tk.EW)
        self.csv = tk.IntVar()
        tk.Checkbutton(self, bg='grey', fg='white', text='Write CSV', variable=self.csv).grid(row=4, sticky=tk.EW)
        tk.Radiobutton(self, )

        # process button
        self.process_but = tk.Button(self, bg='grey', fg='white', text='process', state=tk.DISABLED,
                                     command=lambda: Process(self.directory.get(), self.csv.get()))
        self.process_but.grid(row=5, column=0, columnspan=2)

    def Set_text(self, text):
        self.directory.set(text)

    def Make_active(self):  # makes the process button active, called after the video has been loaded
        self.process_but.config(state=tk.ACTIVE)

    def Open_file(self):
        self.directory.set(fd.askopenfilename())


class SideGraphMenu(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master, bg='#3C3F41', width=305, height=720)
        self.grid_propagate(0)

        # Focus section
        self.graph_menu = tk.Menubutton(self, text='Select focus', bg='grey', fg='white')
        self.graph_menu.grid()
        self.graph_menu.menu = tk.Menu(self.graph_menu, tearoff=0)
        self.graph_menu['menu'] = self.graph_menu.menu
        self.graph_menu.menu.add_command(label='all 5', command=lambda: self.SwitchGraphs(9))
        self.graph_menu.menu.add_command(label='ankle', command=lambda: self.SwitchGraphs(0))
        self.graph_menu.menu.add_command(label='knee', command=lambda: self.SwitchGraphs(1))
        self.graph_menu.menu.add_command(label='hip', command=lambda: self.SwitchGraphs(2))
        self.graph_menu.menu.add_command(label='shoulder', command=lambda: self.SwitchGraphs(3))
        self.graph_menu.menu.add_command(label='elbow', command=lambda: self.SwitchGraphs(4))

    def SwitchGraphs(self, choice):
        app.main_box.frame["GraphsFrame"].FetchGraph(choice)


# Frame option for MainDisplay that shows the video preview
class VideoFrame(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master, width=1040, height=720)
        self.grid_propagate(0)
        self.holder = tk.Label(self, bg='#313335', fg='white', width=1040, height=670)
        self.holder.grid(row=0, column=0, columnspan=2)

        # Creates variables for sliders
        self.start_time = tk.IntVar(0)
        self.end_time = tk.IntVar(0)
        self.preview = 0

    # scales to input start and end time of the section to analyze
    def Create_scales(self):
        self.holder.config(image=self.preview[self.start_time.get()])  # Sets the first image
        self.holder.image = self.preview[self.start_time.get()]  # anchors the image
        # start time widgets
        ttk.Scale(self, orient=tk.HORIZONTAL, var=self.start_time, from_=self.start_time.get(), to=self.end_time.get(),
                  command=self.Update_image).grid(row=1, column=0, sticky=tk.W)
        tk.Entry(self, textvariable=self.start_time, width=4).grid(row=1, column=0)
        # End time widgets
        ttk.Scale(self, orient=tk.HORIZONTAL, var=self.end_time, from_=self.start_time.get(), to=self.end_time.get(),
                  command=self.Update_image).grid(row=1, column=1, sticky=tk.E)
        tk.Entry(self, textvariable=self.end_time, width=4).grid(row=1, column=1)

#        tk.Button(self, bg='red', fg='white', command=lambda: print(self.end_time.get())).grid(row=1, column=0)

    # receives information from Load_video and stores it in a variable inside the object
    def Receiver(self, frames, max_time):
        self.preview = frames
        self.end_time.set(max_time)
        self.Create_scales()
        app.side.frame["SideVideoMenu"].Make_active()

    # Displays a new image in the Label
    def Update_image(self, time):
        self.holder.config(image=self.preview[int(round(float(time)))])
        self.holder.image = self.preview[int(round(float(time)))]


# Frame option for MainDisplay that shows the graphs
class GraphsFrame(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master, bg='grey', relief='ridge', width=1040, height=720)
        self.grid_propagate(0)  # ensures the Frame does not let its slaves define its size
        self.asset = 0
        self.FetchGraph(9)
        self.graph = tk.Label(self, image=self.asset)  # anchors the graph a first time
        self.graph.image = self.asset  # uses the anchor to display the graph (don't ask why it works) REQUIRED
        self.graph.grid(row=2)

    def FetchGraph(self, choice):  # Gets the graph from matplotlib in output directory
        if choice == 9:
            self.asset = tk.PhotoImage(file='output\\matplotlib\\temp_graph.png')
        else:
            name = 'output\\matplotlib\\temp_graph_'+str(choice)+'.png'
            self.asset = tk.PhotoImage(file=name)
        try: self.graph         # Prevents first time setup error as self.graph is not defined the first time this
        except: return          # function is called
        self.graph.config(image=self.asset)


# top menu for options
class TopMenu(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master, bg='#3C3F41')
        top = tk.Menubutton(self, text='settings', relief=tk.RIDGE, bg='#3C3F41', fg='white')
        top.grid(row=0, column=0, columnspan=2)
        top.menu = tk.Menu(top, tearoff=0)
        top["menu"] = top.menu
        top.menu.add_command(label='Switch to graphs', command=lambda: Switch_to('graphs'))
        top.menu.add_command(label='Switch to video', command=lambda: Switch_to('video'))


app = MainWindow()
app.title('Step Counting Application')
app.mainloop()
