import wx
import socket
from struct import *
import sys

# Simple wx window with menus
class MyMenu(wx.Frame):
    def __init__(self, parent, id, title):
        wx.Frame.__init__(self, parent, id, title, wx.DefaultPosition, wx.Size(700, 500))

        menubar = wx.MenuBar()

        self.bsCmd = 0
        self.tbrsHWSetupCmd = 0
        self.presetTBRSHWSetupCmd = ''
        self.zcu104WriteRegCmd = ''
        self.cmd = 0
        self.channelSimDelayCmd = ''
        self.rfGenCmd = ''

        self.LED_ON = 1
        self.LED_OFF = 0
        self.LED_REG = 1

        for i in range(0,34):
            self.presetTBRSHWSetupCmd += str(pack(">l" , 0))

        # Enum for selected command
        self.def_ReadRegCmd = 1
        self.def_RFGenCmd = 2
        self.def_BeamSteerCmd = 3
        self.def_ChannelSimDelayCmd = 4
        self.def_Mode = 5
        self.def_WarmRestart = 6
        self.def_SendExit = 7

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        self.mode_list = ['Offline', 'Mission', 'Test Assist']
        self.command_type_list = ['Read Reg Cmd', 'RF Gen Cmd', 'Beam Steer Cmd', 'Channel Sim Delay Cmd', 'Mode', 'Warm Restart', 'Send Exit']
        self.tbrs_hw_sig_gen_hw_setup_list = ['Off', 'Internal', 'External', 'BIT 1', 'BIT 2', 'BIT 3', 'BIT 4', 'BIT 5']
        self.ipaddress_list = ['ZCU104', 'ZCU208', 'Local']
        self.ipaddress_num_list = ['172.16.80.3', '172.16.80.8', '172.16.80.2']
        self.ipaddress = [[],[],[]]
        
        self.port_tbrsr = 9701
        self.port_tbrse = 6110
        self.port_wr = 6101
        self.port_local = 9012
        self.port_zcu = 3010
        self.data = 1

        # The 'file' menu
        file = wx.Menu()
        quit = wx.MenuItem(file, 105, '&Quit\tCtrl+Q', 'Quit the document')
        file.Append(quit)

        # Add event handler
        # wx.EVT_MENU(self, 105, self.OnQuit )
        self.Bind(wx.EVT_MENU, self.OnQuit)

        menubar.Append(file, '&File')
        self.SetMenuBar(menubar)
        self.CreateStatusBar()

        # Add pannel
        panel = wx.Panel(self, -1)

        # Add check boxes for IP Address
        for i in range (0, len(self.ipaddress_list), 1):
            self.ipaddress[i] = wx.CheckBox(panel, 27 + i, self.ipaddress_list[i], (20 + (i*80), 20))

        # Set check boxes default values
        self.ipaddress[0].SetValue(True)
        self.ipaddress[1].SetValue(True)

        # Add list box
        self.report_type = wx.ListBox(panel, 26, (20, 40), (105, 100), self.command_type_list, wx.LB_SINGLE)

        # Add mode list box
        self.mode_input = wx.ListBox(panel, 50, (150, 40), (100, 100), self.mode_list, wx.LB_SINGLE)

        # Add texts
        wx.StaticText(panel, -1, "TBRS HW Setup Info", pos = (370, 20))
        wx.StaticText(panel, -1, "Sig. Gen. Select:", pos = (300, 35))
        wx.StaticText(panel, -1, "Attenuation (0-127):", pos = (450, 35))

        # Add HW setup list box
        self.sig_gen_hw_setup_input = wx.ListBox(panel, 50, (300, 50), (100, 110), self.tbrs_hw_sig_gen_hw_setup_list, wx.LB_SINGLE)

        # Add Atten input box
        self.sig_gen_atten_input = wx.TextCtrl(panel, -1, "30", pos=(450, 50), size=(35,20))

        # Set list box default value
        self.report_type.SetSelection(3)

        # Add send button
        self.SendButton = wx.Button(panel, 2, 'Send', (20, 300))

        # Add event on send button
        self.SendButton.Bind(wx.EVT_BUTTON, self.EventSendButton, id = 2)

        # Add quit button
        self.QuitButton = wx.Button(panel, 3, 'Quit', (120, 300))

        # Add event on send button
        self.QuitButton.Bind(wx.EVT_BUTTON, self.OnQuit, id = 3)

        # Add texts
        wx.StaticText(panel, -1, "LED3 Test:", pos = (20, 200))

        # Add LED3 Turn On button
        self.LED3OnButton = wx.Button(panel, 2, 'On', (20, 220))

        # Add event on LED3 Turn On button
        self.LED3OnButton.Bind(wx.EVT_BUTTON, self.EventLED3OnButton)

        # Add LED3 Turn Off button
        self.LED3OffButton = wx.Button(panel, 2, 'Off', (120, 220))

        # Add event on LED3 Turn Off button
        self.LED3OffButton.Bind(wx.EVT_BUTTON, self.EventLED3OffButton)

    def OnQuit(self, event):
        self.Close()

    def EventSendButton (self, event):
        self.data = self.report_type.GetSelection() + 1

        # Get data
        if self.data == self.def_ReadRegCmd:
            data = self.GenReadRegCmd()
            # port = 3030
            port = 3010
        if self.data == self.def_RFGenCmd:
            data = self.GenRFGenCmd()
            port = self.port_zcu
        if self.data == self.def_BeamSteerCmd:
            data = self.GenBSCmd()
            port = self.port_tbrsr
        if self.data == self.def_ChannelSimDelayCmd:
            data = self.GenChannelSimDelayCmd()
            port = self.port_zcu
        if self.data == self.def_Mode:
            data = self.GenModeCmd()
            port = self.port_tbrse
        if self.data == self.def_WarmRestart:
            data = self.GenWRCmd()
            port = self.port_zcu
        if self.data == self.def_SendExit:
            data = self.GenSendExitCmd()
            port = self.port_local
                    
        # Send data
        for i in range (0, len(self.ipaddress_list), 1):
            if self.ipaddress[i].GetValue():
                self.sock.sendto(data, (self.ipaddress_num_list[i], port))
                print ("send: %s to %s" % (data, self.ipaddress_num_list[i]))

    def EventLED3OnButton (self, event):
        print ("in led3 on event handler")
        data = self.MPSoCLED(self.LED_REG, self.LED_ON)
        port = self.port_zcu
        # Send data
        for i in range (0, len(self.ipaddress_list), 1):
            if self.ipaddress[i].GetValue():
                self.sock.sendto(data, (self.ipaddress_num_list[i], port))
                print ("send: %s to %s" % (data, self.ipaddress_num_list[i]))

    def EventLED3OffButton (self, event):
        data = self.MPSoCLED(self.LED_REG, self.LED_OFF)
        port = self.port_zcu
        # Send data
        for i in range (0, len(self.ipaddress_list), 1):
            if self.ipaddress[i].GetValue():
                self.sock.sendto(data, (self.ipaddress_num_list[i], port))
                print ("send: %s to %s" % (data, self.ipaddress_num_list[i]))
    

    def GenBSCmd(self):
        self.bsCmd = 1
        msgID = 1
        pbpID = 100
        msgLen = 32
        msgTime1 = 0
        msgTime2 = 0
        numRecord = 0
        recordLen = 0
        recvID = 2
        self.bsCmd = pack(">llllllll" , msgID, pbpID, msgLen, msgTime1, msgTime2, numRecord, recordLen ,recvID)
        return self.bsCmd

    def GenTBRSHWSetupCmd(self):
        self.tbrsHWSetupCmd = 1
        msgID = 105
        pbpID = 1
        msgLen = 32 + 144
        msgTime1 = 0
        msgTime2 = 0
        numRecord = 1
        recordLen = 144
        recvID = 1
        self.tbrsHWSetupCmd = pack(">llllllllll" , msgID, pbpID, msgLen, msgTime1, msgTime2, numRecord, recordLen ,recvID, \
                                   self.sig_gen_hw_setup_input.GetSelection(), int(self.sig_gen_atten_input.GetValue())) + self.presetTBRSHWSetupCmd
        return self.tbrsHWSetupCmd

    def GenChannelSimDelayCmd(self):
        self.channelSimDelayCmd = 1
        msgID = 1401
        pbpID = 100
        msgLen = 32 + (7*4)*1
        msgTime1 = 0
        msgTime2 = 0
        numRecord = 1
        recordLen = 7*4
        recvID = 0
        # Pack header
        self.channelSimDelayCmd = pack(">llllllll" , msgID, pbpID, msgLen, msgTime1, msgTime2, numRecord, recordLen ,recvID)

# int startTime;
# int stopTime;    
# int amplitude;
# int timeDelay;    
# int phaseOffset;

        startTime = 0x3E8
        stopTime = 0xBB8    
        amplitude = 0xFFF
        timeDelay = 0x2710    
        phaseOffset = 0

        # Pack action 1
        chId = 0
        self.channelSimDelayCmd += pack(">lllllll" , 101, chId, startTime, stopTime, amplitude, timeDelay, phaseOffset)     
        # Pack action 2
        chId = 1
        self.channelSimDelayCmd += pack(">lllllll" , 102, chId, 0x2001, 0x3001, 0x201, 0x101, 0x501)  
        # Pack action 3
        chId = 1
        self.channelSimDelayCmd += pack(">lllllll" , 103, chId, 0x2002, 0x3002, 0x202, 0x102, 0x502)  
        # Pack action 4
        chId = 0
        self.channelSimDelayCmd += pack(">lllllll" , 104, chId, 0x2003, 0x3004, 0x203, 0x103, 0x503)  

        return self.channelSimDelayCmd   

    def GenRFGenCmd(self):     
        self.rfGenCmd = 1
        msgID = 1402
        pbpID = 100
        msgLen = 32 + (11*4)*1
        msgTime1 = 0
        msgTime2 = 0
        numRecord = 1
        recordLen = 11*4
        recvID = 0
        # Pack header
        self.rfGenCmd = pack(">llllllll" , msgID, pbpID, msgLen, msgTime1, msgTime2, numRecord, recordLen ,recvID)

        receiveID = 101
        chId = 0
        sid = 11111
        startTime = 0x3E8
        stopTime = 0xBB8    
        amplitude = 0x100 
        phaseOffset = 0
        freq = 0x02222222
        lfm = 0x0
        phaseCode = 0x0
        spare = 0

        # Pack action 1
        self.rfGenCmd += pack(">lllllllllll" , receiveID, chId, sid, startTime, stopTime, amplitude, phaseOffset, freq, lfm, phaseCode, spare)     

        return self.rfGenCmd

    def GenModeCmd(self):
        modeCmd = 0
        msgID = 101
        pbpID = 100
        msgLen = 48
        msgTime1 = 0
        msgTime2 = 0
        numRecord = 1
        recordLen = 16
        recvID = 0
        mode = self.mode_input.GetSelection() + 1
        if mode == 0:
            # default mode to offline
            mode = 1
        lissState = 1
        opState = 1
        simInt = 0
        modeCmd = pack(">llllllllllll" , msgID, pbpID, msgLen, msgTime1, msgTime2, numRecord, recordLen ,recvID, mode, lissState, opState, simInt)
        return modeCmd

    def GenWRCmd(self):
        self.cmd = 1
        msgID = 102
        pbpID = 111
        msgLen = 36
        msgTime1 = 0
        msgTime2 = 0
        numRecord = 0
        recordLen = 0
        recvID = 0
        type = 1
        self.cmd = pack(">lllllllll" , msgID, pbpID, msgLen, msgTime1, msgTime2, numRecord, recordLen ,recvID, type)
        return self.cmd

    def MPSoCLED(self, reg, val):
        return self.GenWriteRegCmd(reg, val)

    def GenReadRegCmd(self):
        self.cmd = 1
        msgID = 2001
        pbpID = 0
        msgLen = 40
        msgTime1 = 0
        msgTime2 = 0
        numRecord = 0
        recordLen = 0
        recvID = 0
        # reg = 1
        # val = 1
        self.cmd = pack(">llllllll" , msgID, pbpID, msgLen, msgTime1, msgTime2, numRecord, recordLen ,recvID)
        return self.cmd  
        #     
        # Temporary uses for timing trigger msg test
        # self.cmd = 1
        # self.cmd = pack("<ll" , 1, 0)
        return self.cmd    

    def GenWriteRegCmd(self, reg, val):
        self.cmd = 1
        msgID = 2002
        pbpID = 0
        msgLen = 40
        msgTime1 = 0
        msgTime2 = 0
        numRecord = 0
        recordLen = 0
        recvID = 0
        reg = reg
        val = int(val)
        self.cmd = pack("<llllllllll" , msgID, pbpID, msgLen, msgTime1, msgTime2, numRecord, recordLen ,recvID, reg, val)
        return self.cmd    

    def GenSendExitCmd(self):
        self.cmd = "exit"
        return self.cmd

class MyApp(wx.App):
    def OnInit(self):
        frame = MyMenu(None, -1, 'RIMS Emulator.py')
        frame.Show(True)
        return True

app = MyApp(0)
app.MainLoop()
