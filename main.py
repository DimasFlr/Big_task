import os
import sys

import requests
from PyQt5 import uic
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QWidget, QLabel
from PyQt5.QtCore import Qt


class Example(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        uic.loadUi('web.ui', self)
        self.setWindowTitle('Отображение карты')
        self.adress = "площадь Мира, 3" #изменить
        self.coords = [54.515280, 36.243843]
        self.delta = 0.003
        self.screen_size = 600, 450
        self.getImage()

    def getImage(self):
        api_server = "http://static-maps.yandex.ru/1.x/"
        params = {
            "ll": ",".join([str(self.coords[1]), str(self.coords[0])]),
            "spn": ",".join([str(self.delta), str(self.delta)]),
            "l": "map"
        }
        response = requests.get(api_server, params=params)

        map_file = "map.png"
        with open(map_file, "wb") as file:
            file.write(response.content)

        if not response:
            print("Ошибка выполнения запроса:")
            print("Http статус:", response.status_code, "(", response.reason, ")")
            sys.exit(1)

        self.pixmap = QPixmap(map_file)
        self.pict.setPixmap(self.pixmap)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_PageUp:
            if self.delta > 0.0002:
                self.delta /= 2
        elif event.key() == Qt.Key_PageDown:
            if self.delta < 0.1:
                self.delta *= 2
        elif event.key() == Qt.Key_Up:
            if self.coords[0] + (self.screen_size[1] * self.delta**2) < 80:
                self.coords[0] += (self.screen_size[1] * self.delta**2)
        elif event.key() == Qt.Key_Down:
            if self.coords[0] - (self.screen_size[1] * self.delta**2) > 0:
                self.coords[0] -= (self.screen_size[1] * self.delta**2)
        elif event.key() == Qt.Key_Left:
            if self.coords[1] - (self.screen_size[1] * self.delta**2) > 0:
                self.coords[1] -= (self.screen_size[1] * self.delta**2)
        elif event.key() == Qt.Key_Right:
            if self.coords[1] + (self.screen_size[1] * self.delta**2) < 80:
                self.coords[1] += (self.screen_size[1] * self.delta**2)
        self.getImage()

    def closeEvent(self, event):
        """При закрытии формы подчищаем за собой"""
        os.remove(self.map_file)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Example()
    ex.show()
    sys.exit(app.exec())