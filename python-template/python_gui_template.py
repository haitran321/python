#!/usr/bin/env python

from __future__ import division

from wx import *

import sys
from os import getcwd

import numpy as np
import scipy as sp
import matplotlib.pyplot as plt

from time        import sleep


class MyApp(wx.App):

    def OnInit(self):
       frame = MyFrame("App name here",(50, 60), (450, 300))
       frame.Show()
       self.SetTopWindow(frame)
       return True

class MyFrame(wx.Frame):

    def __init__(self, title ,pos, size):
        wx.Frame.__init__(self, None, -1, title, pos, size)
        menuFile = wx.Menu()
        menuFile.Append(1, "&About...")
        menuFile.AppendSeparator()
        menuFile.Append(2, "E&xit")
        menuBar = wx.MenuBar()
        menuBar.Append(menuFile, "&File")
        self.SetMenuBar(menuBar)
        self.CreateStatusBar()
        self.SetStatusText("Add text about this app here")
        self.Bind(wx.EVT_MENU, self.OnAbout, id=1)
        self.Bind(wx.EVT_MENU, self.OnQuit, id=2)

        # Add panel that spans the entire frame. Needed to put
        # buttons and stuff on.
        panel = wx.Panel(self)

        # Add user I/F controls to get LRID2TXT file name.
        x_pos = 10
        y_pos = 10
        y_size = 20

        # Add the static text and text box for LRID file name
        wx.StaticText(panel, -1, "Input LRID File:", pos=(x_pos, y_pos))

        # Add user I/F controls to get LRID file name.
        y_pos += y_size
        in_file_button = wx.Button(panel, label="Browse", pos=(x_pos+350,y_pos), size = (70,y_size))
        self.Bind(wx.EVT_BUTTON,self.OnBrowse,in_file_button)

        # Add the text box
        self.in_file_name = wx.TextCtrl(panel, -1, "", pos=(x_pos, y_pos), size=(340,y_size))

        # Add status text box
        y_pos += (2 * y_size)
        # Add the static text and text box for LRID file name
        wx.StaticText(panel, -1, "Status:", pos=(x_pos, y_pos))

        # Add button to start processing
        y_pos += y_size
        self.proc_status = wx.TextCtrl(panel, -1, "", pos=(x_pos, y_pos), size=(340,y_size))
        start_proc_button = wx.Button(panel, label="Start", pos=(x_pos+350,y_pos), size = (70,y_size))
        self.Bind(wx.EVT_BUTTON,self.OnStartProcessing,start_proc_button)

        # Add button to exit the application.
        y_pos += (3 * y_size)
        exit_button = wx.Button(panel, label="Exit", pos=(x_pos+350,y_pos), size = (70,y_size))
        self.Bind(wx.EVT_BUTTON,self.OnQuit,exit_button)


    def OnStartProcessing(self, event):

        print "Start processing here!"

        self.proc_status.SetValue("Started processing for an unkown amount of time...")
        app.Yield()

        # Add processing code here
        self.Processing()

        self.proc_status.SetValue("Finished!")

        print "Finished!\n\n"

    def OnBrowse(self, event):

        # print "Browse for file code here"
        def_dir = "C:/localLrid/"
        wildcard = "LRID File (*.lrid.txt)|*.lrid.txt|" \
                "All files (*.*)|*.*" 
        dialog = wx.FileDialog(
            None,
            "Choose an LRID file",
            def_dir, 
            "",
            wildcard,
            wx.OPEN
        ) 
        if dialog.ShowModal() == wx.ID_OK:
            # Get the filename the user browsed to.
            self.lrid_fname  = dialog.GetPath()
            # Display it in the text box.
            self.in_file_name.SetValue(self.lrid_fname)
        dialog.Destroy()
        self.lrid_txt_fname = self.lrid_fname + ".txt"
        print "Reading from LRID file: %s" % self.lrid_fname

    def OnQuit(self, event):

        self.Close()

    def OnAbout(self, event):
        wx.MessageBox("This is a wxPython Hello world sample", 
                "About Hello World", wx.OK | wx.ICON_INFORMATION, self)


    # Code for real processing
    def Processing (self):
        sleep(3)


# ---------------------------- Begin Main Program ----------------------------

if __name__ == '__main__' :

    # Create the the wxPython application
    app = MyApp(redirect=False)

    # Start the application main loop.
    app.MainLoop()

    # Finished
    sys.exit(0)

