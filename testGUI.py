import tkinter as tk


class TestWindow(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self._frame = None
        self.Switch_frame(StartPage)

    def Switch_frame(self, frame_class):
        new_page = frame_class(self)
        if self._frame:
            self._frame.destroy()
        self._frame = new_page
        self._frame.pack()


class StartPage(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        tk.Label(master=self, bg='blue', text='label_1').pack()
        tk.Button(master=self, bg='grey', text='switch to page 2', command=lambda: master.Switch_frame(SecondPage)).pack()


class SecondPage(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        tk.Label(self, bg='red', text='label_2').pack()
        tk.Button(self, bg='grey', text='switch to page 1', command=lambda: master.Switch_frame(StartPage)).pack()


app = TestWindow()
app.mainloop()



import tkinter as tk
import subprocess