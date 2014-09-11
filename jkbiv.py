#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys, os, glob, importlib.machinery, subprocess
from PIL import Image

CONFIG_PATH = os.path.expanduser("~/.config/jkbivrc.py")

# Shell command
LAST_COMMAND = ""
# All commands on system
COMMANDS = []

# Exif
ORIENTATION_KEY=274
ROTATE_VAR={
    3:180,
    6:90,
    8:270}
CREATED_DATE_KEY=36868

def loadConfigFile():
    config_loader=importlib.machinery.SourceFileLoader("configFile", os.path.expanduser(CONFIG_PATH))
    global CONFIG
    CONFIG = config_loader.load_module("configFile")

try: 
    loadConfigFile()
except FileNotFoundError:
    if not os.path.exists(os.path.dirname(CONFIG_PATH)):
        os.makedirs(os.path.dirname(CONFIG_PATH))
    import shutil
    if os.path.exists("./jkbivrc.py"):
        shutil.copyfile("./jkbivrc.py", CONFIG_PATH)
    else:
        shutil.copyfile("/usr/share/jkbiv/jkbivrc.py", CONFIG_PATH)
    loadConfigFile()
    
# try:
#         from PySide import QtCore, QtGui
# except ImportError:
from PyQt4 import QtCore, QtGui
QtCore.Slot=QtCore.pyqtSlot
QtCore.Signal=QtCore.pyqtSignal
QtCore.Property=QtCore.pyqtProperty


# Mouse wheel behavior
mouseWheelBehavior=CONFIG.mouseWheelBehavior


def genSupportedExtensionList():
    formats = QtGui.QImageReader().supportedImageFormats()
    return [str(x)[2:-1] for x in formats]

SUPPORTED_EXT = genSupportedExtensionList()

# QListWidget
class ImageFileList(QtCore.QObject):
    def __init__(self, directoryPath, fileName=None):
        """I won't check the validation of input path.
        Input path should be an absolute path."""
        super(ImageFileList, self).__init__()

        self.sortBy=CONFIG.sortBy

        # handle inputed directoryPath
        self._dirPath = directoryPath
        
        # gen imageList
        self.genImagesList()
        # gen currentIndex
        if fileName:
            self.currentIndex = self.imageList.index(os.path.join(directoryPath, fileName))
        elif os.path.isdir(directoryPath):
            self.currentIndex=0

    def genImagesList(self):
        "generate _dirPath, imageList"
        images = []
        for ext in SUPPORTED_EXT:
            pattern=os.path.join(self._dirPath, "*.%s" % ext)
            images.extend(glob.glob(pattern))
        if self.sortBy == 'Name':
            images.sort(key=str.lower)
        elif self.sortBy == 'Time':
            images.sort(key=lambda x: os.path.getmtime(x))
            
        # If no picture file exists in path, exit the program.
        if len(images) == 0:
            sys.exit("The path doesn't have any picture.")
        else:
            self.imageList=images


class MainWindow(QtGui.QWidget):
    def __init__(self, imageFileList):
        super(MainWindow, self).__init__()

        self.image_lst = imageFileList
        self.printer = QtGui.QPrinter()

        class ImageLabel(QtGui.QLabel):
            def __init__(self, main_window_instance):
                super(ImageLabel, self).__init__()
                self.setAlignment(QtCore.Qt.AlignCenter)
                self.main_window_instance = main_window_instance
                # desktop = QtGui.QDesktopWidget()
                # self.desktopSize = desktop.availableGeometry(desktop.primaryScreen())

            def wheelEvent(self, event):
                win=self.main_window_instance
                hbar=win.scroll_area.horizontalScrollBar()
                vbar=win.scroll_area.verticalScrollBar()
                modifiers = QtGui.QApplication.keyboardModifiers()
                if mouseWheelBehavior == 'Zoom' or modifiers == QtCore.Qt.ControlModifier:
                    if event.delta() > 0:
                         win.zoomIn()
                    else:
                         win.zoomOut()
                else:
                    if event.delta() > 0:
                        win.prevImage()
                    else:
                        win.nextImage()

            def mousePressEvent(self, event):
                self.__mouseOriginalX = None
                self.__mouseOriginalY = None
                if event.button() == QtCore.Qt.LeftButton:
                    self.__mouseOriginalX = event.globalX()
                    self.__mouseOriginalY = event.globalY()
                super(ImageLabel, self).mousePressEvent(event)

            def updateMouseOriginal(self):
                self.__mouseOriginalX = self.cursor.pos().x()
                self.__mouseOriginalY = self.cursor.pos().y()
                self.currentX = self.cursor.pos().x()
                self.currentY = self.cursor.pos().y()

            def mouseMoveEvent(self, event):
                # Following magic make mouse infinitely drag~
                self.cursor = QtGui.QCursor()
                x = self.cursor.pos().x()
                y = self.cursor.pos().y()
                if x > DESKTOP_WIDTH - 2:
                    self.cursor.setPos(0,y)
                    self.updateMouseOriginal()
                elif x < 1:
                    self.cursor.setPos(DESKTOP_WIDTH, y)
                    self.updateMouseOriginal()
                elif y > DESKTOP_HEIGHT - 2:
                    self.cursor.setPos(x, 0)
                    self.updateMouseOriginal()
                elif y < 1:
                    self.cursor.setPos(x, DESKTOP_HEIGHT)
                    self.updateMouseOriginal()
                else:
                    self.currentX = event.globalX()
                    self.currentY = event.globalY()

                if event.buttons() == QtCore.Qt.LeftButton:
                    barX = self.main_window_instance.scroll_area.horizontalScrollBar()
                    barY = self.main_window_instance.scroll_area.verticalScrollBar()
                    barX.setValue(barX.value() - (self.currentX - self.__mouseOriginalX))
                    barY.setValue(barY.value() - (self.currentY - self.__mouseOriginalY))

                    self.__mouseOriginalX = self.currentX
                    self.__mouseOriginalY = self.currentY

                super(ImageLabel, self).mousePressEvent(event)


        self.scroll_area = QtGui.QScrollArea()
        self.image_label = ImageLabel(self)
        self.scroll_area.setStyleSheet("QLabel { background-color: #000; color: #eee}")
        self.scroll_area.setWidget(self.image_label)

        self.scroll_area.setWidgetResizable(True) # Magic

        self.scroll_area.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.scroll_area.setFrameShape(QtGui.QFrame.NoFrame) # Thanks for lzh~
        self.scroll_area.horizontalScrollBar().setSingleStep(20)
        self.scroll_area.verticalScrollBar().setSingleStep(20)

        layout = QtGui.QVBoxLayout()
        layout.setMargin(0)
        layout.setSpacing(0)
        layout.addWidget(self.scroll_area)

        self.setLayout(layout)

        self.setWindowTitle("jkbiv")

        self.resize(CONFIG.width, CONFIG.height)

#         self.status_bar = QtGui.QStatusBar(self)
#         self.setStatusBar(self.status_bar)
#         self.updateStatusBar()
        self.notify_label =QtGui.QLabel("", self)
        self.notify_label.setStyleSheet('''color:#fff;
        background-color:rgba(0,0,0,100);
        border:1px solid #fff;
        border-radius:3px;
        padding:5px;
        text-align:center;''')
        self.notify_label.setAlignment(QtCore.Qt.AlignCenter)
        self.notify_label.hide()

        self.info_label = QtGui.QLabel("",self)
        self.info_label.setTextFormat(QtCore.Qt.RichText)
        self.info_label.setStyleSheet('''color:#fff;
        background-color:rgba(0,0,0,100);
        text-align:left;
        padding:10px;''')
        self.ifShowInfoLabels=CONFIG.ifShowInfoLabels
        self.ifShowStatusLabels=CONFIG.ifShowStatusLabels
        self.info_label.hide()
        
        self.scaleNum = 1.0
        self.zoomMode = 'fitToWindow'
        self.rememberZoomMode = CONFIG.rememberZoomMode
        self.loadImageFile()

        # Key-bindings
        for k in CONFIG.keys:
            QtGui.QShortcut(QtGui.QKeySequence(k[0]), self, eval("self." + k[1]))



    def resizeEvent(self, resizeEvent): # Qt
        # [FIXME]如果目前縮放模式不是fit to window，記得不要resize image_label
        #        self.image_label.resize(self.size())
        self.refreshImage()

    def loadImageFile(self):
        self.directoryPath = self.image_lst.imageList[self.image_lst.currentIndex]
        self.fileName = os.path.basename(self.directoryPath)
        self.image = QtGui.QPixmap(self.directoryPath)
        self.imageDate = ""

        try:
            exif_data = Image.open(self.directoryPath)._getexif()
            if ORIENTATION_KEY in exif_data:
                orientation = exif_data[ORIENTATION_KEY]
                if orientation in ROTATE_VAR:
                # Translate raw orientation value into actual orientation degrees
                    angle = ROTATE_VAR[orientation]
                    self.image = self.image.transformed(QtGui.QTransform().rotate(angle))
            if CREATED_DATE_KEY in exif_data:
                self.imageDate = " | " + exif_data[CREATED_DATE_KEY]
        except:
            None
        
        self.imageResolution = "{} x {}".format(self.image.width(), self.image.height())
        self.refreshImage()

    def refreshImage(self):
        if self.zoomMode == 'fitToWindow':
            if self.image.width() < self.scroll_area.width() and self.image.height() < self.scroll_area.height():
                self.image_label.setPixmap(self.image)
                self.scaledImage = self.image
            else:
                self.scaledImage = self.image.scaled(self.scroll_area.size(),
                                                QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
                self.image_label.setPixmap(self.scaledImage)
        else: # self.zoomMode == 'free'
            self.scaledImage = self.image.scaled(self.image.size() * self.scaleNum,
                                            QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
            self.image_label.setPixmap(self.scaledImage)
        self.scaleNum = self.scaledImage.width() / self.image.width()
        self.updateInfoLabels()
        # Update scale percentage
        self.scalePercentage = "{percent:.0%}".format(percent=self.scaleNum)
        # Update title text.
        self.setWindowTitle("{} ({}) {}".format(self.fileName, self.imageResolution, self.scalePercentage))

    def updateInfoLabels(self):
        ### Information Label
        if self.ifShowInfoLabels:
            self.info_label.setText(
                '''<span style='color:#ffaf5f'>[{}/{}]</span> {}<br>
                {} {}
                {}'''\
            .format(self.image_lst.currentIndex + 1, len(self.image_lst.imageList), self.fileName,
                    self.imageResolution, self.imageDate,
                    self.genStatusLabels()))
            self.info_label.adjustSize()
            w=self.width()
            h=self.info_label.height()
            x=0
            y=self.rect().height() - h
            self.info_label.setGeometry(x,y,w,h)
            self.info_label.show()
        else:
            self.info_label.hide()

    def toggleInfoLabels(self):
        self.ifShowInfoLabels = not(self.ifShowInfoLabels)
        self.updateInfoLabels()


    def toggleStatusLabels(self):
        self.ifShowStatusLabels = not(self.ifShowStatusLabels)
        self.updateInfoLabels()

    def fitToWindow(self):
        self.zoomMode = 'fitToWindow'
        self.refreshImage()
        self.sendNotify("Fit to Window (%s)" % self.scalePercentage, 500)

    def origianlSize(self):
        self.zoomMode = 'free'
        self.scaleNum = 1
        self.refreshImage()
        self.sendNotify("Original Size (100%)", 500)

    def zoomIn(self):
        self.zoomMode = 'free'
        self.scaleNum *= 1.1
        self.refreshImage()
        self.sendNotify(self.scalePercentage, 500)

    def zoomOut(self):
        self.zoomMode = 'free'
        self.scaleNum *= 0.9
        self.refreshImage()
        self.sendNotify(self.scalePercentage, 500)

    def toggleRememberZoomMode(self):
        self.rememberZoomMode = not(self.rememberZoomMode)
        self.sendNotify("Remenber Zoom Mode" if self.rememberZoomMode else "Always Fit to Window")
        self.updateInfoLabels()
        
    def scrollRight(self, step = 20):
        bar=self.scroll_area.horizontalScrollBar()
        bar.setValue(bar.value() + step)

    def scrollLeft(self, step = 20):
        bar=self.scroll_area.horizontalScrollBar()
        bar.setValue(bar.value() - step)

    def scrollUp(self, step = 20):
        bar=self.scroll_area.verticalScrollBar()
        bar.setValue(bar.value() - step)

    def scrollDown(self, step = 20):
        bar=self.scroll_area.verticalScrollBar()
        bar.setValue(bar.value() + step)

    def ifScaledImageIsSmall(self):
        if self.scaledImage.height() < self.scroll_area.height() + 2 and self.scaledImage.width() < self.scroll_area.width() + 2:
            return True
        else:
            return False

    def smartRight(self):
        if self.ifScaledImageIsSmall():
            self.nextImage()
        else:
            self.scrollRight()

    def smartLeft(self):
        if self.ifScaledImageIsSmall():
            self.prevImage()
        else:
            self.scrollLeft()

    def smartUp(self):
        if self.ifScaledImageIsSmall():
            self.prevImage()
        else:
            self.scrollUp()

    def smartDown(self):
        if self.ifScaledImageIsSmall():
            self.nextImage()
        else:
            self.scrollDown()

    def nextImage(self):
        if 1 + self.image_lst.currentIndex == len(self.image_lst.imageList):
            self.image_lst.currentIndex = 0
            self.sendNotify("Last document reached, continuing on first document.")
        else:
            self.image_lst.currentIndex += 1

        if not(self.rememberZoomMode):
            self.zoomMode = 'fitToWindow'

        self.loadImageFile()

    def prevImage(self):
        if self.image_lst.currentIndex == 0:
            self.image_lst.currentIndex = len(self.image_lst.imageList) - 1
            self.sendNotify("First document reached, continuing on last document.")
        else:
            self.image_lst.currentIndex -= 1

        if not(self.rememberZoomMode):
            self.zoomMode = 'fitToWindow'

        self.loadImageFile()

    def sortByName(self):
        # Because image_lst.currentIndex is just a integer, after re-sort the list,
        # you will get wrong picture with the old integer.
        filename=self.image_lst.imageList[self.image_lst.currentIndex]
        self.image_lst.sortBy='Name'
        self.image_lst.genImagesList()
        self.image_lst.currentIndex = self.image_lst.imageList.index(filename)
        self.sendNotify("Sorting by Name")
        self.updateInfoLabels()

    def sortByTime(self):
        filename=self.image_lst.imageList[self.image_lst.currentIndex]
        self.image_lst.sortBy='Time'
        self.image_lst.genImagesList()
        self.image_lst.currentIndex = self.image_lst.imageList.index(filename)
        self.sendNotify("Sorting by Time")
        self.updateInfoLabels()

    def sortSwitcher(self):
        if self.image_lst.sortBy == 'Time':
            self.sortByName()
        else:
            self.sortByTime()

    def toggleFullScreen(self):
        if self.isFullScreen():
            self.showNormal()
            self.sendNotify("Fullscreen Off")
        else:
            self.showFullScreen()
            self.sendNotify("Fullscreen On")

#    def paintEvent(self, event): # Qt

    def sendNotify(self, string, duration = 2000):
        label = self.notify_label
        label.setText(string)
        label.adjustSize()
        ### Update notification label position
        w = self.notify_label.width()
        h = self.notify_label.height()

        x = (self.rect().width()  - w)/2.0
        y = (self.rect().height() - h)/2.0
        self.notify_label.setGeometry(x,y,w,h)

        label.show()
        QtCore.QTimer.singleShot(duration, lambda: label.hide())

    def genStatusLabels(self):
        if self.ifShowStatusLabels:
            if self.image_lst.sortBy == "Name":
                sort_by=("Name", "#005f87", "#c3c9f8")
            else:
                sort_by=("Time", "#a40000", "#ffafaf")
    
            if self.zoomMode == "fitToWindow":
                zoom_mode=("Fit", "#fff", "#555")
            elif self.scaleNum == 1:
                zoom_mode=("1:1", "#fff", "#555")
            else:
                zoom_mode=("Free", "#fff", "#555")
    
            if self.rememberZoomMode:
                remember=("R", "#875f00", "#ffd700")
            else:
                remember=None
    
            labels=[]
            for l in [sort_by, zoom_mode, remember]:
                if l is not None:
                    labels = labels + ['''<span style='color:{0};
                    background-color:{1};
                    padding:15px;
                    white-space:pre;'> {2} </span>
                    '''.format(l[1],l[2],l[0])]
    
            return "<div align=right>" + " ".join(labels) + "</div>"
        else:
            return ""

    def deleteFile(self):
        msgBox = QtGui.QMessageBox()
        msgBox.setText("Are you sure to <b>delete</b> this picture?<br>\
        (Notice this action <b>cannot be undone!</b>)")
        msgBox.setStandardButtons(QtGui.QMessageBox.Yes | QtGui.QMessageBox.Cancel)
        msgBox.setDefaultButton(QtGui.QMessageBox.Cancel)
        reply=msgBox.exec_()
        if reply == QtGui.QMessageBox.Yes:
            os.remove(self.directoryPath)
            del self.image_lst.imageList[self.image_lst.currentIndex]
            if len(self.image_lst.imageList) == self.image_lst.currentIndex:
                self.image_lst.currentIndex = 0
            self.loadImageFile()
            self.sendNotify("File Deleted.")
        else:
            self.sendNotify("Canceled.")

    def renameFile(self):
        dirPath = self.image_lst._dirPath
        fileName, fileExt = os.path.splitext(self.fileName)
        newFileName, ok = QtGui.QInputDialog.getText(self,
                                                     "Rename",
                                                     "Please input new filename:",
                                                     QtGui.QLineEdit.Normal,
                                                     fileName)
        if ok and newFileName != '':
            newFullFileName = os.path.join(dirPath, (newFileName + fileExt))
            os.rename(self.fullFileName, newFullFileName)
            self.fullFileName = newFullFileName
            self.image_lst.imageList[self.image_lst.currentIndex] = newFullFileName
            self.loadImageFile()
            self.sendNotify("Renamed to " + newFileName)

    @QtCore.Slot(str, bool)
    def _runShellCommand(self, inputCommand, sync=False):
        global LAST_COMMAND
        pyRun = "call" if sync == True else "Popen"
        if inputCommand != "":
            listedCommand=[] # list
            for x in inputCommand.split(" "):
                if "%s" in x:
                    listedCommand.append(x.replace("%s", self.fullFileName))
                else:
                    listedCommand.append(x)
                    
            if "%s" in inputCommand:
                eval("subprocess." + pyRun)(listedCommand,
                                            stdout=subprocess.DEVNULL,
                                            stderr=subprocess.DEVNULL)
            else:
                eval("subprocess." + pyRun)([inputCommand, self.fullFileName],
                                            stdout=subprocess.DEVNULL,
                                            stderr=subprocess.DEVNULL)
        LAST_COMMAND = inputCommand

    def runShellCommand(self):
        dialog = RunShellCommandDialog(self, False)

    def runShellCommandSynchronously(self):
        dialog = RunShellCommandDialog(self, True)
        self.loadImageFile()

    def duplicateWindow(self):
        subprocess.Popen(["jkbiv", self.fullFileName],
                         stdout=subprocess.DEVNULL,
                         stderr=subprocess.DEVNULL)

    def copyFilePath(self):
        global app
        app.clipboard().setText(self.fullFileName)
        self.sendNotify("File Path Copied")
        
    
class RunShellCommandDialog(QtGui.QDialog):
    commandSignal = QtCore.Signal(str, bool)
    def __init__(self, parentInstance, sync=False):
        super(RunShellCommandDialog, self).__init__()
        self.sync = sync        

        if len(COMMANDS) == 0:
            self.genCommandList()
            print(len(COMMANDS))

        # completer + list model + line edit
        model = QtGui.QStringListModel()
        model.setStringList(COMMANDS)
        completer = QtGui.QCompleter()
        completer.setModel(model)
        label = QtGui.QLabel("Run shell command (You can use %s for filename):")
        self.line_edit = QtGui.QLineEdit()
        self.line_edit.setCompleter(completer)
        self.line_edit.setText(LAST_COMMAND)
        label.setBuddy(self.line_edit)

        self.button_box = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel)
        
        # Oh Jesus look these bizarre Signals & Slots
        self.button_box.accepted.connect(self.clickHandler)
        self.commandSignal.connect(parentInstance._runShellCommand)
        self.button_box.rejected.connect(self.close)

        horizontal_layout=QtGui.QHBoxLayout()
        horizontal_layout.addWidget(self.line_edit)
        horizontal_layout.addWidget(self.button_box)
        main_layout=QtGui.QVBoxLayout()
        main_layout.addWidget(label)
        main_layout.addLayout(horizontal_layout)
        self.setLayout(main_layout)
        self.setWindowTitle("Run Shell Command")
        self.exec_()

    def clickHandler(self):
        self.commandSignal.emit(self.line_edit.text(), self.sync)
        self.close()

    def genCommandList(self):
        global COMMANDS
        for path in os.getenv('PATH').split(':'):
            if os.path.isdir(path):
                COMMANDS.extend(os.listdir(path))
        COMMANDS = list(set(COMMANDS))



# if argv exist, set dirPath according to it. Else, use getcwd()

# [FIXME] argument can be:
# - None
# - Filename
# - Directory path
# - File path
# - Directory path
global image_file_list

global ARGV_1
if len(sys.argv) > 1:
    ARGV_1 = os.path.abspath(os.path.expanduser(sys.argv[1]))
    if os.path.isfile(ARGV_1):
        fileNameWithoutExt, fileExt = os.path.splitext(ARGV_1)
        try:
            fileExt in SUPPORTED_EXT
        except IndexError:
        # if the input file is not a support image format (decide by extension)
            sys.exit("This is not a supported image file format (or extension).")

        directoryPath   = os.path.dirname(ARGV_1)
        fileName        = os.path.basename(ARGV_1)
        image_file_list = ImageFileList(directoryPath, fileName)
        
    elif os.path.isdir(ARGV_1):
        image_file_list = ImageFileList(ARGV_1)
else:
    image_file_list = ImageFileList(os.getcwd())
    # [FIXME] How about a real image file, but without file extension?


app = QtGui.QApplication(sys.argv)

if os.path.exists('icons/'):
    ICON_PATH = 'icons/'
else:
    ICON_PATH = '/usr/share/jkbiv/icons/'
    
app_icon = QtGui.QIcon()
app_icon.addFile(ICON_PATH + '16.png', QtCore.QSize(16,16))
app_icon.addFile(ICON_PATH + '22.png', QtCore.QSize(22,22))
app_icon.addFile(ICON_PATH + '48.png', QtCore.QSize(48,48))
app_icon.addFile(ICON_PATH + '256.png', QtCore.QSize(256,256))
app.setWindowIcon(app_icon)

DESKTOP_HEIGHT = app.desktop().height()
DESKTOP_WIDTH = app.desktop().width()
main_window = MainWindow(image_file_list)
main_window.show()

if CONFIG.fullScreen:
    main_window.showFullScreen()

app.exec_()

