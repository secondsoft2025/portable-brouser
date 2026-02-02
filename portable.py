import sys
import os
import json
from datetime import datetime
from pathlib import Path
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWebEngineWidgets import *

class BrowserTab(QWidget):
    def __init__(self, parent=None, home_page="https://www.google.com"):
        super().__init__(parent)
        self.home_page = home_page  # Сохраняем домашнюю страницу
        self.browser = QWebEngineView()
        self.browser.setUrl(QUrl(self.home_page))  # Используем домашнюю страницу по умолчанию
        
        # Панель навигации
        self.nav_bar = QToolBar()
        self.back_btn = QPushButton("←")
        self.forward_btn = QPushButton("→")
        self.reload_btn = QPushButton("↻")
        self.home_btn = QPushButton("🏠")  # Кнопка домашней страницы
        self.url_bar = QLineEdit()
        self.go_btn = QPushButton("Go")
        
        self.back_btn.clicked.connect(self.browser.back)
        self.forward_btn.clicked.connect(self.browser.forward)
        self.reload_btn.clicked.connect(self.browser.reload)
        self.home_btn.clicked.connect(self.go_home)
        self.go_btn.clicked.connect(self.navigate_to_url)
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        self.browser.urlChanged.connect(self.update_url)
        
        self.nav_bar.addWidget(self.back_btn)
        self.nav_bar.addWidget(self.forward_btn)
        self.nav_bar.addWidget(self.reload_btn)
        self.nav_bar.addWidget(self.home_btn)
        self.nav_bar.addWidget(self.url_bar)
        self.nav_bar.addWidget(self.go_btn)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.nav_bar)
        layout.addWidget(self.browser)
        self.setLayout(layout)
    
    def go_home(self):
        """Перейти на домашнюю страницу"""
        self.browser.setUrl(QUrl(self.home_page))
    
    def navigate_to_url(self):
        url = self.url_bar.text()
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        self.browser.setUrl(QUrl(url))
    
    def update_url(self, q):
        self.url_bar.setText(q.toString())

class BlockedSitesManager:
    def __init__(self, config_dir):
        self.config_dir = Path(config_dir)
        self.config_file = self.config_dir / "blocked_sites.json"
        self.blocked_sites = self.load_blocked_sites()
    
    def load_blocked_sites(self):
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                return json.load(f)
        return []
    
    def save_blocked_sites(self):
        self.config_dir.mkdir(parents=True, exist_ok=True)
        with open(self.config_file, 'w') as f:
            json.dump(self.blocked_sites, f, indent=2)
    
    def add_site(self, site):
        if site not in self.blocked_sites:
            self.blocked_sites.append(site)
            self.save_blocked_sites()
            return True
        return False
    
    def remove_site(self, site):
        if site in self.blocked_sites:
            self.blocked_sites.remove(site)
            self.save_blocked_sites()
            return True
        return False
    
    def is_blocked(self, url):
        url_str = url.toString().lower()
        for site in self.blocked_sites:
            if site.lower() in url_str:
                return True
        return False

class PortableBrowser(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Инициализация папок
        self.app_dir = Path(__file__).parent
        self.data_dir = self.app_dir / "browser_data"
        self.config_dir = self.data_dir / "config"
        
        # Настройки домашней страницы
        self.home_page = "https://www.google.com"  # Фиксированная домашняя страница
        
        # Менеджер заблокированных сайтов
        self.block_manager = BlockedSitesManager(self.config_dir)
        
        # Состояние браузера
        self.incognito_mode = False
        self.dark_mode = False
        
        # Интерфейс
        self.setWindowTitle("Portable Browser - Домашняя страница: Google")
        self.setGeometry(100, 100, 1200, 800)
        
        # Установка иконки
        self.setWindowIcon(QIcon(self.create_browser_icon()))
        
        # Создание интерфейса
        self.setup_ui()
        
        # Загрузка настроек
        self.load_settings()
        
        # Текущие вкладки
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.currentChanged.connect(self.tab_changed)
        
        # Создаем первую вкладку с Google в качестве домашней страницы
        self.add_new_tab()
        
        self.setCentralWidget(self.tabs)
        
        # Показываем сообщение о домашней странице при запуске
        QTimer.singleShot(1000, self.show_home_page_notification)
    
    def show_home_page_notification(self):
        """Показываем уведомление о домашней странице при запуске"""
        current_tab = self.tabs.currentWidget()
        if current_tab and current_tab.browser.url().toString() == self.home_page:
            self.statusBar().showMessage(f"Домашняя страница: {self.home_page}", 3000)
    
    def create_browser_icon(self):
        # Создаем иконку с логотипом Google
        pixmap = QPixmap(64, 64)
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Google цвета
        colors = [
            QColor("#4285F4"),  # Blue
            QColor("#EA4335"),  # Red
            QColor("#FBBC05"),  # Yellow
            QColor("#34A853"),  # Green
        ]
        
        # Рисуем Google-подобную иконку
        painter.setBrush(QBrush(colors[0]))
        painter.drawEllipse(10, 10, 44, 44)
        
        # Буква "G"
        painter.setPen(QPen(Qt.white, 3))
        painter.setBrush(Qt.NoBrush)
        painter.drawEllipse(20, 20, 24, 24)
        painter.drawLine(32, 30, 38, 30)
        painter.drawLine(32, 30, 32, 40)
        
        painter.end()
        return pixmap
    
    def setup_ui(self):
        # Создание меню
        menubar = self.menuBar()
        
        # Меню Файл
        file_menu = menubar.addMenu("Файл")
        
        new_tab_action = QAction("Новая вкладка", self)
        new_tab_action.setShortcut("Ctrl+T")
        new_tab_action.triggered.connect(self.add_new_tab)
        file_menu.addAction(new_tab_action)
        
        new_incognito_tab_action = QAction("Новое окно в режиме инкогнито", self)
        new_incognito_tab_action.setShortcut("Ctrl+Shift+N")
        new_incognito_tab_action.triggered.connect(self.add_incognito_tab)
        file_menu.addAction(new_incognito_tab_action)
        
        home_action = QAction("Открыть домашнюю страницу", self)
        home_action.setShortcut("Ctrl+H")
        home_action.triggered.connect(self.open_home_page)
        file_menu.addAction(home_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Выход", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Меню Настройки
        settings_menu = menubar.addMenu("Настройки")
        
        self.dark_mode_action = QAction("Темная тема", self)
        self.dark_mode_action.setCheckable(True)
        self.dark_mode_action.triggered.connect(self.toggle_dark_mode)
        settings_menu.addAction(self.dark_mode_action)
        
        incognito_action = QAction("Режим инкогнито", self)
        incognito_action.setCheckable(True)
        incognito_action.triggered.connect(self.toggle_incognito_mode)
        settings_menu.addAction(incognito_action)
        
        # Меню Блокировщик
        block_menu = menubar.addMenu("Блокировщик")
        
        manage_blocks_action = QAction("Управление заблокированными сайтами", self)
        manage_blocks_action.triggered.connect(self.manage_blocked_sites)
        block_menu.addAction(manage_blocks_action)
        
        # Меню Справка
        help_menu = menubar.addMenu("Справка")
        
        about_action = QAction("О браузере", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
        # Панель инструментов
        toolbar = QToolBar()
        self.addToolBar(toolbar)
        
        new_tab_btn = QPushButton("+")
        new_tab_btn.setToolTip("Новая вкладка (Ctrl+T)")
        new_tab_btn.clicked.connect(self.add_new_tab)
        toolbar.addWidget(new_tab_btn)
        
        home_btn = QPushButton("🏠")
        home_btn.setToolTip("Домашняя страница (Ctrl+H)")
        home_btn.clicked.connect(self.open_home_page)
        toolbar.addWidget(home_btn)
        
        incognito_btn = QPushButton("👤")
        incognito_btn.setToolTip("Режим инкогнито")
        incognito_btn.clicked.connect(self.toggle_incognito_mode)
        toolbar.addWidget(incognito_btn)
        
        dark_mode_btn = QPushButton("🌙")
        dark_mode_btn.setToolTip("Темная тема")
        dark_mode_btn.clicked.connect(self.toggle_dark_mode)
        toolbar.addWidget(dark_mode_btn)
        
        block_btn = QPushButton("🚫")
        block_btn.setToolTip("Блокировщик сайтов")
        block_btn.clicked.connect(self.manage_blocked_sites)
        toolbar.addWidget(block_btn)
        
        # Добавляем информационную метку о домашней странице
        home_label = QLabel(f"Домашняя страница: Google")
        home_label.setStyleSheet("color: #666; padding: 5px;")
        toolbar.addWidget(home_label)
    
    def open_home_page(self):
        """Открыть домашнюю страницу в текущей вкладке"""
        current_tab = self.tabs.currentWidget()
        if current_tab:
            current_tab.browser.setUrl(QUrl(self.home_page))
            self.statusBar().showMessage(f"Открыта домашняя страница: {self.home_page}", 2000)
    
    def add_new_tab(self, url=None, incognito=False):
        """Добавить новую вкладку"""
        # Всегда используем домашнюю страницу по умолчанию, если не указан другой URL
        if url is None:
            url = self.home_page
        
        tab = BrowserTab(home_page=self.home_page)  # Передаем домашнюю страницу в таб
        
        # Устанавливаем профиль в зависимости от режима
        if self.incognito_mode or incognito:
            profile = QWebEngineProfile("incognito")
            storage_name = f"incognito_{datetime.now().timestamp()}"
            profile.setPersistentStoragePath(str(self.data_dir / storage_name))
            profile.setHttpCacheType(QWebEngineProfile.NoCache)
            profile.setPersistentCookiesPolicy(QWebEngineProfile.NoPersistentCookies)
        else:
            profile = QWebEngineProfile.defaultProfile()
        
        webpage = QWebEnginePage(profile, tab.browser)
        tab.browser.setPage(webpage)
        
        # Устанавливаем URL
        tab.browser.setUrl(QUrl(url))
        
        # Подключаем обработчик для блокировки сайтов
        def handle_url_change(q):
            if self.block_manager.is_blocked(q):
                tab.browser.setHtml(self.get_blocked_page_html(q.toString()))
        
        tab.browser.urlChanged.connect(handle_url_change)
        
        # Определяем название вкладки
        if url == self.home_page:
            tab_name = "Google"
        else:
            tab_name = "Новая вкладка"
        
        index = self.tabs.addTab(tab, tab_name)
        self.tabs.setCurrentIndex(index)
        
        # Обновляем заголовок при изменении
        def update_title():
            title = tab.browser.page().title()
            if title:
                # Для Google показываем просто "Google"
                if "google" in tab.browser.url().toString().lower():
                    self.tabs.setTabText(index, "Google")
                else:
                    self.tabs.setTabText(index, title[:20] + "..." if len(title) > 20 else title)
        
        tab.browser.titleChanged.connect(update_title)
        
        # Показываем статус в статусной строке
        self.statusBar().showMessage(f"Открыта новая вкладка", 1500)
        
        return tab
    
    def add_incognito_tab(self):
        """Добавить вкладку в режиме инкогнито"""
        self.add_new_tab(url=self.home_page, incognito=True)
        self.statusBar().showMessage("Открыта новая вкладка в режиме инкогнито", 2000)
    
    def close_tab(self, index):
        if self.tabs.count() > 1:
            self.tabs.removeTab(index)
            self.statusBar().showMessage("Вкладка закрыта", 1500)
        else:
            self.close()
    
    def tab_changed(self, index):
        if index >= 0:
            tab = self.tabs.widget(index)
            if tab:
                current_url = tab.browser.url().toString()
                if current_url == self.home_page:
                    self.statusBar().showMessage(f"Текущая вкладка: Домашняя страница (Google)", 2000)
                else:
                    self.statusBar().showMessage(f"Текущая вкладка: {tab.browser.page().title()}", 2000)
    
    def toggle_dark_mode(self):
        self.dark_mode = not self.dark_mode
        self.dark_mode_action.setChecked(self.dark_mode)
        
        if self.dark_mode:
            self.setStyleSheet("""
                QMainWindow, QWidget {
                    background-color: #2b2b2b;
                    color: #ffffff;
                }
                QTabWidget::pane {
                    border: 1px solid #444;
                    background-color: #2b2b2b;
                }
                QTabBar::tab {
                    background-color: #3b3b3b;
                    color: #ffffff;
                    padding: 8px;
                }
                QTabBar::tab:selected {
                    background-color: #4b4b4b;
                }
                QLineEdit {
                    background-color: #3b3b3b;
                    color: #ffffff;
                    border: 1px solid #555;
                    padding: 5px;
                }
                QPushButton {
                    background-color: #4b4b4b;
                    color: #ffffff;
                    border: none;
                    padding: 5px 10px;
                }
                QPushButton:hover {
                    background-color: #5b5b5b;
                }
                QToolBar {
                    background-color: #3b3b3b;
                    border: none;
                }
                QStatusBar {
                    background-color: #3b3b3b;
                    color: #ffffff;
                }
                QLabel {
                    color: #ffffff;
                }
            """)
        else:
            self.setStyleSheet("""
                QStatusBar {
                    background-color: #f0f0f0;
                    color: #000000;
                }
            """)
        
        self.statusBar().showMessage(f"Темная тема: {'Включена' if self.dark_mode else 'Выключена'}", 2000)
        self.save_settings()
    
    def toggle_incognito_mode(self):
        self.incognito_mode = not self.incognito_mode
        status = "ВКЛ" if self.incognito_mode else "ВЫКЛ"
        self.setWindowTitle(f"Portable Browser - Домашняя страница: Google - Режим инкогнито: {status}")
        self.statusBar().showMessage(f"Режим инкогнито: {status}", 2000)
        self.save_settings()
    
    def manage_blocked_sites(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Управление заблокированными сайтами")
        dialog.setModal(True)
        dialog.resize(500, 400)
        
        layout = QVBoxLayout()
        
        # Информация
        info_label = QLabel("Примечание: Google всегда доступен как домашняя страница")
        info_label.setStyleSheet("color: #4285F4; font-weight: bold; padding: 5px;")
        layout.addWidget(info_label)
        
        # Список заблокированных сайтов
        self.block_list_widget = QListWidget()
        self.update_block_list()
        layout.addWidget(QLabel("Заблокированные сайты:"))
        layout.addWidget(self.block_list_widget)
        
        # Поле для добавления нового сайта
        add_layout = QHBoxLayout()
        self.new_site_input = QLineEdit()
        self.new_site_input.setPlaceholderText("Введите URL для блокировки (например: facebook.com)")
        add_btn = QPushButton("Добавить")
        add_btn.clicked.connect(self.add_site_to_block)
        add_layout.addWidget(self.new_site_input)
        add_layout.addWidget(add_btn)
        layout.addLayout(add_layout)
        
        # Кнопки управления
        btn_layout = QHBoxLayout()
        remove_btn = QPushButton("Удалить выбранное")
        remove_btn.clicked.connect(self.remove_selected_site)
        clear_btn = QPushButton("Очистить все")
        clear_btn.clicked.connect(self.clear_all_sites)
        btn_layout.addWidget(remove_btn)
        btn_layout.addWidget(clear_btn)
        layout.addLayout(btn_layout)
        
        # Кнопки закрытия
        close_btn = QPushButton("Закрыть")
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn)
        
        dialog.setLayout(layout)
        dialog.exec_()
    
    def update_block_list(self):
        self.block_list_widget.clear()
        for site in self.block_manager.blocked_sites:
            self.block_list_widget.addItem(site)
    
    def add_site_to_block(self):
        site = self.new_site_input.text().strip()
        if site:
            # Не позволяем блокировать Google
            if "google" in site.lower():
                QMessageBox.warning(self, "Ошибка", "Google не может быть заблокирован - это домашняя страница браузера")
                return
            
            if self.block_manager.add_site(site):
                self.update_block_list()
                self.new_site_input.clear()
                QMessageBox.information(self, "Успех", f"Сайт {site} добавлен в список блокировки")
    
    def remove_selected_site(self):
        current_item = self.block_list_widget.currentItem()
        if current_item:
            site = current_item.text()
            if self.block_manager.remove_site(site):
                self.update_block_list()
    
    def clear_all_sites(self):
        reply = QMessageBox.question(
            self, "Подтверждение",
            "Вы уверены, что хотите удалить все заблокированные сайты?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.block_manager.blocked_sites = []
            self.block_manager.save_blocked_sites()
            self.update_block_list()
    
    def get_blocked_page_html(self, url):
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    background-color: #f0f0f0;
                    color: #333;
                    text-align: center;
                    padding: 50px;
                }}
                .container {{
                    max-width: 600px;
                    margin: 0 auto;
                    background-color: white;
                    padding: 30px;
                    border-radius: 10px;
                    box-shadow: 0 0 10px rgba(0,0,0,0.1);
                }}
                h1 {{ color: #d32f2f; }}
                .url {{ color: #666; font-style: italic; }}
                .home-link {{
                    background-color: #4285F4;
                    color: white;
                    padding: 10px 20px;
                    text-decoration: none;
                    border-radius: 5px;
                    display: inline-block;
                    margin-top: 20px;
                }}
                .home-link:hover {{
                    background-color: #3367D6;
                }}
                .dark-mode {{
                    background-color: #2b2b2b;
                    color: #ffffff;
                }}
                .dark-mode .container {{
                    background-color: #3b3b3b;
                }}
                .dark-mode h1 {{ color: #ff6b6b; }}
                .dark-mode .home-link {{
                    background-color: #34A853;
                }}
            </style>
        </head>
        <body class="{'dark-mode' if self.dark_mode else ''}">
            <div class="container">
                <h1>🚫 Доступ запрещен</h1>
                <p>Сайт <span class="url">{url}</span> заблокирован Portable Browser.</p>
                <p>Этот сайт был добавлен в список блокировки для вашей безопасности.</p>
                <p>Google всегда доступен как домашняя страница.</p>
                <p><a href="{self.home_page}" class="home-link">Вернуться на Google</a></p>
            </div>
        </body>
        </html>
        """
    
    def show_about(self):
        """Показать информацию о браузере"""
        about_text = f"""
        <h2>Portable Browser</h2>
        <p>Версия 1.0</p>
        <p>Портативный браузер с вкладками, режимом инкогнито, темной темой и блокировщиком сайтов.</p>
        <p><b>Домашняя страница:</b> {self.home_page}</p>
        <p><b>Режим инкогнито:</b> {'Включен' if self.incognito_mode else 'Выключен'}</p>
        <p><b>Заблокированных сайтов:</b> {len(self.block_manager.blocked_sites)}</p>
        <hr>
        <p>Все данные сохраняются в папке: {self.data_dir}</p>
        <p>Google всегда доступен как домашняя страница.</p>
        """
        QMessageBox.about(self, "О браузере", about_text)
    
    def load_settings(self):
        settings_file = self.config_dir / "settings.json"
        if settings_file.exists():
            try:
                with open(settings_file, 'r') as f:
                    settings = json.load(f)
                    self.dark_mode = settings.get('dark_mode', False)
                    self.incognito_mode = settings.get('incognito_mode', False)
                    
                    if self.dark_mode:
                        self.dark_mode_action.setChecked(True)
                        self.toggle_dark_mode()
            except:
                pass
    
    def save_settings(self):
        settings_file = self.config_dir / "settings.json"
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        settings = {
            'dark_mode': self.dark_mode,
            'incognito_mode': self.incognito_mode,
            'home_page': self.home_page,  # Сохраняем домашнюю страницу
            'saved_at': datetime.now().isoformat()
        }
        
        with open(settings_file, 'w') as f:
            json.dump(settings, f, indent=2)
    
    def closeEvent(self, event):
        self.save_settings()
        self.statusBar().showMessage("Сохранение настроек...", 1000)
        event.accept()

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Portable Browser")
    app.setOrganizationName("Portable Browser")
    
    # Устанавливаем стиль по умолчанию
    app.setStyle("Fusion")
    
    # Создаем и показываем браузер
    browser = PortableBrowser()
    browser.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()