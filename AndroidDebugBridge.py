#!/bin/python

"""
Android Debug Bridge automator
Author: Samuel Joyce
Organisation: company Ltd
Purpose: Provides quick access to Android Debug Brige functions and development tools. It allows a user to keep many Android phones plugged in at once.
All files downloaded go to C:/ADBScripts
"""

import wx, subprocess, re, os, urllib, time, json, urllib3, requests, webbrowser, shutil
from threading import Thread
from urllib import request
from requests.auth import HTTPBasicAuth


########################################################################
class LoginDialog(wx.Dialog):
    """
    Class to define login dialog
    """

    moduser, modpassword, devuser, devpass = "asd", "qwe", "asd", "qwe"

    # ----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        wx.Dialog.__init__(self, None, title="Credential Setup")

        # user info
        user_sizer = wx.BoxSizer(wx.HORIZONTAL)

        user_lbl = wx.StaticText(self, label="Mod Name:")
        user_sizer.Add(user_lbl, 0, wx.ALL | wx.CENTER, 5)
        self.user = wx.TextCtrl(self)
        self.user.Bind(wx.EVT_TEXT, self.updateacc)

        user_sizer.Add(self.user, 0, wx.ALL, 5)

        # pass info
        p_sizer = wx.BoxSizer(wx.HORIZONTAL)

        p_lbl = wx.StaticText(self, label="Mod Password:")
        p_sizer.Add(p_lbl, 0, wx.ALL | wx.CENTER, 5)
        self.password = wx.TextCtrl(self, style=wx.TE_PASSWORD | wx.TE_PROCESS_ENTER)
        p_sizer.Add(self.password, 0, wx.ALL, 5)

        # dev_lbl = wx.StaticText(self, label="Development Name:")
        # dev_sizer.Add(dev_lbl, 0, wx.ALL | wx.CENTER, 5)
        self.user = wx.TextCtrl(self)
        self.user.Bind(wx.EVT_TEXT, self.updateacc)

        p_lbl = wx.StaticText(self, label="Development Password:")
        p_sizer.Add(p_lbl, 0, wx.ALL | wx.CENTER, 5)
        self.password = wx.TextCtrl(self, style=wx.TE_PASSWORD | wx.TE_PROCESS_ENTER)
        p_sizer.Add(self.password, 0, wx.ALL, 5)

        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(user_sizer, 0, wx.ALL, 5)
        main_sizer.Add(p_sizer, 0, wx.ALL, 5)

        btn = wx.Button(self, wx.ID_OK)
        main_sizer.Add(btn, 0, wx.ALL | wx.CENTER, 5)

        self.password.Bind(wx.EVT_TEXT, self.updatepass)

        self.SetSizer(main_sizer)

    def updateacc(self, event):
        LoginDialog.moduser = self.user.GetValue()

    def updatepass(self, event):
        LoginDialog.modpassword = self.password.GetValue()


########################################################################
class MyDialog(wx.Dialog):
    """ This window lets the user search up which APK they want """

    # DevNote: Get all folders
    # projects = 'https://appsindogame2.office.company.com/api/projects'
    # game1Branches = 'https://appsindogame2.office.company.com/api/projects/7/branches'
    # game2Branches = 'https://appsindogame2.office.company.com/api/projects/5/branches'

    # password_mgr = urllib.request.HTTPPasswordMgrWithDefaultRealm()

    # password_mgr.add_password(None, projects, "sam_joyce", "Asdqwe123")
    # password_mgr.add_password(None, game1Branches, "sam_joyce", "Asdqwe123")
    # password_mgr.add_password(None, game2Branches, "sam_joyce", "Asdqwe123")

    # handler = urllib.request.HTTPBasicAuthHandler(password_mgr)
    # opener = urllib.request.build_opener(handler)
    # urllib.request.install_opener(opener)

    # Read the API URL and get a JSON object
    # query1 = urllib.request.urlopen(projects).read().decode()
    # game1 = urllib.request.urlopen(game1Branches).read().decode()
    # game2 = urllib.request.urlopen(game2Branches).read().decode()

    game1list = ["App1"]
    game1id = ["game1id"]
    game2list = ["App2"]
    game2id = ["game2id"]
    game3list = ["App3"]
    game3id = ["game3id"]
    # This is to use on the button
    nameList = []

    # Load JSON objects, get Name & ID
    # for x in json.loads(game1):
    #     game1list.append(x['Name'])
    #     game1id.append(x['Id'])
    #
    # for y in json.loads(game2):
    #     game2list.append(y['Name'])
    #     game2id.append(y['Id'])

    # Create a dictionary
    game3dict = dict(zip(game3list, game3id))
    game2dict = dict(zip(game2list, game2id))
    game1dict = dict(zip(game1list, game1id))

    # Combine
    game1dict.update(game2dict)
    game1dict.update(game3dict)

    # print(game1dict)
    # Need a list of names for the ComboBox, we can refer to the dict later for our download ID
    for eachname in game1dict:
        nameList.append(eachname)
        # print(eachname)
    updateoutput = 1

    def __init__(self):
        """Constructor"""
        wx.Dialog.__init__(self, None, title="Search for a APK")

        panel = wx.Panel(self, -1, style=wx.BORDER_RAISED)

        self.comboBox1 = wx.ComboBox(panel, choices=self.nameList, style=wx.CB_SIMPLE, pos=(0, 0))

        self.comboBox1.Bind(wx.EVT_TEXT, self.text_return)
        self.comboBox1.Bind(wx.EVT_COMBOBOX, self.selectChoice)

        okBtn = wx.Button(panel, wx.ID_OK, pos=(100, 0))
        chkBtn = wx.CheckBox(panel, wx.CHK_2STATE, label="Debug APK?", pos=(100, 60))

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(panel)
        self.SetSizerAndFit(sizer)


        self.ignoreEvtText = False

    def selectChoice(self, event):

        self.comboBox1.Unbind(wx.EVT_TEXT)
        output = self.comboBox1.GetStringSelection()
        self.comboBox1.SetValue(output)

        # Here we get our ID from our dictionary
        MyDialog.updateoutput = self.game1dict.get(output)
        # MyDialog.ismulti = MyDialog.chkBtn

    def text_return(self, event):
        if self.ignoreEvtText:
            self.ignoreEvtText = False
            return
        textEntered = event.GetString()

        if textEntered:
            matching = [s for s in self.nameList if textEntered in s]
            self.comboBox1.Set(matching)
            self.ignoreEvtText = True
            self.comboBox1.SetValue(textEntered)
            self.comboBox1.SetInsertionPointEnd()

        else:
            self.comboBox1.Set(self.nameList)


########################################################################
class MainFrame(wx.Frame):
    """
    This frame has all the GUI the user will see on start up
    """

    # DevNote: This prevents subprocess.call from creating console windows
    createNoWindow = 0x08000000
    modpass, modacc = "", ""

    def __init__(self, *args, **kw):
        # ensure the parent's __init__ is called
        super(MainFrame, self).__init__(*args, **kw)

        # Lets prompt the user for details, store it away in a .dat file then we don't have to do prompts anymore
        # my_file = Path("./mydetails.dat")
        # if not my_file.is_file():
        #     dlg = LoginDialog()
        #     res = dlg.ShowModal()
        #     if res == wx.ID_OK:
        #         modacc = LoginDialog.moduser
        #         modpass = LoginDialog.modpassword
        #         np.save('./AA_data.dat', [modacc, modpass])

        # create a panel in the frame
        pnl = wx.Panel(self)

        # DevNote: Left Side
        self.game1MCinstallbutton = wx.Button(pnl, label="Install App1 Debug", pos=(10, 10), id=1)
        self.game1MCinstallbutton.Bind(wx.EVT_BUTTON, self.game1Multiclient, id=1)

        self.game1SCinstallbutton = wx.Button(pnl, label="Install App2 Live Client", pos=(10, 40), id=8)
        self.game1SCinstallbutton.Bind(wx.EVT_BUTTON, self.game1SingleClient, id=8)

        self.game1livebutton = wx.Button(pnl, label="Launch App1 to Live", pos=(10, 70), id=3)
        self.game1livebutton.Bind(wx.EVT_BUTTON, self.launchgame1Live, id=3)

        # DevNote: Right Side
        self.game2installbutton = wx.Button(pnl, label="Install App3", pos=(220, 10), id=2)
        self.game2installbutton.Bind(wx.EVT_BUTTON, self.installgame2, id=2)

        self.game2livebutton = wx.Button(pnl, label="Launch App3 Live", pos=(220, 40), id=4)
        self.game2livebutton.Bind(wx.EVT_BUTTON, self.launchgame2Live, id=4)

        # DevNote: Left Side
        self.rentalbutton = wx.Button(pnl, label="Launch App to Test Server", pos=(10, 100), id=5)
        self.rentalbutton.Bind(wx.EVT_BUTTON, self.EnterRentalInput, id=5)

        self.screenshotbutton = wx.Button(pnl, label="Screenshot Connected Devices", pos=(10, 140), id=6)
        self.screenshotbutton.Bind(wx.EVT_BUTTON, self.deviceScreenshot, id=6)

        self.videobutton = wx.Button(pnl, label="Video Record Device", pos=(10, 170), id=7)
        self.videobutton.Bind(wx.EVT_BUTTON, self.videoRecordDevice, id=7)

        # create a menu bar
        self.makeMenuBar()

        # and a status bar
        self.CreateStatusBar()
        self.SetStatusText("Welcome to the ADB Automator!")

    def makeMenuBar(self):
        """
        A menu bar is composed of menus, which are composed of menu items.
        This method builds a set of menus and binds handlers to be called
        when the menu enemy is selected.
        """

        # Make a file menu with Hello and Exit items
        fileMenu = wx.Menu()
        # When using a stock ID we don't need to specify the menu enemy's
        exitItem = fileMenu.Append(wx.ID_EXIT)

        toolsMenu = wx.Menu()
        downloadAPK = toolsMenu.Append(wx.ID_ANY, "Download APK", "This will download the APK to C:\\ADBScript\\APKLibrary\\")
        # App13Packing = toolsMenu.Append(wx.ID_ANY, "Pack App1 3 Stream", "This will pack your custom stream")
        # gamePacking = toolsMenu.Append(wx.ID_ANY, "Pack game Stream", "Type in your stream and start packing")
        androidMonitor = toolsMenu.Append(wx.ID_ANY, "Android Device Monitor", "This will open ADM if you have it installed")
        resetsave = toolsMenu.Append(wx.ID_ANY, "Reset Save File", "Reset save(s) on QA & RC")

        # Now a help menu for the about enemy
        helpMenu = wx.Menu()
        aboutItem = helpMenu.Append(wx.ID_ABOUT)

        # Make the menu bar and add the two menus to it. The '&' defines
        # that the next letter is the "mnemonic" for the menu enemy. On the
        # platforms that support it those letters are underlined and can be
        # triggered from the keyboard.
        menuBar = wx.MenuBar()
        menuBar.Append(fileMenu, "&File")
        menuBar.Append(toolsMenu, "&Tools")
        menuBar.Append(helpMenu, "&Help")

        # Give the menu bar to the frame
        self.SetMenuBar(menuBar)

        # Finally, associate a handler function with the EVT_MENU event for
        # each of the menu items. That means that when that menu enemy is
        # activated then the associated handler function will be called.

        self.Bind(wx.EVT_MENU, self.OnExit, exitItem)
        self.Bind(wx.EVT_MENU, self.downloadAPK, downloadAPK)
        self.Bind(wx.EVT_MENU, self.startAndroidDeviceMonitor, androidMonitor)
        self.Bind(wx.EVT_MENU, self.OnAbout, aboutItem)
        self.Bind(wx.EVT_MENU, self.resetsave, resetsave)
        self.Bind(wx.EVT_MENU, self.startAndroidDeviceMonitor, androidMonitor)


    def OnExit(self, event):
        """Close the frame, terminating the application."""
        self.Close(True)

    # noinspection PyMethodMayBeStatic
    def OnAbout(self, event):
        """Display an About Dialog"""
        wx.MessageBox("Author: Samuel Joyce \nCreated: 10/12/2018",
                      "About",
                      wx.OK | wx.ICON_INFORMATION)

    def getDevices(self):
        """Use ADB to get all connected devices

        :return: String: deviceModel, deviceID
        """

        devices = None

        for i in range(3):
            devices = subprocess.check_output("adb devices -l", creationflags=self.createNoWindow)

        devices = devices.decode()
        deviceModel = re.findall("model:(.*) device", devices)
        deviceID = re.findall(r"(\S+) {2}", devices, flags=re.IGNORECASE)

        return deviceModel, deviceID

    def game1Multiclient(self, event):
        """Uninstall all App1 3 packages found on devices, then install bootstrap_rs2client-release.apk to them"""

        self.game1MCinstallbutton.Disable()
        deviceModel, deviceID = self.getDevices()

        if not deviceModel or not deviceID:
            self.SetStatusText("No Android devices detected")
            self.game1MCinstallbutton.Enable()
            return

        listLength = len(deviceID)

        for i in deviceID:
            self.SetStatusText(f"Processing {i} out of {listLength}.")
            print(i)
            subprocess.call(f"adb -s {i} uninstall com.company.App1.android", creationflags=self.createNoWindow)
            subprocess.call(f'adb -s {i} install -r "C:\\ADBscripts\\APKLibrary\\App1.apk"', creationflags=self.createNoWindow)
            print("installed")
        if listLength > 1:
            self.SetStatusText(f"Finished Installing App1 3 on {listLength} devices")
        else:
            self.SetStatusText(f"Finished Installing App1 3 on {listLength} device")

        self.game1MCinstallbutton.Enable()

    def game1SingleClient(self, event):
        """Uninstall all App1 3 packages found on devices, then install bootstrap_rs2client-release.apk to them"""

        self.game1SCinstallbutton.Disable()
        deviceModel, deviceID = self.getDevices()

        if not deviceModel or not deviceID:
            self.SetStatusText("No Android devices detected")
            self.game1SCinstallbutton.Enable()
            return

        listLength = len(deviceID)

        for i in range(listLength):
            self.SetStatusText(f"Processing {deviceModel[i]} {i+1} out of {listLength}.")
            subprocess.call(f"adb -s {deviceID[i]} uninstall com.company.App1.android", creationflags=self.createNoWindow)
            subprocess.call(f"adb -s {deviceID[i]} uninstall com.company.App1.android.debug", creationflags=self.createNoWindow)
            subprocess.call(f"adb -s {deviceID[i]} uninstall com.company.App1.debug", creationflags=self.createNoWindow)
            subprocess.call(f"adb -s {deviceID[i]} uninstall com.company.App1", creationflags=self.createNoWindow)
            subprocess.call(f"adb -s {deviceID[i]} install -r C:\\ADBscripts\\APKLibrary\\apk1.apk", creationflags=self.createNoWindow)

        if listLength > 1:
            self.SetStatusText(f"Finished Installing App1 3 on {listLength} devices")
        else:
            self.SetStatusText(f"Finished Installing App1 3 on {listLength} device")

        self.game1SCinstallbutton.Enable()

    def installgame2(self, event):
        """Uninstall all game packages found on devices, then install android-release.apk to them"""

        self.game2installbutton.Disable()

        deviceModel, deviceID = self.getDevices()

        if not deviceModel or not deviceID:
            self.SetStatusText("No Android devices detected")
            self.game2installbutton.Enable()
            return

        listLength = len(deviceID)

        for i in range(listLength):

            self.SetStatusText(f"Processing {deviceModel[i]} {i+1} out of {listLength}.")
            subprocess.call(f"adb -s {deviceID[i]} uninstall com.company.App2.android", creationflags=self.createNoWindow)
            subprocess.call(f"adb -s {deviceID[i]} uninstall com.company.App2.android.debug", creationflags=self.createNoWindow)
            subprocess.call(f"adb -s {deviceID[i]} uninstall com.company.App2.debug", creationflags=self.createNoWindow)
            subprocess.call(f"adb -s {deviceID[i]} uninstall com.company.App2", creationflags=self.createNoWindow)
            response = subprocess.call(f"adb -s {deviceID[i]} install -r C:\\ADBscripts\\APKLibrary\\apk2.apk", creationflags=self.createNoWindow)
            print("Print")
        if response == 0:
            if listLength > 1:
                self.SetStatusText(f"Finished Launching App1 on {listLength} devices to live")
            else:
                self.SetStatusText(f"Finished Launching App1 {listLength} device to live")
        elif response != 0:
            self.SetStatusText(f"Application not installed")

        self.game2installbutton.Enable()

    def launchServer(self, event, userinput):
        """Launch the server based on the input from the user"""

        self.rentalbutton.Disable()
        deviceModel, deviceID = self.getDevices()

        if not deviceModel or not deviceID:
            self.SetStatusText("No Android devices detected")
            self.rentalbutton.Enable()
            return

        listLength = len(deviceID)

        for i in range(listLength):
            self.SetStatusText(f"Processing {deviceModel[i]} {i+1} out of {listLength}.")
            subprocess.call(f"adb -s {deviceID[i]} shell am force-stop com.company.App1.android", creationflags=self.createNoWindow)
            subprocess.call(f"adb -s {deviceID[i]} shell am force-stop com.company.App2.android", creationflags=self.createNoWindow)
            subprocess.call(f"adb -s {deviceID[i]} shell am start {userinput}", creationflags=self.createNoWindow)

        if listLength > 1:
            self.SetStatusText(f"Finished Launching {listLength} devices to {userinput}")
        else:
            self.SetStatusText(f"Finished Launching device to {userinput}")

    def launchgame1Live(self, event):
        """Launch App1 Application to Live"""

        self.game1livebutton.Disable()

        deviceModel, deviceID = self.getDevices()
        listLength = len(deviceID)

        if not deviceModel or not deviceID:
            self.SetStatusText("No Android devices detected")
            self.game1livebutton.Enable()
            return

        for i in range(listLength):
            self.SetStatusText(f"Launching App1 3 on {deviceModel[i]} {i+1}/{listLength} to live")
            response = subprocess.call(f"adb -s {deviceID[i]} shell monkey -p com.atrox.app1 -c android.intent.category.LAUNCHER 1", creationflags=self.createNoWindow)

        if response == 0:
            if listLength > 1:
                self.SetStatusText(f"Finished Launching App1 on {listLength} devices to live")
            else:
                self.SetStatusText(f"Finished Launching App1 {listLength} device to live")
        elif response != 0:
            self.SetStatusText(f"Application not installed")

        self.game1livebutton.Enable()

    def launchgame2Live(self, event):
        """Launch game Application to Live"""

        self.game2livebutton.Disable()

        deviceModel, deviceID = self.getDevices()
        listLength = len(deviceID)

        if not deviceModel or not deviceID:
            self.SetStatusText("No Android devices detected")
            self.game2livebutton.Enable()
            return

        for i in range(listLength):
            self.SetStatusText(f"Launching App3 on {deviceModel[i]} {i+1}/{listLength} to live")
            response = subprocess.call(f"adb -s {deviceID[i]} shell monkey -p com.atrox.app2.android -c android.intent.category.LAUNCHER 1", creationflags=self.createNoWindow)
            # print(response)

        if response == 0:
            if listLength > 1:
                self.SetStatusText(f"Finished Launching App3 on {listLength} devices to live")
            else:
                self.SetStatusText(f"Finished Launching App3 {listLength} device to live")

        elif response != 0:
            self.SetStatusText(f"Application not installed")

        self.game2livebutton.Enable()

    def EnterRentalInput(self, event):
        """User can input a server link and open the app with it

        :input server link #1
        :input server link #2
        """
        self.rentalbutton.Disable()

        clipboard = wx.TextDataObject()
        wx.TheClipboard.Open()
        success = wx.TheClipboard.GetData(clipboard)
        wx.TheClipboard.Close()

        if success:
            if re.findall("atrox-game-server", clipboard.GetText()) or re.findall("rs-launch", clipboard.GetText()):
                self.launchServer(self, clipboard.GetText())
            else:
                self.SetStatusText(f"No game server detected, copy from main")
        else:
            self.SetStatusText(f"No game server detected, copy from main")

        self.rentalbutton.Enable()

    def deviceScreenshot(self, event):
        """ Screenshot all devices connected and place the output at root"""

        self.screenshotbutton.Disable()

        deviceModel, deviceID = self.getDevices()
        deviceIDModel = []

        if not deviceModel or not deviceID:
            self.SetStatusText("No Android devices detected")
            self.screenshotbutton.Enable()
            return

        for everyi in deviceModel:
            for everym in deviceID:
                deviceIDModel = [everym + " " + everyi]

        try:
            dialog = wx.MultiChoiceDialog(self, "Pick your devices", "caption", deviceIDModel, wx.OK | wx.CANCEL)
        except UnboundLocalError:
            self.SetStatusText(f"No Devices Found")
            self.screenshotbutton.Enable()
            return

        instance = dialog.ShowModal()
        devices = dialog.GetSelections()

        listLength = len(devices)
        dialog.Destroy()

        if instance == wx.ID_OK:
            for i in range(listLength):
                self.SetStatusText(f"Screenshotting {deviceModel[i]} {i+1}/{listLength}")
                subprocess.call(f"adb -s {deviceID[i]} shell screencap /sdcard/{deviceModel[i]}.png", creationflags=self.createNoWindow)
                subprocess.call(fr"adb -s {deviceID[i]} pull /sdcard/{deviceModel[i]}.png C:\ADBscripts\PhoneScreenshots", creationflags=self.createNoWindow)

            if listLength > 1:
                self.SetStatusText(f"Took {listLength} Screenshots")
            else:
                self.SetStatusText(f"Took {listLength} Screenshot")

        self.screenshotbutton.Enable()

    def videoRecordDevice(self, event):
        """ Video Record all devices connected and place the output at root"""
        self.videobutton.Disable()

        deviceModel, deviceID = self.getDevices()
        deviceIDModel = []

        if not deviceModel or not deviceID:
            self.SetStatusText("No Android devices detected")
            self.videobutton.Enable()
            return

        for everyi in deviceModel:
            for everym in deviceID:
                deviceIDModel = [everym + " " + everyi]

        try:
            dialog = wx.MultiChoiceDialog(self, "Pick your devices", "caption", deviceIDModel, wx.OK | wx.CANCEL)
        except UnboundLocalError:
            self.SetStatusText(f"No Devices Detected")
            self.videobutton.Enable()
            return

        instance = dialog.ShowModal()
        devices = dialog.GetSelections()

        listLength = len(devices)
        dialog.Destroy()

        if instance == wx.ID_OK:
            video = wx.TextEntryDialog(self, "", "How long do you want to record for in seconds?", "", wx.OK | wx.CANCEL)

            instance = video.ShowModal()
            videoLength = video.GetValue()
            video.Destroy()

            if instance == wx.ID_OK:
                for i in range(listLength):
                    self.SetStatusText(f"Video Recording {devices[i]} {i+1}/{listLength}")
                    subprocess.call(f"adb -s {deviceID[i]} shell screenrecord /sdcard/{deviceModel[i]}.mp4 --time {videoLength}")
                    subprocess.call(fr"adb -s {deviceID[i]} pull /sdcard/{deviceModel[i]}.mp4 C:\ADBscripts\PhoneVideos")

                if listLength > 1:
                    self.SetStatusText(f"Recorded a {videoLength} second video on {listLength} devices")
                else:
                    self.SetStatusText(f"Recorded a {videoLength} second video on {listLength} device")

        self.videobutton.Enable()

    def startAndroidDeviceMonitor(self, event):
        """ Here we provide a shortcut to start up the Android Device Monitor. This tool has a filtered logcat """
        try:
            os.startfile(r"C:\Users\sam_JOYCE\AppData\Local\Android\Sdk\tools\lib\monitor-x86_64\monitor.exe")
            self.SetStatusText(f"Successfully started Android Device Monitor")
        except FileNotFoundError:
            self.SetStatusText(f"Not Found. Please install the Android SDK")

    def downloadAPK(self, event):
        """ A user can search a list gathered from artstore for an APK they want """

        # DevNote: Needs Fixing
        choice = ""

        dlg = MyDialog()
        res = dlg.ShowModal()
        if res == wx.ID_OK:
            choice = MyDialog.updateoutput

        if choice:
            # print(choice)
            sublist = []
            subid = []
            subbranch = []
            game1, game2 = False, False

            if choice is "game1id":
                mychoice = choice
                choice = "App1"
            elif choice is "game2id":
                mychoice = choice
                choice = "App2"
            elif choice is "game3id":
                mychoice = choice
                choice = "App3"
            else:
                self.SetStatusText("No choice found!")
                return

            if mychoice:
                try:
                    shutil.copy(f"C:\\Users\\svjkr\\Downloads\\{choice}.apk", f"C:\\ADBScripts\\APKLibrary\\{choice}.apk")
                except:
                    self.SetStatusText(f"{choice} was not found!")
                    return

            self.SetStatusText(f"Downloaded Successfully")

    def packgame1(self, event):
        """ With the correct Mod name, password and stream, you can send a pack request to packmaster """

        username = wx.TextEntryDialog(self, "", "Enter your Mod name here", "", wx.OK | wx.CANCEL)

        modal = username.ShowModal()
        userName = username.GetValue()
        username.Destroy()

        if modal == wx.ID_OK:
            password = wx.PasswordEntryDialog(self, "", "Enter your password here", "", wx.OK | wx.CANCEL)

            modal = password.ShowModal()
            passWord = password.GetValue()
            password.Destroy()

            if modal == wx.ID_OK:
                stream = wx.TextEntryDialog(self, "", "Enter your game1 stream name here", "", wx.OK | wx.CANCEL)

                modal = stream.ShowModal()
                streamName = stream.GetValue()
                stream.Destroy()

                if modal == wx.ID_OK:
                    whatStream = f"https://packmaster.office.company.com/run.ws?label=p4&task=rs2_incremental&rtArgs0={streamName}&slave=Any"

                    password_mgr = urllib.request.HTTPPasswordMgrWithDefaultRealm()
                    password_mgr.add_password(None, whatStream, userName, passWord)

                    handler = urllib.request.HTTPBasicAuthHandler(password_mgr)
                    opener = urllib.request.build_opener(handler)
                    urllib.request.install_opener(opener)

                    try:
                        packmaster_id = urllib.request.urlopen(whatStream).read()
                        packmaster_id = packmaster_id.decode("utf-8")
                        webbrowser.open("https://packmaster.office.company.com/")

                        wrongitem = f'"id": {packmaster_id},\n  "label": "p4",\n  "name": "rs2_incremental",\n  "status": "Failed"'.encode()

                        packmaster_url = f"https://packmaster.office.company.com/jobs_js.ws?focus={packmaster_id}&displayType=1"
                        packscrape_top_level_url = packmaster_url
                        password_mgr.add_password(None, packscrape_top_level_url, userName, passWord)

                        packmaster_html = urllib.request.urlopen(packmaster_url).read()

                        if wrongitem in packmaster_html:
                            self.SetStatusText(f"Packing has failed.")
                        else:
                            self.SetStatusText(f"Login Successful, now packing {streamName}")

                    except urllib.request.HTTPError as e:
                        self.SetStatusText(f"{e}")

    # def threadmaster(self, event):
        worker = Thread(target=self.packgame2())
        worker.setDaemon(True)
        worker.start()

    def packgame2(self):
        """Pack an game stream through https://packmaster.office.company.com

        User needs to enter their mod name, password and game stream name, such as: samj_game2_stream"""

        packmaster_byte_id, packmaster_html = b'', b''

        self.SetStatusText("Started packing game")

        username = wx.TextEntryDialog(self, "", "Enter your Mod name here", "", wx.OK | wx.CANCEL)

        modal = username.ShowModal()
        userName = username.GetValue()
        username.Destroy()

        if modal == wx.ID_OK:
            password = wx.PasswordEntryDialog(self, "", "Enter your password here", "", wx.OK | wx.CANCEL)

            modal = password.ShowModal()
            passWord = password.GetValue()
            password.Destroy()

            if modal == wx.ID_OK:
                stream = wx.TextEntryDialog(self, "", "Enter your game2 stream name here", "", wx.OK | wx.CANCEL)

                modal = stream.ShowModal()
                streamName = stream.GetValue()
                stream.Destroy()

                if modal == wx.ID_OK:
                    packmaster_functions = ['sprites', 'textures', 'bases', 'anims', 'models', 'binary', 'jagfx', 'vorbis', 'patch', 'midi', 'jingle', 'constants', 'config', 'cs2', 'if', 'config', 'cs2', 'config', 'cs2', 'if', 'map', 'worldmap', 'script', 'defaults', 'webscripts']

                    webbrowser.open("https://packmaster.office.company.com/")
                    for i in packmaster_functions:
                        game2_pack_url = f"https://packmaster.office.company.com/run.ws?label=p4&task=App2_{i}_v4&rtArgs0={streamName}&slave=Any"

                        password_mgr = urllib.request.HTTPPasswordMgrWithDefaultRealm()
                        password_mgr.add_password(None, game2_pack_url, userName, passWord)

                        handler = urllib.request.HTTPBasicAuthHandler(password_mgr)
                        opener = urllib.request.build_opener(handler)
                        urllib.request.install_opener(opener)

                        # Start Function, collect ID, handle exception
                        try:
                            packmaster_byte_id = urllib.request.urlopen(game2_pack_url, timeout=900).read()
                        except urllib.request.HTTPError as e:
                            self.SetStatusText(f"{e}")

                        # Job ID
                        packID = packmaster_byte_id.decode("utf-8")
                        packmaster_url = f"https://packmaster.office.company.com/jobs_js.ws?displayType=0&jobID={packID}"
                        password_mgr.add_password(None, packmaster_url, userName, passWord)

                        print(f"Packing App2_{i}_v4")
                        self.SetStatusText(f"Packing App2_{i}_v4")

                        try:
                            packmaster_html = urllib.request.urlopen(packmaster_url, timeout=900).read().decode()
                        except urllib.request.HTTPError as e:
                            self.SetStatusText(f"{e}")

                        while True:
                            if "Failed" in packmaster_html:
                                print("Failed, try repacking config if if/cs2/script is failing")
                                self.SetStatusText(f"Script failed. Try repacking config if if/cs2/script is failing")
                                return

                            if "Killed" in packmaster_html:
                                print("Killed")
                                self.SetStatusText('Job killed. Stopping program as this has happened for a reason.')
                                return

                            if "Pending" in packmaster_html:
                                print("Pending")
                                self.SetStatusText("Job is in a queue. Waiting.")
                                try:
                                    pendinghtml = urllib.request.urlopen(packmaster_url, timeout=900).read()
                                    penddecoded = pendinghtml.decode()
                                    packmaster_html = penddecoded

                                except urllib.request.HTTPError as e:
                                    print(e)

                            if "Done" in packmaster_html:
                                print("Job Finished")
                                self.SetStatusText(f"Done")
                                try:
                                    finishedhtml = urllib.request.urlopen(packmaster_url, timeout=900).read()
                                    findecoded = finishedhtml.decode()
                                    packmaster_html = findecoded

                                except urllib.request.HTTPError as e:
                                    print(e)
                                break

                            if "In progress" in packmaster_html:
                                print("In Progress")
                                try:
                                    inproghtml = urllib.request.urlopen(packmaster_url, timeout=900).read()
                                    decoded = inproghtml.decode()
                                    packmaster_html = decoded

                                except urllib.request.HTTPError.reason as e:
                                    print(e)

                            else:
                                print("This is bad, keywords must of changed... why?!")
                                exit()

    def resetsave(self, event):

        whataccount = wx.TextEntryDialog(self, "", "What account?", "", wx.OK | wx.CANCEL)
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(whataccount, 0, wx.LEFT, 0)
        modal = whataccount.ShowModal()
        mod_account = whataccount.GetValue()
        whataccount.Destroy()

        self.SetStatusText(f"I just reset the save file of: {mod_account}")
        print(f"\nI just reset the save file of: {mod_account}")


########################################################################
if __name__ == '__main__':
    try:
        os.mkdir(r"C:\ADBscripts")
        os.mkdir(r"C:\ADBscripts\PhoneVideos")
        os.mkdir(r"C:\ADBscripts\PhoneScreenshots")
        os.mkdir(r"C:\ADBscripts\APKLibrary")
    except FileExistsError:
        pass
    app = wx.App(False)
    frm = MainFrame(None, title='Android Debug Bridge Automator', style=wx.DEFAULT_FRAME_STYLE ^ wx.RESIZE_BORDER ^ wx.MAXIMIZE_BOX, size=(400, 300))

    frm.Show(True)


    app.MainLoop()


def main_code():
    """This is only so i can click to the bottom of the page"""
    pass
