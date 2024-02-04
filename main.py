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
        self.pushButton_f_o.clicked.connect(self.find_object)

    def find_object(self):
        toponym_to_find = self.lineEdit_f_o.text()
        print(toponym_to_find)

        geocoder_api_server = "http://geocode-maps.yandex.ru/1.x/"

        geocoder_params = {
            "apikey": "40d1649f-0493-4b70-98ba-98533de7710b",
            "geocode": toponym_to_find,
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
        toponym_coodrinates = toponym["Point"]["pos"]
        # Долгота и широта:
        toponym_longitude, toponym_lattitude = toponym_coodrinates.split(" ")

        delta = "0.005"

        # Собираем параметры для запроса к StaticMapsAPI:
        map_params = {
            "ll": ",".join([toponym_longitude, toponym_lattitude]),
            "spn": ",".join([delta, delta]),
            "l": "map"
        }

        map_api_server = "http://static-maps.yandex.ru/1.x/"
        # ... и выполняем запрос
        response = requests.get(map_api_server, params=map_params)

        map_file = "map.png"
        with open(map_file, "wb") as file:
            file.write(response.content)

        if not response:
            print("Ошибка выполнения запроса:")
            print("Http статус:", response.status_code, "(", response.reason, ")")
            sys.exit(1)

        self.pixmap = QPixmap(map_file)
        self.pict.setPixmap(self.pixmap)


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