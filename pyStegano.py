from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog
from PyQt5.QtWidgets import QPushButton, QLabel, QLineEdit, QTextEdit
from PyQt5.QtGui import QPixmap, QImage, QColor
#from PyQt5 import uic
from pySteganoUI import Ui_MainWindow

class MainWindow(QMainWindow,Ui_MainWindow):
    def __init__(self):
        super().__init__()
        #uic.loadUi('pySteganoUI.ui',self)
        self.setupUi(self)
        self.btnClear.clicked.connect(self.btnClearClick)
        self.btnHide.clicked.connect(self.btnHideClick)
        self.btnLoad.clicked.connect(self.btnLoadClick)
        self.btnSave.clicked.connect(self.btnSaveClick)
        self.btnUnhide.clicked.connect(self.btnUnhideClick)
        pixmap = QPixmap(256,256)
        self.pixmapImg = pixmap.scaled(256, 256)
        self.labelPic.setPixmap(self.pixmapImg)

    def btnClearClick(self):
        self.textEdit.clear()

    def btnHideClick(self):
        self.keyA = int(self.editA.text())
        self.keyB = int(self.editB.text())
        self.keyC = self.pixmapImg.width() * self.pixmapImg.height()
        self.keySeed = int(self.editSeed.text())
        seed = self.keySeed
        s = self.textEdit.toPlainText()
        n = len(s)
        if n > 8192:
            n = 8192
        image = self.pixmapImg.toImage()
        seed = self.hide16bits(image, n, seed)
        for ch in s:
            seed = self.hide16bits(image, ord(ch), seed)
        self.pixmapImg = self.pixmapImg.fromImage(image)
        self.labelPic.setPixmap(self.pixmapImg)

    def btnLoadClick(self):
        fname = QFileDialog.getOpenFileName(self, 'Выбрать картинку', '')[0]
        if fname!='':
            pixmap = QPixmap(fname)
            self.pixmapImg = pixmap.scaled(256, 256)
            self.labelPic.setPixmap(self.pixmapImg)

    def btnSaveClick(self):
        fname = QFileDialog.getSaveFileName(self, 'Выбрать картинку', '')[0]
        if fname!='':
            self.pixmapImg.save(fname, format='BMP')

    def btnUnhideClick(self):
        self.keyA = int(self.editA.text())
        self.keyB = int(self.editB.text())
        self.keyC = self.pixmapImg.width() * self.pixmapImg.height()
        self.keySeed = int(self.editSeed.text())
        seed = self.keySeed
        image = self.pixmapImg.toImage()
        seed, n = self.unHide16bits(image, seed)
        if n>8192:
            n=8192
        s = ''
        for _ in range(n):
            seed, ch = self.unHide16bits(image, seed)
            s = s + chr(ch)
        self.textEdit.setText(s)

    def RND(self, a, b, c, seed):
        return (a * seed + b) % c

    def changePixel(self, image, bits54, bits32, bits10, seed):
        pos = self.RND(self.keyA, self.keyB, self.keyC, seed)
        x = pos % self.pixmapImg.width()
        y = pos // self.pixmapImg.height()
        rgb = image.pixelColor(x, y).getRgb()
        r = (rgb[0] & 252) | bits10
        g = (rgb[1] & 252) | bits32
        b = (rgb[2] & 252) | bits54
        image.setPixelColor(x, y, QColor.fromRgb(r, g, b))
        return pos

    def readPixel(self, image, seed):
        pos = self.RND(self.keyA, self.keyB, self.keyC, seed)
        x = pos % self.pixmapImg.width()
        y = pos // self.pixmapImg.height()
        rgb = image.pixelColor(x, y).getRgb()
        bits10 = rgb[0] & 3
        bits32 = rgb[1] & 3
        bits54 = rgb[2] & 3
        return pos, bits54, bits32, bits10

    def byteToBits(self, b8bit):
        bits76 = (b8bit >> 6) & 3
        bits54 = (b8bit >> 4) & 3
        bits32 = (b8bit >> 2) & 3
        bits10 = b8bit & 3
        return (bits76, bits54, bits32, bits10)

    def hide16bits(self, image, w16bit, seed):
        b1 = w16bit % 256
        b2 = w16bit // 256
        bitsFE, bitsDC, bitsBA, bits98 = self.byteToBits(b2)
        bits76, bits54, bits32, bits10 = self.byteToBits(b1)
        seed = self.changePixel(image, bits54, bits32, bits10, seed)
        seed = self.changePixel(image, bits98, bits76, bits54, seed)
        seed = self.changePixel(image, bitsDC, bitsBA, bits98, seed)
        seed = self.changePixel(image, bits10, bitsFE, bitsDC, seed)
        return seed

    def unHide16bits(self, image, seed):
        seed, bits54, bits32, bits10 = self.readPixel(image, seed)
        seed, bits98, bits76, bits54 = self.readPixel(image, seed)
        seed, bitsDC, bitsBA, bits98 = self.readPixel(image, seed)
        seed, bits10, bitsFE, bitsDC = self.readPixel(image, seed)
        b1 = (bits76 << 6) | (bits54 << 4) | (bits32 << 2) | bits10
        b2 = (bitsFE << 6) | (bitsDC << 4) | (bitsBA << 2) | bits98
        w16bit = (b2 << 8) | b1
        return seed, w16bit

app = QApplication([])
form1 = MainWindow()
form1.show()
app.exec()
