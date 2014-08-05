# -*- coding: utf-8 -*-
import sys, os, glob

# try:
#         from PySide import QtCore, QtGui
# except ImportError:
from PyQt4 import QtCore, QtGui
QtCore.Slot=QtCore.pyqtSlot
QtCore.Signal=QtCore.pyqtSignal
QtCore.Property=QtCore.pyqtProperty

def genSupportedExtensionList():
    formats = QtGui.QImageReader().supportedImageFormats()
    return [str(x)[2:-1] for x in formats]

SUPPORTED_EXT = genSupportedExtensionList()

# QListWidget
class ImageFileList(QtCore.QObject):
    def __init__(self):
        super(ImageFileList, self).__init__()

        self.sortBy='Name'
        
        # if argv exist, set dirPath according to it. Else, use getcwd()
        if len(sys.argv) > 1 and os.path.isfile(sys.argv[1]):
            self._dirPath = os.path.dirname(os.path.realpath(sys.argv[1]))
            self.currentImage=self.imageList.index(os.path.abspath(sys.argv[1]))
        else:
            self._dirPath = os.getcwd()
            self.currentImage=0  # 如果檔案不是圖檔該怎麼處理？或者有些檔案其實是圖檔但沒有副檔名？

        self.genImagesList()

    def genImagesList(self):
        images = []
        for extension in SUPPORTED_EXT:
            pattern=os.path.join(self._dirPath, "*.%s" % extension)
            images.extend(glob.glob(pattern))
        if self.sortBy == 'Name':
            images.sort()
        elif self.sortBy == 'Time':
            images.sort(key=lambda x: os.path.getmtime(x))
            
        self.imageList=images # [FIXME]如果當前目錄沒有任何圖片，就不要啟動app
 

class MainWindow(QtGui.QWidget):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.image_lst = ImageFileList()

        self.printer = QtGui.QPrinter()

        self.image_label = QtGui.QLabel()
        self.image_label.setStyleSheet("QLabel { background-color: #000; color: #eee}")
#        self.image_label.setScaledContents(True) # 不要放這個

        self.image_label.setAlignment(QtCore.Qt.AlignCenter)
        
        self.scroll_area = QtGui.QScrollArea()
        self.scroll_area.setStyleSheet("QLabel { background-color: #000; color: #eee}")
        self.scroll_area.setWidget(self.image_label)

        self.scroll_area.setWidgetResizable(True) # Magic

        self.scroll_area.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.scroll_area.setFrameShape(QtGui.QFrame.NoFrame) # Thanks for lzh~

        layout = QtGui.QVBoxLayout()
        layout.setMargin(0)
        layout.setSpacing(0)
        layout.addWidget(self.scroll_area)
        
        self.setLayout(layout)
        
        self.setWindowTitle("jkbiv")
        self.setStyleSheet("QLabel { background-color: #000; color: #eee}")
        self.resize(500,400)

#         self.status_bar = QtGui.QStatusBar(self)
#         self.setStatusBar(self.status_bar)
#         self.updateStatusBar()
        self.notify_label =QtGui.QLabel("", self)
        self.notify_label.setStyleSheet('''color:#fff;
        background-color:rgba(0,0,0,100);
        border:1px solid #fff;
        border-radius:3px;
        text-align:center;''')
        self.notify_label.setAlignment(QtCore.Qt.AlignCenter)
        self.notify_label.hide()

        self.scaleNum = 1.0
        self.zoomMode = 'fitToWindow'
        self.refreshImage()
        
        QtGui.QShortcut(QtGui.QKeySequence("q"), self, self.close)
        QtGui.QShortcut(QtGui.QKeySequence("Right"), self, self.nextImage)
        QtGui.QShortcut(QtGui.QKeySequence("Left"), self, self.prevImage)
        QtGui.QShortcut(QtGui.QKeySequence("s"), self, self.sortSwitcher)
        QtGui.QShortcut(QtGui.QKeySequence("f"), self, self.toggleFullScreen)
        QtGui.QShortcut(QtGui.QKeySequence("="), self, self.zoomIn)
        QtGui.QShortcut(QtGui.QKeySequence("-"), self, self.zoomOut)
        QtGui.QShortcut(QtGui.QKeySequence("1"), self, self.origianlSize)
        QtGui.QShortcut(QtGui.QKeySequence("w"), self, self.fitToWindow)

    def resizeEvent(self, resizeEvent): # Qt
        # [FIXME]如果目前縮放模式不是fit to window，記得不要resize image_label
#        self.image_label.resize(self.size())
        self.refreshImage()
        
    def refreshImage(self):
        self.image = QtGui.QPixmap(self.image_lst.imageList[self.image_lst.currentImage])
        if self.zoomMode == 'fitToWindow':
            self.fitToWindow()
        else:
            scaledImage = self.image.scaled(self.image.size() * self.scaleNum,
                                            QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
            self.image_label.setPixmap(scaledImage)
        # 記得更新title的檔名

    def fitToWindow(self):
        self.zoomMode = 'fitToWindow'
        if self.image.width() < self.scroll_area.width() and self.image.height() < self.scroll_area.height():
            self.image_label.setPixmap(self.image)
        else:
            scaledImage = self.image.scaled(self.scroll_area.size(),
                                     QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
            self.image_label.setPixmap(scaledImage)
        self.scaleNum = self.image_label.width() / self.image.width() # useless/nonsense
        self.sendNotify("Fit to Window", 500)
    
    def origianlSize(self):
        self.zoomMode = 'free'
        self.scaleNum = 1
        self.sendNotify("Original Size", 500)
        self.refreshImage()
        
    def zoomIn(self):
        self.zoomMode = 'free'
        self.scaleNum *= 1.1
        self.sendNotify("{percent:.0%}".format(percent=self.scaleNum), 500)
        self.refreshImage()

    def zoomOut(self):
        self.zoomMode = 'free'
        self.scaleNum *= 0.9
        self.sendNotify("{percent:.0%}".format(percent=self.scaleNum), 500)
        self.refreshImage()
        
    def nextImage(self):
        if 1 + self.image_lst.currentImage == len(self.image_lst.imageList):
            self.image_lst.currentImage = 0
            self.sendNotify("Last document reached, continuing on first document.")
        else:
            self.image_lst.currentImage += 1
        self.refreshImage()

    def prevImage(self):
        if self.image_lst.currentImage == 0:
            self.image_lst.currentImage = len(self.image_lst.imageList) - 1
            self.sendNotify("First document reached, continuing on last document.")
        else:
            self.image_lst.currentImage -= 1
        self.refreshImage()

    def sortByName(self):
        # Because image_lst.currentImage is just a integer, after re-sort the list,
        # you will get wrong picture with the old integer.
        filename=self.image_lst.imageList[self.image_lst.currentImage]
        self.image_lst.sortBy='Name'
        self.image_lst.genImagesList()
        self.image_lst.currentImage = self.image_lst.imageList.index(filename)
        self.sendNotify("Sorting by Name")

    def sortByTime(self):
        filename=self.image_lst.imageList[self.image_lst.currentImage]
        self.image_lst.sortBy='Time'
        self.image_lst.genImagesList()
        self.image_lst.currentImage = self.image_lst.imageList.index(filename)
        self.sendNotify("Sorting by Time")

    def sortSwitcher(self):
        if self.image_lst.sortBy == 'Time':
            self.sortByName()
        else:
            self.sortByTime()

    def toggleFullScreen(self):
        if self.isFullScreen():
            self.showNormal()
            self.sendNotify("Fullscreen off")
        else:
            self.showFullScreen()
            self.sendNotify("Fullscreen on")

    def paintEvent(self, event): # Qt
        w = self.notify_label.width()
        h = self.notify_label.height()

        x = (self.rect().width()  - w)/2.0
        y = (self.rect().height() - h)/2.0
        self.notify_label.setGeometry(x,y,w,h)

    def sendNotify(self, string, duration = 2000):
        label = self.notify_label
        label.setText(string)
        label.adjustSize()
        x = label.width() + 20
        y = label.height() + 10
        label.resize(x, y)
        label.show()
        QtCore.QTimer.singleShot(duration, lambda: label.hide())

        
app = QtGui.QApplication(sys.argv)
main_window = MainWindow()
main_window.show()
app.exec_()

# print(main_window.image_lst.imageList)
