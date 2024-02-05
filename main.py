import os
import sys



import requests
from PyQt5 import uic
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QWidget, QRadioButton
from PyQt5.QtCore import Qt


class Example(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        uic.loadUi('web.ui', self)
        self.map_file = 'map.png'
        self.setWindowTitle('Отображение карты')
        self.toponym_to_find = "Калуга, площадь Мира, 3"
        self.toponym_coodrinates = "36.243843 54.515280"
        self.kind = 'map'
        self.delta = 0.003
        self.screen_size = 600, 450
        self.getImage()
        self.pushButton_f_o.clicked.connect(self.find_object)
        self.unblock_find_btn.clicked.connect(self.unblock_finder)
        self.map_radio.clicked.connect(self.get_l)
        self.sat_radio.clicked.connect(self.get_l)
        self.hibrid_radio.clicked.connect(self.get_l)

    def unblock_finder(self):
        self.lineEdit_f_o.setEnabled(True)

    def get_l(self):
        self.kind = self.sender().text()
        self.getImage()

    def find_object(self):
        try:
            self.toponym_to_find = self.lineEdit_f_o.text()
            print(self.toponym_to_find)

            geocoder_api_server = "http://geocode-maps.yandex.ru/1.x/"

            geocoder_params = {
                "apikey": "40d1649f-0493-4b70-98ba-98533de7710b",
                "geocode": self.toponym_to_find,
                "format": "json"}

            response = requests.get(geocoder_api_server, params=geocoder_params)

            if not response:
                # обработка ошибочной ситуации
                pass

            # Преобразуем ответ в json-объект
            json_response = response.json()
            # Получаем первый топоним из ответа геокодера.
            toponym = json_response["response"]["GeoObjectCollection"][
                "featureMember"][0]["GeoObject"]
            # Координаты центра топонима:
            self.toponym_coodrinates = toponym["Point"]["pos"]
            self.getImage()
        except KeyError:
            pass
        except IndexError:
            pass
        finally:
            self.lineEdit_f_o.setDisabled(True)

    def getImage(self):
        toponym_longitude, toponym_lattitude = self.toponym_coodrinates.split(" ")
        api_server = "http://static-maps.yandex.ru/1.x/"
        map_params = {
            "ll": ",".join([toponym_longitude, toponym_lattitude]),
            "spn": ",".join([str(self.delta), str(self.delta)]),
            "l": self.kind
        }
        response = requests.get(api_server, params=map_params)

        with open(self.map_file, "wb") as file:
            file.write(response.content)

        if not response:
            print("Ошибка выполнения запроса:")
            print("Http статус:", response.status_code, "(", response.reason, ")")
            sys.exit(1)

        self.pixmap = QPixmap(self.map_file)
        self.pict.setPixmap(self.pixmap)

    def keyPressEvent(self, event):
        top_long, top_lat = float(self.toponym_coodrinates.split(" ")[0]), float(self.toponym_coodrinates.split(" ")[1])
        if event.key() == Qt.Key_PageUp:
            if self.delta > 0.0002:
                self.delta /= 2
        if event.key() == Qt.Key_PageDown:
            if self.delta < 0.1:
                self.delta *= 2
        if event.key() == Qt.Key_Up:
            if top_lat + (self.screen_size[1] * self.delta**2) < 80:
                top_lat += (self.screen_size[1] * self.delta**2)
        if event.key() == Qt.Key_Down:
            if top_lat - (self.screen_size[1] * self.delta**2) > 0:
                top_lat -= (self.screen_size[1] * self.delta**2)
        if event.key() == Qt.Key_Left:
            if top_long - (self.screen_size[1] * self.delta**2) > 0:
                top_long -= (self.screen_size[1] * self.delta**2)
        if event.key() == Qt.Key_Right:
            if top_long + (self.screen_size[1] * self.delta**2) < 80:
                top_long += (self.screen_size[1] * self.delta**2)
        self.toponym_coodrinates = f"{top_long} {top_lat}"
        self.getImage()

    def closeEvent(self, event):
        """При закрытии формы подчищаем за собой"""
        os.remove(self.map_file)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Example()
    ex.show()
    sys.exit(app.exec())