#!/usr/bin/env python

from __future__ import division

import wx

import sys
from os import getcwd
from os import walk

import numpy as np
import scipy as sp
import matplotlib.pyplot as plt

from time        import sleep

import shutil

class MyApp(wx.App):

    def OnInit(self):
       frame = MyFrame("List of Files Template",(50, 60), (450, 260))
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
        self.SetStatusText("List of File Template")
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
        self.in_file_path = wx.TextCtrl(panel, -1, "", pos=(x_pos, y_pos), size=(340,y_size))

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

        print ("Start processing here!")

        self.proc_status.SetValue("Started processing for an unkown amount of time...")
        app.Yield()

        # Add processing code here
        self.Processing()

        self.proc_status.SetValue("Finished!")

        print ("Finished!\n\n")

    def OnBrowse(self, event):

        # print "Browse for file code here"
        def_dir = "E:/Eglin/CSPU/LRID/Site/Aug2013/Soak_Data_for_DR04/"
        wildcard = "Log File (*.*)|*.*|" \
                "All files (*.*)|*.*" 
        dialog = wx.DirDialog(
            None,
            "Choose a directory:",
            style=wx.DD_DEFAULT_STYLE | wx.DD_CHANGE_DIR
        ) 
        if dialog.ShowModal() == wx.ID_OK:
            self.filePath = ''
            self.fileList = []
            self.in_file_path = ''
            # Get the filename the user browsed to.
            self.filePath  = dialog.GetPath()
            tree = walk(dialog.GetPath()) # Walk the current directory

            # Put the twgs filenames in a list
            file_to_save = 'output'
            for dir in tree:
                # print dir
                if dir[0] != '': # Just the top directory
                    for file in dir[2]:
                        print (file)
                        if (file[:4] == file_to_save):
                            self.fileList.append(file)
        # Display it in the text box.
        self.in_file_path.SetValue(dialog.GetPath())
        dialog.Destroy()

    def OnQuit(self, event):

        self.Close()

    def OnAbout(self, event):
        wx.MessageBox("This is a wxPython Hello world sample", 
                "About Hello World", wx.OK | wx.ICON_INFORMATION, self)


    # Code for real processing
    def Processing (self):

        for file_index in range(0, len(self.fileList)):

            print ("Processing %s" % self.fileList[file_index])

# ---------------------------- Begin Main Program ----------------------------

if __name__ == '__main__' :

    # Create the the wxPython application
    app = MyApp(redirect=False)

    # Start the application main loop.
    app.MainLoop()

    # Finished
    sys.exit(0)

