import sys

import psycopg2
from PyQt6.QtCore import QSize
from PyQt6.QtWidgets import (
    QApplication,
    QComboBox,
    QDialog,
    QGridLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QStyledItemDelegate,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from config import DATABASE_URL

# Подключение к базе данных
connection = psycopg2.connect(DATABASE_URL)


# Создание кастомного делегата для ячеек таблицы с отступами
class PaddedItemDelegate(QStyledItemDelegate):
    def __init__(self, padding=4):
        super().__init__()
        self.padding = padding

    def paint(self, painter, option, index):
        option.rect.adjust(self.padding, self.padding, -self.padding, -self.padding)
        super().paint(painter, option, index)

    def sizeHint(self, option, index):
        size = super().sizeHint(option, index)
        size += QSize(self.padding * 2, self.padding * 2)
        return size


# Класс приложения
class ToyStoreApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Магазин игрушек")
        self.setGeometry(100, 100, 960, 540)

        self.init_ui()

    def init_ui(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout()

        # Макет для поиска
        self.search_layout = QHBoxLayout()
        self.search_label = QLabel("Поиск:")
        self.search_input = QLineEdit()
        self.search_input.setFixedHeight(30)
        self.search_button = QPushButton("Найти")
        self.search_button.setFixedHeight(30)
        self.search_button.clicked.connect(self.search_toys)
        self.search_layout.addWidget(self.search_label)
        self.search_layout.addWidget(self.search_input)
        self.search_layout.addWidget(self.search_button)
        self.layout.addLayout(self.search_layout)

        # Кнопка сброса поиска
        self.reset_button = QPushButton("Сбросить поиск")
        self.reset_button.setFixedHeight(30)
        self.reset_button.clicked.connect(self.reset_search)
        self.reset_button.setVisible(False)
        self.search_layout.addWidget(self.reset_button)

        # Макет для сортировки
        self.sort_layout = QHBoxLayout()
        self.sort_label = QLabel("Сортировка:")
        self.sort_combo = QComboBox()
        self.sort_combo.setFixedHeight(30)
        self.sort_combo.addItems(
            [
                "По номеру (возр.)",
                "По номеру (убыв.)",
                "По названию (возр.)",
                "По названию (убыв.)",
                "По типу (возр.)",
                "По типу (убыв.)",
                "По материалу (возр.)",
                "По материалу (убыв.)",
                "По цвету (возр.)",
                "По цвету (убыв.)",
                "По цене (возр.)",
                "По цене (убыв.)",
            ]
        )
        self.sort_button = QPushButton("Сортировать")
        self.sort_button.setFixedHeight(30)
        self.sort_button.clicked.connect(self.sort_toys)
        self.sort_layout.addWidget(self.sort_label)
        self.sort_layout.addWidget(self.sort_combo)
        self.sort_layout.addWidget(self.sort_button)
        self.layout.addLayout(self.sort_layout)

        # Таблица
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(
            ["ID", "Название", "Тип", "Материал", "Цвет", "Цена"]
        )
        # Установка кастомного делегата
        padded_delegate = PaddedItemDelegate(padding=12)
        self.table.setItemDelegate(padded_delegate)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.Stretch
        )
        self.layout.addWidget(self.table)

        # Макет для кнопок управления
        self.button_layout = QHBoxLayout()
        self.delete_button = QPushButton("Удалить игрушку")
        self.delete_button.setFixedHeight(40)
        self.delete_button.clicked.connect(self.delete_toy)
        self.button_layout.addWidget(self.delete_button)
        self.edit_button = QPushButton("Изменить игрушку")
        self.edit_button.setFixedHeight(40)
        self.edit_button.clicked.connect(self.edit_toy)
        self.button_layout.addWidget(self.edit_button)
        self.add_button = QPushButton("Добавить игрушку")
        self.add_button.setFixedHeight(40)
        self.add_button.clicked.connect(self.add_toy)
        self.button_layout.addWidget(self.add_button)
        self.layout.addLayout(self.button_layout)

        self.central_widget.setLayout(self.layout)
        self.load_toys()

    # Обработка события изменения размеров окна
    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.sort_combo.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )

    # Загрузка игрушек
    def load_toys(self):
        self.table.setRowCount(0)
        cursor = connection.cursor()
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS toys (id SERIAL PRIMARY KEY, name TEXT, type TEXT, material TEXT, color TEXT, price REAL)"
        )
        cursor.execute("SELECT COUNT(*) FROM toys")
        count = cursor.fetchone()[0]

        if count == 0:
            cursor.execute(
                """
                INSERT INTO toys (name, type, material, color, price)
                VALUES 
                    ('Машина', 'Транспорт', 'Пластик', 'Красный', 10.99),
                    ('Поезд', 'Транспорт', 'Металл', 'Синий', 15.99),
                    ('Кукла', 'Фигура', 'Ткань', 'Розовый', 8.99),
                    ('Робот', 'Робот', 'Металл', 'Серебряный', 19.99),
                    ('Мяч', 'Спорт', 'Резина', 'Зеленый', 5.99),
                    ('Кубики', 'Игрушка', 'Дерево', 'Желтый', 12.99),
                    ('Медведь', 'Игрушка', 'Плюш', 'Коричневый', 9.99),
                    ('Самолет', 'Транспорт', 'Пластик', 'Белый', 17.99),
                    ('Каталка', 'Игрушка', 'Пластик', 'Оранжевый', 14.99),
                    ('Кукольный домик', 'Игрушка', 'Дерево', 'Фиолетовый', 24.99),
                    ('Мягкий мяч', 'Спорт', 'Ткань', 'Серый', 7.99),
                    ('Игровой набор', 'Игрушка', 'Пластик', 'Голубой', 11.99),
                    ('Тетрис', 'Игрушка', 'Пластик', 'Черный', 16.99),
                    ('Игрушечный компьютер', 'Игрушка', 'Пластик', 'Фиолетовый', 21.99),
                    ('Магнитный конструктор', 'Игрушка', 'Металл', 'Желтый', 19.99),
                    ('Лошадка на пружине', 'Игрушка', 'Пластик', 'Коричневый', 27.99),
                    ('Пазл', 'Игрушка', 'Картон', 'Зеленый', 13.99),
                    ('Роликовые коньки', 'Спорт', 'Металл', 'Черный', 34.99),
                    ('Беговел', 'Транспорт', 'Металл', 'Красный', 29.99),
                    ('Набор инструментов', 'Игрушка', 'Пластик', 'Оранжевый', 18.99),
                    ('Карточные игры', 'Игрушка', 'Картон', 'Синий', 9.99),
                    ('Игрушечный телефон', 'Игрушка', 'Пластик', 'Белый', 7.99),
                    ('Кукольная коляска', 'Игрушка', 'Пластик', 'Розовый', 23.99),
                    ('Велосипед', 'Транспорт', 'Металл', 'Синий', 45.99),
                    ('Пластиковые фигурки', 'Игрушка', 'Пластик', 'Зеленый', 8.99),
                    ('Комплект посуды', 'Игрушка', 'Пластик', 'Желтый', 12.99),
                    ('Бильярдный стол', 'Игрушка', 'Дерево', 'Коричневый', 69.99),
                    ('Водный пистолет', 'Игрушка', 'Пластик', 'Голубой', 6.99),
                    ('Малярный набор', 'Игрушка', 'Пластик', 'Оранжевый', 15.99),
                    ('Магнитный пазл', 'Игрушка', 'Пластик', 'Красный', 11.99),
                    ('Конструктор LEGO', 'Игрушка', 'Пластик', 'Желтый', 33.99),
                    ('Пистолет-пулемет', 'Игрушка', 'Пластик', 'Серый', 7.99),
                    ('Набор для рисования', 'Игрушка', 'Пластик', 'Фиолетовый', 14.99),
                    ('Игрушечная кухня', 'Игрушка', 'Пластик', 'Коричневый', 19.99),
                    ('Масса для лепки', 'Игрушка', 'Пластик', 'Зеленый', 9.99),
                    ('Футбольные ворота', 'Спорт', 'Металл', 'Белый', 25.99),
                    ('Детский тренажер', 'Спорт', 'Пластик', 'Синий', 28.99),
                    ('Мягкий пазл', 'Игрушка', 'Ткань', 'Красный', 10.99),
                    ('Комплект инструментов', 'Игрушка', 'Пластик', 'Оранжевый', 11.99),
                    ('Игрушечная ракета', 'Игрушка', 'Пластик', 'Серый', 18.99),
                    ('Магнитный лабиринт', 'Игрушка', 'Пластик', 'Голубой', 16.99),
                    ('Рулетка для измерений', 'Игрушка', 'Пластик', 'Белый', 9.99),
                    ('Детский смартфон', 'Игрушка', 'Пластик', 'Коричневый', 7.99),
                    ('Набор доктора', 'Игрушка', 'Пластик', 'Розовый', 13.99),
                    ('Игрушечный вертолет', 'Игрушка', 'Пластик', 'Синий', 20.99),
                    ('Скакалка', 'Спорт', 'Пластик', 'Красный', 4.99)
                """
            )

        connection.commit()
        cursor.execute("SELECT * FROM toys")
        toys = cursor.fetchall()

        for toy in toys:
            row_position = self.table.rowCount()
            self.table.insertRow(row_position)
            for col_index, col in enumerate(toy):
                self.table.setItem(row_position, col_index, QTableWidgetItem(str(col)))

    # Поиск игрушек
    def search_toys(self):
        keyword = self.search_input.text().lower()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM toys")
        toys = cursor.fetchall()
        self.table.setRowCount(0)

        for toy in toys:
            if any(keyword in str(col).lower() for col in toy):
                row_position = self.table.rowCount()
                self.table.insertRow(row_position)
                for col_index, col in enumerate(toy):
                    self.table.setItem(
                        row_position, col_index, QTableWidgetItem(str(col))
                    )

        cursor.close()
        self.reset_button.setVisible(True)

    # Сброс поиска
    def reset_search(self):
        self.search_input.clear()
        self.reset_button.setVisible(False)
        self.load_toys()

    # Сортировка игрушек
    def sort_toys(self):
        sort_option = self.sort_combo.currentText()
        cursor = connection.cursor()

        if "По названию" in sort_option:
            cursor.execute(
                f"SELECT * FROM toys ORDER BY name {'ASC' if 'возр.' in sort_option else 'DESC'}"
            )
        elif "По типу" in sort_option:
            cursor.execute(
                f"SELECT * FROM toys ORDER BY type {'ASC' if 'возр.' in sort_option else 'DESC'}"
            )
        elif "По материалу" in sort_option:
            cursor.execute(
                f"SELECT * FROM toys ORDER BY material {'ASC' if 'возр.' in sort_option else 'DESC'}"
            )
        elif "По цвету" in sort_option:
            cursor.execute(
                f"SELECT * FROM toys ORDER BY color {'ASC' if 'возр.' in sort_option else 'DESC'}"
            )
        elif "По цене" in sort_option:
            cursor.execute(
                f"SELECT * FROM toys ORDER BY price {'ASC' if 'возр.' in sort_option else 'DESC'}"
            )
        elif "По номеру" in sort_option:
            cursor.execute(
                f"SELECT * FROM toys ORDER BY id {'ASC' if 'возр.' in sort_option else 'DESC'}"
            )

        toys = cursor.fetchall()
        self.table.setRowCount(0)

        for toy in toys:
            row_position = self.table.rowCount()
            self.table.insertRow(row_position)
            for col_index, col in enumerate(toy):
                self.table.setItem(row_position, col_index, QTableWidgetItem(str(col)))

    # Добавление новой игрушки
    def add_toy(self):
        dialog = AddToyDialog(self)
        dialog.exec()
        self.load_toys()

    # Изменение выбранной игрушки
    def edit_toy(self):
        selected_row = self.table.currentRow()
        if selected_row != -1:
            id = int(self.table.item(selected_row, 0).text())
            dialog = EditToyDialog(self, id)
            dialog.exec()
            self.load_toys()
        else:
            QMessageBox.warning(self, "Ошибка", "Выберите игрушку для редактирования")

    # Удаление выбранной игрушки
    def delete_toy(self):
        selected_row = self.table.currentRow()
        if selected_row != -1:
            id = int(self.table.item(selected_row, 0).text())
            cursor = connection.cursor()
            cursor.execute("DELETE FROM toys WHERE id=%s", (id,))
            connection.commit()
            self.load_toys()
        else:
            QMessageBox.warning(self, "Ошибка", "Выберите игрушку для удаления")


# Диалог добавления новой игрушки
class AddToyDialog(QDialog):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.setWindowTitle("Добавить игрушку")
        self.layout = QGridLayout()
        self.name_label = QLabel("Название:")
        self.name_input = QLineEdit()
        self.layout.addWidget(self.name_label, 0, 0)
        self.layout.addWidget(self.name_input, 0, 1)
        self.type_label = QLabel("Тип:")
        self.type_input = QLineEdit()
        self.layout.addWidget(self.type_label, 1, 0)
        self.layout.addWidget(self.type_input, 1, 1)
        self.material_label = QLabel("Материал:")
        self.material_input = QLineEdit()
        self.layout.addWidget(self.material_label, 2, 0)
        self.layout.addWidget(self.material_input, 2, 1)
        self.color_label = QLabel("Цвет:")
        self.color_input = QLineEdit()
        self.layout.addWidget(self.color_label, 3, 0)
        self.layout.addWidget(self.color_input, 3, 1)
        self.price_label = QLabel("Цена:")
        self.price_input = QLineEdit()
        self.layout.addWidget(self.price_label, 4, 0)
        self.layout.addWidget(self.price_input, 4, 1)
        self.add_button = QPushButton("Добавить")
        self.add_button.clicked.connect(self.add_toy)
        self.layout.addWidget(self.add_button, 5, 0, 1, 2)
        self.setLayout(self.layout)

    # Добавление новой игрушки в базу данных
    def add_toy(self):
        name = self.name_input.text()
        type = self.type_input.text()
        material = self.material_input.text()
        color = self.color_input.text()
        price = float(self.price_input.text())
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO toys (name, type, material, color, price) VALUES (%s, %s, %s, %s, %s)",
            (name, type, material, color, price),
        )
        connection.commit()
        self.parent.load_toys()
        self.close()


# Диалог редактирования игрушки
class EditToyDialog(QDialog):
    def __init__(self, parent, id):
        super().__init__()
        self.parent = parent
        self.id = id
        self.setWindowTitle("Редактировать игрушку")
        self.layout = QGridLayout()
        self.name_label = QLabel("Название:")
        self.name_input = QLineEdit()
        self.layout.addWidget(self.name_label, 0, 0)
        self.layout.addWidget(self.name_input, 0, 1)
        self.type_label = QLabel("Тип:")
        self.type_input = QLineEdit()
        self.layout.addWidget(self.type_label, 1, 0)
        self.layout.addWidget(self.type_input, 1, 1)
        self.material_label = QLabel("Материал:")
        self.material_input = QLineEdit()
        self.layout.addWidget(self.material_label, 2, 0)
        self.layout.addWidget(self.material_input, 2, 1)
        self.color_label = QLabel("Цвет:")
        self.color_input = QLineEdit()
        self.layout.addWidget(self.color_label, 3, 0)
        self.layout.addWidget(self.color_input, 3, 1)
        self.price_label = QLabel("Цена:")
        self.price_input = QLineEdit()
        self.layout.addWidget(self.price_label, 4, 0)
        self.layout.addWidget(self.price_input, 4, 1)
        self.edit_button = QPushButton("Сохранить изменения")
        self.edit_button.clicked.connect(self.edit_toy)
        self.layout.addWidget(self.edit_button, 5, 0, 1, 2)
        self.setLayout(self.layout)
        self.load_toy_data()

    # Загрузка данных выбранной игрушки
    def load_toy_data(self):
        cursor = connection.cursor()
        cursor.execute(
            "SELECT name, type, material, color, price FROM toys WHERE id=%s",
            (self.id,),
        )
        toy = cursor.fetchone()
        self.name_input.setText(toy[0])
        self.type_input.setText(toy[1])
        self.material_input.setText(toy[2])
        self.color_input.setText(toy[3])
        self.price_input.setText(str(toy[4]))

    # Сохранение изменений игрушки
    def edit_toy(self):
        name = self.name_input.text()
        type = self.type_input.text()
        material = self.material_input.text()
        color = self.color_input.text()
        price = float(self.price_input.text())
        cursor = connection.cursor()
        cursor.execute(
            "UPDATE toys SET name=%s, type=%s, material=%s, color=%s, price=%s WHERE id=%s",
            (name, type, material, color, price, self.id),
        )
        connection.commit()
        self.parent.load_toys()
        self.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ToyStoreApp()
    window.show()
    sys.exit(app.exec())
