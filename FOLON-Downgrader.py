import sys
import subprocess
import shutil
import os
import Utility as Util
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import QIcon
from inspect import isfunction

from LoadScreenFuncs import LoadingThread, LoadingTranslucentScreen

class Threader(QThread):

    def __init__(self, Function):
        super().__init__()
        self._Function = Function

    def run(self):
        # Open the URL address.
        _Function()


class ScreenThread(LoadingThread):
    #Thanks to Yousef Azizi for his PyQtLoadingscreen script

    def __init__(self, Function, PostFunction = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._Function = Function
        if callable(PostFunction):
            self.finished.connect(lambda: PostFunction())

    def run(self):
        self._Function()

class MainWindow(QTabWidget):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        self.tab1 = QWidget()
        self.tab2 = QWidget()
        self.tab1.setObjectName("Tab")
        self.tab2.setObjectName("Tab")

        self.addTab(self.tab1, "Tab 1")
        self.addTab(self.tab2, "Tab 2")
        self.tab1UI()
        self.tab2UI()

        self.setWindowTitle("FOLON Fallout 4 downgrader")
        if Util.IsBundled:
            FOLONIcon = QIcon(".FOLON-Downgrader-Files/img/FOLON256.png")
        else:
            FOLONIcon = QIcon("img/FOLON256.png")
        self.setWindowIcon(FOLONIcon)
#########################################################################################
# GENERAL GUI                                                                           #
#########################################################################################
    
    def Loading(self, Function, text = "Loading..", PostFunction = None):
        self.__loadingTranslucentScreen = LoadingTranslucentScreen(parent=self,
                                                                   description_text=text)
        self.__loadingTranslucentScreen.setDescriptionLabelDirection('Right')
        #self.__thread = LoadingThread(loading_screen=self.__loadingTranslucentScreen)
        # for second result
        self.__thread = ScreenThread(Function, PostFunction=PostFunction, loading_screen=self.__loadingTranslucentScreen)
        self.__thread.start()


##########################################################################################
# STEAM LOGIN                                                                            #
##########################################################################################

    def tab1UI(self):
        layout = QFormLayout()

        layout.addRow(
            QLabel("<h1>Please log into Steam before downgrading Fallout 4.</h1>")
        )
        layout.addRow(
            QLabel(
                "<p>To downgrade Fallout 4 we will need to download files via Steam, please login to do so.</p>"
            )
        )

        self.UsernameEntry = QLineEdit()
        Settings = Util.Read_Settings()
        self.UsernameEntry.setText(Settings["Username"])
        self.UsernameEntry.returnPressed.connect(self.GoToPassword)
        self.PasswordEntry = QLineEdit()
        self.PasswordEntry.setEchoMode(QLineEdit.EchoMode.Password)
        self.PasswordEntry.returnPressed.connect(self.SteamSubmit)
        self.PasswordCheck = QCheckBox()
        self.PasswordCheck.setChecked(True)
        self.PasswordCheck.stateChanged.connect(self.ChangeHiddenPassword)

        LoginButton = QPushButton(text="Login to Steam")
        LoginButton.pressed.connect(self.SteamSubmit)

        layout.addRow("Username:", self.UsernameEntry)
        layout.addRow("Password:", self.PasswordEntry)
        layout.addRow("Password hidden:", self.PasswordCheck)
        layout.addRow(LoginButton)

        self.setTabText(0, "Steam login")
        self.tab1.setLayout(layout)
        # self.setTabEnabled(0, False)

    # Steam Functions

    def GoToPassword(self):
        self.PasswordEntry.setFocus()

    def ChangeHiddenPassword(self):
        if self.PasswordCheck.isChecked():
            self.PasswordEntry.setEchoMode(QLineEdit.EchoMode.Password)
        else:
            self.PasswordEntry.setEchoMode(QLineEdit.EchoMode.Normal)

    def SteamSubmit(self):
        Settings = Util.Read_Settings()
        Settings["Username"] = self.UsernameEntry.text()
        self.Password = self.PasswordEntry.text()
        Util.Write_Settings(Settings)
        self.LoginSteamInit()

    def LoginSteamInit(self):
        if not os.path.isdir(".FOLON-Downgrader-Files/SteamFiles/"):
            self.Loading(self.SetupSteam, text="Loading Steam backend", 
                PostFunction=self.LoginSteamInit)
        else:
            self.Loading(self.LoginSteam, text="Logging into Steam")

    def SetupSteam(self):
        import zipfile
        import pathlib

        if not os.path.isdir(".FOLON-Downgrader-Files"):
            os.mkdir(".FOLON-Downgrader-Files")

        if Util.IsWindows():
            os.system(
                'curl -sqL "https://steamcdn-a.akamaihd.net/client/installer/steamcmd.zip" -o .FOLON-Downgrader-Files/steamcmd.zip'
            )
            with zipfile.ZipFile(".FOLON-Downgrader-Files/steamcmd.zip", "r") as zip_ref:
                zip_ref.extractall(".FOLON-Downgrader-Files/SteamFiles/")

            os.system(".FOLON-Downgrader-Files/SteamFiles/steamcmd.sh +quit")
        else:
            if os.path.isdir(".FOLON-Downgrader-Files/SteamFiles"):
                shutil.rmtree(".FOLON-Downgrader-Files/SteamFiles")

            pathlib.Path.mkdir(".FOLON-Downgrader-Files/SteamFiles")
            os.system(
                'curl -sqL "https://steamcdn-a.akamaihd.net/client/installer/steamcmd_linux.tar.gz" | tar zxvf - -C .FOLON-Downgrader-Files/SteamFiles'
            )
            os.system(".FOLON-Downgrader-Files/SteamFiles/steamcmd.sh +quit")

    def LoginSteam(self):
        Settings = Util.Read_Settings()
        Username = Settings["Username"]
        Password = self.Password
        if Util.IsWindows():
            if os.path.isfile(".FOLON-Downgrader-Files/SteamFiles/steamcmd.exe"):
                p = subprocess.Popen(
                    [
                        ".FOLON-Downgrader-Files/SteamFiles/steamcmd.exe",
                        "+login",
                        f"{Username}",
                        f"{Password}",
                        "+quit",
                    ],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                )
        else:
            if os.path.isfile(".FOLON-Downgrader-Files/SteamFiles/steamcmd.sh"):
                p = subprocess.Popen(
                    [
                        ".FOLON-Downgrader-Files/SteamFiles/steamcmd.sh",
                        "+login",
                        f"{Username}",
                        f"{Password}",
                        "+quit",
                    ],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                )
        p.communicate(b"quit")
        if (
            b"You can also enter this code at any time using 'set_steam_guard_code'"
            in p.communicate()[0]
        ):

            self.SteamGDlg = QDialog(self)
            self.SteamGDlgLayout = QFormLayout()

            self.SteamGDlgLayout.addRow(
                QLabel("<h3>Please enter your Steam guard code.</h3>")
            )
            self.SteamGDlgLayout.addRow(
                QLabel("<p>To authorize your identity Steam has sent a code</p>")
            )
            self.SteamGDlgLayout.addRow(
                QLabel("<p>to either your mail or phone, please enter it here.</p>")
            )

            self.GuardEntry = QLineEdit()
            GuardButton = QPushButton(text="Submit")
            GuardButton.pressed.connect(self.GuardSubmit)

            self.SteamGDlgLayout.addRow(
                QLabel("<p>Steam guard code:</p>"), self.GuardEntry
            )
            self.SteamGDlgLayout.addRow(GuardButton)
            self.SteamGDlg.setWindowTitle("Steam Guard Dialog")
            self.SteamGDlg.setLayout(self.SteamGDlgLayout)
            self.SteamGDlg.exec()
        elif (
            bytes(f"Logging in user '{Username}' to Steam Public...OK", "UTF-8")
            in p.communicate()[0]
        ):
            try:
                self.SteamGDlg.close()
            except:
                pass
        elif bytes("rate limit", "UTF-8") in p.communicate()[0]:
            self.OpenRateDialog()

        elif b"FAILED (Invalid Password)" in p.communicate()[0]:
            try:
                self.LoadingDialog.close()
            except:
                pass
            SteamPDlg = QDialog(self)
            SteamPDlgLayout = QFormLayout()

            SteamPDlgLayout.addRow(QLabel("<h3>Incorrect Password.</h3>"))
            SteamPDlgLayout.addRow(QLabel("<p>Please re-enter the password.</p>"))
            SteamPDlgLayout.addRow(
                QLabel("<p>Remember to <b>check</b> if it is correct.</p>")
            )
            SteamPDlg.setWindowTitle("Steam Password Dialog")
            SteamPDlg.setLayout(SteamPDlgLayout)
            SteamPDlg.exec()

    def GuardSteam(self):
        Settings = Util.Read_Settings()

        if Util.IsWindows():
            p = subprocess.Popen(
                f'.FOLON-Downgrader-Files/SteamFiles/steamcmd.exe +login "{Settings["Username"]}" "{self.PasswordEntry.text()}" +quit',
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
            )
        else:
            p = subprocess.Popen(
                f'.FOLON-Downgrader-Files/SteamFiles/steamcmd.sh +login "{Settings["Username"]}" "{self.PasswordEntry.text()}" +quit',
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
            )
        p.communicate(b"quit")

    def GuardSubmit(self):
        Settings = Util.Read_Settings()
        print(self.GuardEntry.text())
        import subprocess

        if Util.IsWindows():
            p = subprocess.Popen(
                [
                    ".FOLON-Downgrader-Files/SteamFiles/steamcmd.exe",
                    "+login",
                    f'{Settings["Username"]}',
                    f"{self.PasswordEntry.text()}",
                    f"{self.GuardEntry.text()}",
                    "+quit",
                ],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
            )
        else:
            p = subprocess.Popen(
                [
                    ".FOLON-Downgrader-Files/SteamFiles/steamcmd.sh",
                    "+login",
                    f'{Settings["Username"]}',
                    f"{self.PasswordEntry.text()}",
                    f"{self.GuardEntry.text()}",
                    "+quit",
                ],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
            )
        Code = self.GuardEntry.text()
        p.communicate(bytes(Code + "\n", "UTF-8"))
        if (
            bytes(
                f"Logging in user '{Settings['Username']}' to Steam Public...OK",
                "UTF-8",
            )
            in p.communicate()[0]
        ):

            try:
                self.SteamGDlg.close()
            except:
                pass
            print("DONE")
        elif bytes("rate limit", "UTF-8") in p.communicate()[0]:
            self.OpenRateDialog()

    def OpenRateDialog(self):
        try:
            self.SteamGDlg.close()
        except:
            pass
        RateDialog = QDialog(self)
        RateDialogLayout = QFormLayout()
        RateDialogLayout.addRow(QLabel("<h1>You are being rate limited</h1>"))
        RateDialogLayout.addRow(
            QLabel("<p>This is most likely because of an error in the installer</p>")
        )
        LinkLabel = QLabel(
            "<a href='https://discord.gg/GtmKaR8'>Please report it to the Discord server</a>"
        )
        LinkLabel.setOpenExternalLinks(True)
        RateDialogLayout.addRow(LinkLabel)
        RateDialogLayout.addRow(QLabel("And ping @Coffandro for help"))

        RateDialogButton = QPushButton(text="Close")
        RateDialogButton.pressed.connect(self.CloseRateDialog)
        RateDialogLayout.addRow(RateDialogButton)

        RateDialog.setLayout(RateDialogLayout)
        RateDialog.exec()

    def CloseRateDialog(self):
        sys.exit()

    def print_output(self, s):
        print(s)

    def ContinueUI(self):
        print("DONE WITH 1")

    ##########################################################################################
    # Installation                                                                           #
    ##########################################################################################

    def tab2UI(self):
        # Thanks to Zerratar for reference implementation in his FO4-Downgrader
        self.Depots = [
            # Main game
            [377161, 7497069378349273908],
            [377162, 5847529232406005096],
            [377163, 5819088023757897745],
            [377164, 2178106366609958945],
            # Wasteland W
            [435880, 1255562923187931216],
            # Automatron
            [435870, 1691678129192680960],
            [435871, 5106118861901111234],
            # Contraptions W
            [480630, 5527412439359349504],
            # Far harbour
            [435881, 1207717296920736193],
            [435882, 8482181819175811242],
            # Vault tec
            [480631, 6588493486198824788],
            [393885, 5000262035721758737],
            # Nuka world
            [490650, 4873048792354485093],
            [393895, 7677765994120765493],
        ]
        layout = QFormLayout()

        SteamLabel = QLabel(text=str(Util.WhereSteam()))
        layout.addRow(SteamLabel)

        CopyButton = QPushButton(text="Copy Depots to local folder")
        CopyButton.pressed.connect(self.CopyFiles)
        layout.addRow(CopyButton)

        """
        InstallButton1 = QPushButton(text="Install Depot 1")
        InstallButton1.pressed.connect(lambda: self.Install(0))
        layout.addRow(InstallButton1)

        InstallButton2 = QPushButton(text="Install Depot 2")
        InstallButton2.pressed.connect(lambda: self.Install(1))
        layout.addRow(InstallButton2)

        InstallButton3 = QPushButton(text="Install Depot 3")
        InstallButton3.pressed.connect(lambda: self.Install(2))
        layout.addRow(InstallButton3)

        InstallButton4 = QPushButton(text="Install Depot 4")
        InstallButton4.pressed.connect(lambda: self.Install(3))
        layout.addRow(InstallButton4)

        InstallButton5 = QPushButton(text="Install Depot 5")
        InstallButton5.pressed.connect(lambda: self.Install(4))
        layout.addRow(InstallButton5)

        InstallButton6 = QPushButton(text="Install Depot 6")
        InstallButton6.pressed.connect(lambda: self.Install(5))
        layout.addRow(InstallButton6)

        InstallButton7 = QPushButton(text="Install Depot 7")
        InstallButton7.pressed.connect(lambda: self.Install(6))
        layout.addRow(InstallButton7)

        InstallButton8 = QPushButton(text="Install Depot 8")
        InstallButton8.pressed.connect(lambda: self.Install(7))
        layout.addRow(InstallButton8)

        InstallButton9 = QPushButton(text="Install Depot 9")
        InstallButton9.pressed.connect(lambda: self.Install(8))
        layout.addRow(InstallButton9)

        InstallButton10 = QPushButton(text="Install Depot 10")
        InstallButton10.pressed.connect(lambda: self.Install(9))
        layout.addRow(InstallButton10)

        InstallButton11 = QPushButton(text="Install Depot 11")
        InstallButton11.pressed.connect(lambda: self.Install(10))
        layout.addRow(InstallButton11)

        InstallButton12 = QPushButton(text="Install Depot 12")
        InstallButton12.pressed.connect(lambda: self.Install(11))
        layout.addRow(InstallButton12)

        InstallButton13 = QPushButton(text="Install Depot 13")
        InstallButton13.pressed.connect(lambda: self.Install(12))
        layout.addRow(InstallButton13)

        InstallButton14 = QPushButton(text="Install Depot 14")
        InstallButton14.pressed.connect(lambda: self.Install(13))
        layout.addRow(InstallButton14)
        """

        self.setTabText(1, "Installation")
        self.tab2.setLayout(layout)
        # self.setTabEnabled(1, False)

    def Install(self, index):
        Settings = Util.Read_Settings()
        if Util.IsWindows():
            subprocess.Popen(
                [
                    ".FOLON-Downgrader-Files/SteamFiles/steamcmd.exe",
                    "+login",
                    f'{Settings["Username"]}',
                    f"{self.PasswordEntry.text()}",
                    "+download_depot",
                    f"377160",
                    f"{self.Depots[index][0]}",
                    f"{self.Depots[index][1]}",
                    "+quit",
                ]
            )
        else:
            subprocess.Popen(
                [
                    ".FOLON-Downgrader-Files/SteamFiles/steamcmd.sh",
                    "+login",
                    f'{Settings["Username"]}',
                    f"{self.PasswordEntry.text()}",
                    "+download_depot",
                    f"377160",
                    f"{self.Depots[index][0]}",
                    f"{self.Depots[index][1]}",
                    "+quit",
                ]
            )

    def CopyFiles(self, Depot):
        try:
            if Util.IsWindows():
                SteamFiles = ".FOLON-Downgrader-Files/SteamFiles/steamapps/content/app_377160"
            else:
                SteamFiles = ".FOLON-Downgrader-Files/SteamFiles/linux32/steamapps/content/app_377160"
            if Util.IsBundled():
                Destination = "."
            else:
                Destination = "../Fallout 4"

            print("Started Depot:", Depot)
            for a in os.listdir(f"{SteamFiles}/depot_{Depot}"):
                if os.path.isdir(f"{SteamFiles}/depot_{Depot}/{a}"):
                    for b in os.listdir(f"{SteamFiles}/depot_{Depot}/{a}"):
                        if not os.path.isdir(f"{Destination}/{a}"):
                            os.mkdir(f"{Destination}/{a}")
                        shutil.move(
                            f"{SteamFiles}/depot_{Depot}/{a}/{b}",
                            f"{Destination}/{a}/{b}",
                        )
                else:
                    shutil.move(
                        f"{SteamFiles}/depot_{Depot}/{a}", f"{Destination}/{a}"
                    )
                print("moved:", a)
            shutil.rmtree(f"{SteamFiles}/depot_{Depot}")
            print("Finished Depot:", Depot)
        except:
            print("Skipped Depot:", Depot)


def main():
    app = QApplication(sys.argv)
    if Util.IsBundled():
        sshFile = ".FOLON-Downgrader-Files/FOLON.css"
    else:
        sshFile = "FOLON.css"
        if os.path.isdir(".FOLON-Downgrader-Files"):
            shutil.rmtree(".FOLON-Downgrader-Files")
    with open(sshFile, "r") as fh:
        app.setStyleSheet(fh.read())
    ex = MainWindow()
    ex.setMinimumWidth(ex.width())
    ex.setMinimumHeight(ex.height())
    ex.setMaximumWidth(ex.width())
    ex.setMaximumHeight(ex.height())
    ex.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
