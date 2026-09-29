import sys
import json
import time
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QInputDialog
from PyQt5.QtGui import QColor, QFont
from PyQt5.QtWidgets import QGraphicsDropShadowEffect
from pr1 import Ui_MainWindow

USERS_FILE = "users.json"
SESSION_FILE = "session.txt"


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # --- РОЗШИРЕНИЙ ДИЗАЙН ТА ЕФЕКТИ ---
        self.apply_advanced_design()

        # Змінні для захисту від брутфорсу
        self.failed_attempts = 0
        self.block_until = 0

        # Підключення кнопок до обробників
        self.ui.loginButton.clicked.connect(self.handle_login)
        self.ui.registerButton.clicked.connect(self.handle_register)

    def apply_advanced_design(self):
        # 1. Головне вікно та стиль платформи
        self.setStyleSheet("""
            QMainWindow {
                background-color: #121212;
            }
        """)

        # 2. М'яка неонова тінь для центрального фрейму (об'ємний ефект)
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(35)
        shadow.setColor(QColor(255, 107, 0, 120))  # Насичене помаранчеве світіння MOTO DRIVE
        shadow.setOffset(0, 0)
        self.ui.frame.setGraphicsEffect(shadow)

        # 3. Стильний заголовок / логотип із міткою
        self.ui.titleLabel.setText("🏍️ MOTO DRIVE")
        self.ui.titleLabel.setStyleSheet("""
            QLabel {
                color: #FF6B00;
                font-size: 28px;
                font-weight: bold;
                letter-spacing: 2px;
            }
        """)

        # 4. Преміальний дизайн кнопок (градієнт, скруглення та ефекти ховеру)
        modern_button_style = """
            QPushButton {
                background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                                                  stop:0 #FF8C42, stop:1 #FF5500);
                color: #FFFFFF;
                border: none;
                border-radius: 16px;
                font-size: 16px;
                font-weight: bold;
                padding: 12px;
                letter-spacing: 1px;
            }
            QPushButton:hover {
                background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                                                  stop:0 #FFA366, stop:1 #FF6B00);
                border: 2px solid #FFFFFF;
            }
            QPushButton:pressed {
                background-color: #CC4400;
                border: none;
            }
        """
        self.ui.loginButton.setStyleSheet(modern_button_style)
        self.ui.registerButton.setStyleSheet(modern_button_style)

    def load_users(self):
        try:
            with open(USERS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            return []

    def save_users(self, users):
        with open(USERS_FILE, "w", encoding="utf-8") as f:
            json.dump(users, f, indent=4, ensure_ascii=False)

    def handle_login(self):
        current_time = time.time()
        if current_time < self.block_until:
            remaining = int(self.block_until - current_time)
            QMessageBox.warning(self.ui.centralwidget, "Помилка",
                                f"Система заблокована через невірні спроби. Зачекайте {remaining} сек.")
            return

        email, ok1 = QInputDialog.getText(self, "Авторизація", "Введіть ваш email:")
        if not ok1 or not email:
            return

        password, ok2 = QInputDialog.getText(self, "Авторизація", "Введіть пароль:", QInputDialog.Password)
        if not ok2 or not password:
            return

        users = self.load_users()
        user_found = None

        for user in users:
            if user["email"] == email and user["password"] == password:
                user_found = user
                break

        if user_found:
            self.failed_attempts = 0
            if user_found["role"] == "admin":
                total_users = len(users)
                QMessageBox.information(self, "Режим адміністратора",
                                        f"Вітаємо, Адміне!\nЗагальна кількість зареєстрованих користувачів: {total_users}")
            else:
                QMessageBox.information(self, "Успіх", "Вітаємо у нашому мотосалоні MOTO DRIVE!")
                remember, ok3 = QInputDialog.getItem(self, "Сесія", "Бажаєте зберегти сесію?", ["Так", "Ні"], 0, False)
                if ok3 and remember == "Так":
                    with open(SESSION_FILE, "w", encoding="utf-8") as sf:
                        sf.write(email)
        else:
            self.failed_attempts += 1
            if self.failed_attempts >= 3:
                self.block_until = time.time() + 10
                self.failed_attempts = 0
                QMessageBox.critical(self, "Блокування",
                                     "3 невірні спроби підряд! Кнопку входу заблоковано на 10 секунд.")
            else:
                QMessageBox.warning(self.ui.centralwidget, "Помилка",
                                    f"Невірний email або пароль! Залишилось спроб: {3 - self.failed_attempts}")

    def handle_register(self):
        email, ok1 = QInputDialog.getText(self, "Реєстрація", "Введіть новий email:")
        if not ok1 or not email:
            return

        password, ok2 = QInputDialog.getText(self, "Реєстрація", "Введіть пароль:", QInputDialog.Password)
        if not ok2 or not password:
            return

        users = self.load_users()
        for user in users:
            if user["email"] == email:
                QMessageBox.warning(self, "Помилка", "Користувач із таким email вже існує!")
                return

        new_user = {"email": email, "password": password, "role": "customer"}
        users.append(new_user)
        self.save_users(users)
        QMessageBox.information(self, "Успіх", "Реєстрація успішна! Тепер ви можете увійти.")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())