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
        self.scaleNum = 0.0

        self.image_label = QtGui.QLabel()
        self.image_label.setStyleSheet("QLabel { background-color: #000; color: #eee}")
#        self.image_label.setScaledContents(True) # 不要放這個
        self.image_label.setSizePolicy(QtGui.QSizePolicy.Ignored, QtGui.QSizePolicy.Ignored) # WTF?
        self.image_label.setAlignment(QtCore.Qt.AlignCenter)
        layout = QtGui.QHBoxLayout()
        layout.setMargin(0)
        layout.addWidget(self.image_label)
        
        self.setLayout(layout)
        
        
        self.setWindowTitle("jkbiv")
        self.setStyleSheet("QLabel { background-color: #000; color: #eee}")
        self.resize(500,400)

#         self.status_bar = QtGui.QStatusBar(self)
#         self.setStatusBar(self.status_bar)
#         self.updateStatusBar()

        self.scaleNum = 1.0
        self.refreshImage()
 
        QtGui.QShortcut(QtGui.QKeySequence("q"), self, self.close)
        QtGui.QShortcut(QtGui.QKeySequence("Right"), self, self.nextImage)
        QtGui.QShortcut(QtGui.QKeySequence("Left"), self, self.prevImage)
        QtGui.QShortcut(QtGui.QKeySequence("s"), self, self.sortSwitcher)
        QtGui.QShortcut(QtGui.QKeySequence("f"), self, self.toggleFullScreen)

    def resizeEvent(self, resizeEvent):
        self.refreshImage()
    def updateStatusBar(self):
        self.status_bar.showMessage(' | '.join([self.image_lst.sortBy]))

    def refreshImage(self):
#        image = QtGui.QImage(self.image_lst.imageList[self.image_lst.currentImage])
#        scaledImage=image.scaled(self.image_label.size(), QtCore.Qt.KeepAspectRatio)
#        self.image_label.setPixmap(QtGui.QPixmap.fromImage(image))
        image = QtGui.QPixmap(self.image_lst.imageList[self.image_lst.currentImage])
        scaledImage=image.scaled(self.size(), QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
        self.image_label.setPixmap(scaledImage)
        # 記得更新title的檔名

    def nextImage(self):
        if 1 + self.image_lst.currentImage == len(self.image_lst.imageList):
            self.image_lst.currentImage = 0
        else:
            self.image_lst.currentImage += 1
        self.refreshImage()

    def prevImage(self):
        if self.image_lst.currentImage == 0:
            self.image_lst.currentImage = len(self.image_lst.imageList) - 1
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
        self.updateStatusBar()

    def sortByTime(self):
        filename=self.image_lst.imageList[self.image_lst.currentImage]
        self.image_lst.sortBy='Time'
        self.image_lst.genImagesList()
        self.image_lst.currentImage = self.image_lst.imageList.index(filename)
        self.updateStatusBar()

    def sortSwitcher(self):
        if self.image_lst.sortBy == 'Time':
            self.sortByName()
        else:
            self.sortByTime()

    def toggleFullScreen(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

app = QtGui.QApplication(sys.argv)
main_window = MainWindow()
main_window.show()
app.exec_()

# print(main_window.image_lst.imageList)
