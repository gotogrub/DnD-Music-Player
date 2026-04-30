import os
import random
import json
import pygame
import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QListWidget, QPushButton, QLabel,
                             QSlider, QDialog, QLineEdit, QListWidgetItem,
                             QMessageBox, QShortcut, QComboBox, QInputDialog,
                             QGridLayout, QFrame, QScrollArea, QColorDialog,
                             QSizePolicy)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QSize
from PyQt5.QtGui import QKeySequence, QColor, QFont

# Unicode иконки для категорий
CATEGORY_ICONS = {
    "swords": "⚔️",      # Бой
    "castle": "🏰",      # Город/Замок
    "tree": "🌲",        # Лес
    "skull": "💀",       # Катакомбы/Темное
    "moon": "🌙",        # Ночь
    "fire": "🔥",        # Огонь/Лагерь
    "tavern": "🍺",      # Таверна
    "scroll": "📜",      # История/Квест
    "crystal": "🔮",     # Магия
    "mountain": "⛰️",    # Путешествие
    "waves": "🌊",       # Вода/Море
    "star": "⭐",        # Небо/Ночь
    "dragon": "🐉",      # Босс/Эпик
    "heart": "❤️",       # Эмоции
    "music": "🎵",       # Музыка (по умолчанию)
}

# Палитра цветов Dark Fantasy
COLOR_PALETTE = [
    "#8b0000",  # Темно-красный (кровь)
    "#4a0080",  # Темно-фиолетовый (магия)
    "#006400",  # Темно-зеленый (лес)
    "#00008b",  # Темно-синий (ночь)
    "#8b4513",  # Коричневый (таверна)
    "#2f4f4f",  # Темно-серый (катакомбы)
    "#ff6600",  # Оранжевый (огонь)
    "#4682b4",  # Стальной синий (замок)
    "#9932cc",  # Фиолетовый (магия)
    "#708090",  # Серый (нейтральный)
]

# QSS стили для темной темы
DARK_THEME_STYLE = """
QMainWindow, QWidget {
    background-color: #1a1a2e;
    color: #e4e4e7;
}

QLabel {
    color: #e4e4e7;
    font-size: 12px;
}

QListWidget {
    background-color: #16213e;
    color: #e4e4e7;
    border: 1px solid #0f3460;
    border-radius: 5px;
    padding: 5px;
    font-size: 12px;
}

QListWidget::item {
    padding: 8px;
    border-radius: 3px;
}

QListWidget::item:selected {
    background-color: #0f3460;
}

QListWidget::item:hover {
    background-color: #1f4068;
}

QPushButton {
    background-color: #16213e;
    color: #e4e4e7;
    border: 1px solid #0f3460;
    border-radius: 5px;
    padding: 8px 16px;
    font-size: 14px;
}

QPushButton:hover {
    background-color: #1f4068;
    border-color: #e4e4e7;
}

QPushButton:pressed {
    background-color: #0f3460;
}

QSlider::groove:horizontal {
    border: 1px solid #0f3460;
    height: 8px;
    background: #16213e;
    border-radius: 4px;
}

QSlider::handle:horizontal {
    background: #e4e4e7;
    border: 1px solid #0f3460;
    width: 18px;
    margin: -5px 0;
    border-radius: 9px;
}

QSlider::sub-page:horizontal {
    background: #0f3460;
    border-radius: 4px;
}

QLineEdit, QComboBox {
    background-color: #16213e;
    color: #e4e4e7;
    border: 1px solid #0f3460;
    border-radius: 5px;
    padding: 8px;
    font-size: 12px;
}

QComboBox::drop-down {
    border: none;
    padding-right: 10px;
}

QComboBox QAbstractItemView {
    background-color: #16213e;
    color: #e4e4e7;
    selection-background-color: #0f3460;
}

QDialog {
    background-color: #1a1a2e;
}

QMessageBox {
    background-color: #1a1a2e;
}

QMessageBox QLabel {
    color: #e4e4e7;
}

QScrollArea {
    border: none;
    background-color: transparent;
}

QScrollBar:vertical {
    background-color: #16213e;
    width: 12px;
    border-radius: 6px;
}

QScrollBar::handle:vertical {
    background-color: #0f3460;
    border-radius: 6px;
    min-height: 20px;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

QFrame#drumpad_container {
    background-color: #16213e;
    border-radius: 10px;
    padding: 10px;
}
"""


class CategoryDrumpadButton(QPushButton):
    """Кнопка в стиле drumpad для категории"""

    def __init__(self, category_name, category_data, parent=None):
        super().__init__(parent)
        self.category_name = category_name
        self.category_data = category_data
        self.is_active = False

        self.setFixedSize(120, 120)
        self.setCursor(Qt.PointingHandCursor)
        self.update_display()

    def update_display(self):
        """Обновляет отображение кнопки"""
        icon = self.category_data.get('icon', 'music')
        icon_char = CATEGORY_ICONS.get(icon, CATEGORY_ICONS['music'])
        hotkey = self.category_data.get('hotkey', '')
        track_count = len(self.category_data.get('tracks', []))
        color = self.category_data.get('color', COLOR_PALETTE[0])

        # Сокращаем название если слишком длинное
        display_name = self.category_name
        if len(display_name) > 12:
            display_name = display_name[:10] + "..."

        self.setText(f"{icon_char}\n{display_name}\n({track_count})")
        self.setFont(QFont("Segoe UI Emoji", 10))

        self.update_style(color)

    def update_style(self, color):
        """Обновляет стиль кнопки с учетом цвета"""
        # Рассчитываем более светлый оттенок для hover
        qcolor = QColor(color)
        lighter = qcolor.lighter(130).name()
        darker = qcolor.darker(120).name()

        active_style = ""
        if self.is_active:
            active_style = f"border: 3px solid #e4e4e7; background-color: {lighter};"

        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: #e4e4e7;
                border: 2px solid {darker};
                border-radius: 10px;
                font-size: 11px;
                font-weight: bold;
                text-align: center;
                {active_style}
            }}
            QPushButton:hover {{
                background-color: {lighter};
                border-color: #e4e4e7;
            }}
            QPushButton:pressed {{
                background-color: {darker};
            }}
        """)

    def set_active(self, active):
        """Устанавливает активное состояние (воспроизведение)"""
        self.is_active = active
        color = self.category_data.get('color', COLOR_PALETTE[0])
        self.update_style(color)


class CategoryDialog(QDialog):
    def __init__(self, parent=None, existing_data=None):
        super().__init__(parent)
        self.setWindowTitle("Категория")
        self.setModal(True)
        self.setMinimumWidth(350)
        self.selected_color = existing_data.get('color', COLOR_PALETTE[0]) if existing_data else COLOR_PALETTE[0]
        self.selected_icon = existing_data.get('icon', 'music') if existing_data else 'music'
        self.setup_ui(existing_data)

    def setup_ui(self, existing_data=None):
        layout = QVBoxLayout()
        layout.setSpacing(15)

        # Название
        layout.addWidget(QLabel("Название:"))
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Название категории")
        if existing_data:
            self.name_input.setText(existing_data.get('name', ''))
        layout.addWidget(self.name_input)

        # Горячая клавиша
        layout.addWidget(QLabel("Горячая клавиша:"))
        self.hotkey_combo = QComboBox()
        self.hotkey_combo.addItems([str(i) for i in range(1, 10)])
        if existing_data:
            self.hotkey_combo.setCurrentText(existing_data.get('hotkey', '1'))
        layout.addWidget(self.hotkey_combo)

        # Выбор иконки
        layout.addWidget(QLabel("Иконка:"))
        icon_layout = QGridLayout()
        self.icon_buttons = {}

        icons = list(CATEGORY_ICONS.items())
        for i, (icon_name, icon_char) in enumerate(icons):
            btn = QPushButton(icon_char)
            btn.setFixedSize(40, 40)
            btn.setFont(QFont("Segoe UI Emoji", 16))
            btn.clicked.connect(lambda checked, name=icon_name: self.select_icon(name))
            icon_layout.addWidget(btn, i // 5, i % 5)
            self.icon_buttons[icon_name] = btn

        layout.addLayout(icon_layout)
        self.update_icon_selection()

        # Выбор цвета
        layout.addWidget(QLabel("Цвет:"))
        color_layout = QHBoxLayout()

        # Предустановленные цвета
        self.color_buttons = []
        for color in COLOR_PALETTE:
            btn = QPushButton()
            btn.setFixedSize(30, 30)
            btn.setStyleSheet(f"background-color: {color}; border: 2px solid #0f3460; border-radius: 5px;")
            btn.clicked.connect(lambda checked, c=color: self.select_color(c))
            color_layout.addWidget(btn)
            self.color_buttons.append((btn, color))

        # Кнопка выбора своего цвета
        custom_color_btn = QPushButton("+")
        custom_color_btn.setFixedSize(30, 30)
        custom_color_btn.setToolTip("Выбрать свой цвет")
        custom_color_btn.clicked.connect(self.choose_custom_color)
        color_layout.addWidget(custom_color_btn)

        layout.addLayout(color_layout)

        # Превью выбранного цвета
        self.color_preview = QLabel()
        self.color_preview.setFixedSize(200, 30)
        self.update_color_preview()
        layout.addWidget(self.color_preview)

        # Кнопки OK/Отмена
        button_layout = QHBoxLayout()
        self.ok_btn = QPushButton("OK")
        self.cancel_btn = QPushButton("Отмена")
        button_layout.addWidget(self.ok_btn)
        button_layout.addWidget(self.cancel_btn)
        layout.addLayout(button_layout)

        self.ok_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)

        self.setLayout(layout)

    def select_icon(self, icon_name):
        self.selected_icon = icon_name
        self.update_icon_selection()

    def update_icon_selection(self):
        for name, btn in self.icon_buttons.items():
            if name == self.selected_icon:
                btn.setStyleSheet("background-color: #0f3460; border: 2px solid #e4e4e7; border-radius: 5px;")
            else:
                btn.setStyleSheet("background-color: #16213e; border: 1px solid #0f3460; border-radius: 5px;")

    def select_color(self, color):
        self.selected_color = color
        self.update_color_preview()

    def update_color_preview(self):
        self.color_preview.setStyleSheet(
            f"background-color: {self.selected_color}; border: 2px solid #0f3460; border-radius: 5px;"
        )

    def choose_custom_color(self):
        color = QColorDialog.getColor(QColor(self.selected_color), self, "Выберите цвет")
        if color.isValid():
            self.selected_color = color.name()
            self.update_color_preview()

    def get_data(self):
        return {
            'name': self.name_input.text(),
            'hotkey': self.hotkey_combo.currentText(),
            'icon': self.selected_icon,
            'color': self.selected_color
        }


class MusicPlayer(QMainWindow):
    def __init__(self):
        super().__init__()
        pygame.mixer.init()

        self.current_track = None
        self.is_playing = False
        self.is_paused = False
        self.loop_mode = False
        self.categories = {}
        self.category_shortcuts = {}
        self.current_category_playing = None
        self.category_track_index = {}
        self.drumpad_buttons = {}

        self.load_settings()
        self.init_ui()
        self.setup_shortcuts()

        # Устанавливаем начальную громкость после инициализации UI
        self.set_volume(50)

        # Таймер для проверки окончания трека
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_track_end)
        self.timer.start(500)

    def init_ui(self):
        self.setWindowTitle("D&D Music Player")
        self.setGeometry(100, 100, 1200, 800)
        self.setMinimumSize(1000, 700)
        self.setStyleSheet(DARK_THEME_STYLE)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(15, 15, 15, 15)
        central_widget.setLayout(main_layout)

        # === Верхняя часть: Drumpad категорий ===
        drumpad_frame = QFrame()
        drumpad_frame.setObjectName("drumpad_container")
        drumpad_layout = QVBoxLayout(drumpad_frame)

        drumpad_header = QHBoxLayout()
        drumpad_header.addWidget(QLabel("Категории:"))
        drumpad_header.addStretch()

        # Кнопки управления категориями
        self.add_category_btn = QPushButton("+")
        self.add_category_btn.setFixedSize(30, 30)
        self.add_category_btn.setToolTip("Добавить категорию")
        self.add_category_btn.clicked.connect(self.add_category)
        drumpad_header.addWidget(self.add_category_btn)

        self.edit_category_btn = QPushButton("✎")
        self.edit_category_btn.setFixedSize(30, 30)
        self.edit_category_btn.setToolTip("Редактировать категорию")
        self.edit_category_btn.clicked.connect(self.edit_category)
        drumpad_header.addWidget(self.edit_category_btn)

        self.remove_category_btn = QPushButton("−")
        self.remove_category_btn.setFixedSize(30, 30)
        self.remove_category_btn.setToolTip("Удалить категорию")
        self.remove_category_btn.clicked.connect(self.remove_category)
        drumpad_header.addWidget(self.remove_category_btn)

        drumpad_layout.addLayout(drumpad_header)

        # Сетка кнопок категорий
        self.drumpad_grid = QGridLayout()
        self.drumpad_grid.setSpacing(10)
        drumpad_layout.addLayout(self.drumpad_grid)

        main_layout.addWidget(drumpad_frame)

        # === Средняя часть: Плейлист и информация ===
        middle_layout = QHBoxLayout()

        # Список треков
        track_panel = QVBoxLayout()
        track_panel.addWidget(QLabel("Все композиции:"))
        self.track_list = QListWidget()
        self.track_list.itemDoubleClicked.connect(self.play_selected_track)
        track_panel.addWidget(self.track_list)

        # Кнопки добавления/удаления треков из категорий
        track_buttons = QHBoxLayout()
        self.add_track_btn = QPushButton("Добавить в категорию")
        self.add_track_btn.clicked.connect(self.add_track_to_category)
        track_buttons.addWidget(self.add_track_btn)

        self.remove_track_btn = QPushButton("Удалить из категории")
        self.remove_track_btn.clicked.connect(self.remove_track_from_category)
        track_buttons.addWidget(self.remove_track_btn)
        track_panel.addLayout(track_buttons)

        middle_layout.addLayout(track_panel, 3)

        # Информация о текущей категории
        info_panel = QVBoxLayout()
        info_panel.addWidget(QLabel("Треки в категории (двойной клик для воспроизведения):"))
        self.category_tracks_list = QListWidget()
        self.category_tracks_list.itemDoubleClicked.connect(self.play_category_track)
        info_panel.addWidget(self.category_tracks_list)

        middle_layout.addLayout(info_panel, 2)

        main_layout.addLayout(middle_layout)

        # === Нижняя часть: Управление воспроизведением ===
        control_frame = QFrame()
        control_frame.setStyleSheet("background-color: #16213e; border-radius: 10px; padding: 10px;")
        control_layout = QVBoxLayout(control_frame)

        # Текущий трек
        self.current_track_label = QLabel("Не воспроизводится")
        self.current_track_label.setAlignment(Qt.AlignCenter)
        self.current_track_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #e4e4e7;")
        control_layout.addWidget(self.current_track_label)

        # Кнопки управления
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(15)

        # Стиль для больших кнопок управления
        control_btn_style = """
            QPushButton {
                background-color: #0f3460;
                color: #e4e4e7;
                border: 2px solid #1f4068;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1f4068;
                border-color: #e4e4e7;
            }
            QPushButton:pressed {
                background-color: #0a2540;
            }
        """

        self.play_btn = QPushButton("PLAY")
        self.play_btn.setFixedSize(80, 50)
        self.play_btn.setStyleSheet(control_btn_style)
        self.play_btn.clicked.connect(self.play)
        buttons_layout.addWidget(self.play_btn)

        self.pause_btn = QPushButton("PAUSE")
        self.pause_btn.setFixedSize(80, 50)
        self.pause_btn.setStyleSheet(control_btn_style)
        self.pause_btn.clicked.connect(self.pause)
        buttons_layout.addWidget(self.pause_btn)

        self.stop_btn = QPushButton("STOP")
        self.stop_btn.setFixedSize(80, 50)
        self.stop_btn.setStyleSheet(control_btn_style)
        self.stop_btn.clicked.connect(self.stop)
        buttons_layout.addWidget(self.stop_btn)

        self.next_btn = QPushButton("NEXT")
        self.next_btn.setFixedSize(80, 50)
        self.next_btn.setStyleSheet(control_btn_style)
        self.next_btn.clicked.connect(self.next_track)
        buttons_layout.addWidget(self.next_btn)

        self.loop_btn = QPushButton("LOOP")
        self.loop_btn.setFixedSize(80, 50)
        self.loop_btn.setCheckable(True)
        self.loop_btn.setToolTip("Зацикливание текущего трека")
        self.loop_btn.setStyleSheet(control_btn_style)
        self.loop_btn.clicked.connect(self.toggle_loop)
        buttons_layout.addWidget(self.loop_btn)

        buttons_layout.addStretch()

        # Громкость
        volume_layout = QHBoxLayout()
        volume_label_text = QLabel("VOL:")
        volume_label_text.setStyleSheet("font-size: 14px; font-weight: bold;")
        volume_layout.addWidget(volume_label_text)

        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(50)
        self.volume_slider.setFixedWidth(200)
        self.volume_slider.valueChanged.connect(self.set_volume)
        volume_layout.addWidget(self.volume_slider)

        self.volume_label = QLabel("50%")
        self.volume_label.setFixedWidth(50)
        self.volume_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        volume_layout.addWidget(self.volume_label)

        buttons_layout.addLayout(volume_layout)

        control_layout.addLayout(buttons_layout)
        main_layout.addWidget(control_frame)

        self.load_music_files()
        self.update_drumpad()

    def update_drumpad(self):
        """Обновляет сетку drumpad кнопок"""
        # Очищаем старые кнопки
        for btn in self.drumpad_buttons.values():
            btn.deleteLater()
        self.drumpad_buttons.clear()

        # Очищаем сетку
        while self.drumpad_grid.count():
            item = self.drumpad_grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Создаем кнопки для каждой категории
        categories_list = list(self.categories.items())
        cols = 6  # Количество колонок

        for i, (category_name, category_data) in enumerate(categories_list):
            btn = CategoryDrumpadButton(category_name, category_data)
            btn.clicked.connect(lambda checked, name=category_name: self.on_drumpad_click(name))

            row = i // cols
            col = i % cols
            self.drumpad_grid.addWidget(btn, row, col)
            self.drumpad_buttons[category_name] = btn

            # Обновляем активное состояние
            if category_name == self.current_category_playing and self.is_playing:
                btn.set_active(True)

    def on_drumpad_click(self, category_name):
        """Обработчик клика по drumpad кнопке"""
        self.play_random_from_category_by_name(category_name)
        self.show_category_tracks(category_name)

    def show_category_tracks(self, category_name):
        """Показывает треки выбранной категории"""
        self.category_tracks_list.clear()
        tracks = self.categories.get(category_name, {}).get('tracks', [])
        for track in tracks:
            self.category_tracks_list.addItem(track)

    def setup_shortcuts(self):
        for key in range(1, 10):
            shortcut = QShortcut(QKeySequence(str(key)), self)
            shortcut.activated.connect(lambda k=key: self.play_from_hotkey(k))

        # Пробел - пауза/воспроизведение
        self.space_shortcut = QShortcut(QKeySequence("Space"), self)
        self.space_shortcut.activated.connect(self.toggle_play_pause)

        # Стрелки - громкость
        self.volume_up_shortcut = QShortcut(QKeySequence("Up"), self)
        self.volume_up_shortcut.activated.connect(self.volume_up)

        self.volume_down_shortcut = QShortcut(QKeySequence("Down"), self)
        self.volume_down_shortcut.activated.connect(self.volume_down)

    def volume_up(self):
        """Увеличить громкость на 5%"""
        current = self.volume_slider.value()
        self.volume_slider.setValue(min(100, current + 5))

    def volume_down(self):
        """Уменьшить громкость на 5%"""
        current = self.volume_slider.value()
        self.volume_slider.setValue(max(0, current - 5))

    def toggle_play_pause(self):
        if self.is_playing and not self.is_paused:
            self.pause()
        elif self.is_paused:
            self.play()
        elif not self.is_playing and self.current_track:
            self.play_track(self.current_track)

    def play_from_hotkey(self, key):
        for category_name, category_data in self.categories.items():
            if category_data.get('hotkey') == str(key):
                self.play_random_from_category_by_name(category_name)
                self.show_category_tracks(category_name)
                break

    def load_music_files(self):
        music_dir = "music"
        if not os.path.exists(music_dir):
            os.makedirs(music_dir)
            QMessageBox.information(self, "Информация",
                                    f"Создана папка '{music_dir}'. Добавьте туда музыкальные файлы.")
            return

        supported_formats = ('.mp3', '.wav', '.ogg', '.flac')
        music_files = []

        for file in os.listdir(music_dir):
            if file.lower().endswith(supported_formats):
                music_files.append(file)

        self.track_list.clear()
        for file in sorted(music_files):
            self.track_list.addItem(file)

    def load_settings(self):
        try:
            with open('player_settings.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.categories = data.get('categories', {})

                # Добавляем стандартные значения для icon и color если их нет
                for category_name, category_data in self.categories.items():
                    if 'icon' not in category_data:
                        category_data['icon'] = 'music'
                    if 'color' not in category_data:
                        # Назначаем цвет из палитры по индексу
                        idx = list(self.categories.keys()).index(category_name) % len(COLOR_PALETTE)
                        category_data['color'] = COLOR_PALETTE[idx]
                    self.category_track_index[category_name] = 0
        except FileNotFoundError:
            self.categories = {
                "Битва": {"tracks": [], "hotkey": "1", "icon": "swords", "color": COLOR_PALETTE[0]},
                "Таверна": {"tracks": [], "hotkey": "2", "icon": "tavern", "color": COLOR_PALETTE[4]},
                "Город": {"tracks": [], "hotkey": "3", "icon": "castle", "color": COLOR_PALETTE[7]}
            }
            for category_name in self.categories:
                self.category_track_index[category_name] = 0

    def save_settings(self):
        with open('player_settings.json', 'w', encoding='utf-8') as f:
            json.dump({'categories': self.categories}, f, ensure_ascii=False, indent=2)

    def add_category(self):
        dialog = CategoryDialog(self)
        dialog.setStyleSheet(DARK_THEME_STYLE)
        if dialog.exec_():
            data = dialog.get_data()
            name = data['name']
            if name and name not in self.categories:
                self.categories[name] = {
                    "tracks": [],
                    "hotkey": data['hotkey'],
                    "icon": data['icon'],
                    "color": data['color']
                }
                self.category_track_index[name] = 0
                self.update_drumpad()
                self.save_settings()

    def remove_category(self):
        # Используем диалог выбора категории
        category_names = list(self.categories.keys())
        if not category_names:
            QMessageBox.warning(self, "Внимание", "Нет категорий для удаления")
            return

        category_name, ok = QInputDialog.getItem(
            self, "Удалить категорию", "Выберите категорию:", category_names, 0, False
        )
        if ok and category_name:
            reply = QMessageBox.question(self, "Подтверждение",
                                         f"Удалить категорию '{category_name}'?")
            if reply == QMessageBox.Yes:
                del self.categories[category_name]
                if category_name in self.category_track_index:
                    del self.category_track_index[category_name]
                if category_name == self.current_category_playing:
                    self.current_category_playing = None
                self.update_drumpad()
                self.save_settings()

    def edit_category(self):
        category_names = list(self.categories.keys())
        if not category_names:
            QMessageBox.warning(self, "Внимание", "Нет категорий для редактирования")
            return

        category_name, ok = QInputDialog.getItem(
            self, "Редактировать категорию", "Выберите категорию:", category_names, 0, False
        )
        if ok and category_name:
            category_data = self.categories[category_name]
            existing_data = {
                'name': category_name,
                'hotkey': category_data.get('hotkey', '1'),
                'icon': category_data.get('icon', 'music'),
                'color': category_data.get('color', COLOR_PALETTE[0])
            }

            dialog = CategoryDialog(self, existing_data)
            dialog.setStyleSheet(DARK_THEME_STYLE)

            if dialog.exec_():
                new_data = dialog.get_data()
                new_name = new_data['name']

                if new_name and new_name != category_name:
                    # Переименование категории
                    self.categories[new_name] = self.categories.pop(category_name)
                    self.category_track_index[new_name] = self.category_track_index.pop(category_name, 0)
                    if self.current_category_playing == category_name:
                        self.current_category_playing = new_name
                    category_name = new_name

                self.categories[category_name]['hotkey'] = new_data['hotkey']
                self.categories[category_name]['icon'] = new_data['icon']
                self.categories[category_name]['color'] = new_data['color']

                self.update_drumpad()
                self.save_settings()

    def add_track_to_category(self):
        track_item = self.track_list.currentItem()
        if not track_item:
            QMessageBox.warning(self, "Внимание", "Выберите трек")
            return

        category_names = list(self.categories.keys())
        if not category_names:
            QMessageBox.warning(self, "Внимание", "Нет категорий")
            return

        category_name, ok = QInputDialog.getItem(
            self, "Добавить в категорию", "Выберите категорию:", category_names, 0, False
        )

        if ok and category_name:
            track_name = track_item.text()
            if track_name not in self.categories[category_name]['tracks']:
                self.categories[category_name]['tracks'].append(track_name)
                self.update_drumpad()
                self.save_settings()
                QMessageBox.information(self, "Успех", f"Трек добавлен в '{category_name}'")
                self.show_category_tracks(category_name)
            else:
                QMessageBox.information(self, "Информация", "Трек уже в этой категории")

    def remove_track_from_category(self):
        category_names = list(self.categories.keys())
        if not category_names:
            QMessageBox.warning(self, "Внимание", "Нет категорий")
            return

        category_name, ok = QInputDialog.getItem(
            self, "Удалить из категории", "Выберите категорию:", category_names, 0, False
        )

        if ok and category_name:
            tracks = self.categories[category_name]['tracks']
            if tracks:
                track_name, ok = QInputDialog.getItem(
                    self, "Удалить трек", "Выберите трек:", tracks, 0, False
                )
                if ok and track_name:
                    self.categories[category_name]['tracks'].remove(track_name)
                    if (self.current_category_playing == category_name and
                            self.category_track_index[category_name] >= len(self.categories[category_name]['tracks'])):
                        self.category_track_index[category_name] = 0
                    self.update_drumpad()
                    self.save_settings()
                    self.show_category_tracks(category_name)
            else:
                QMessageBox.warning(self, "Внимание", f"В категории '{category_name}' нет треков")

    def play_selected_track(self, item):
        self.current_category_playing = None
        self.update_active_drumpad(None)
        self.play_track(item.text())

    def play_category_track(self, item):
        """Воспроизводит выбранный трек из списка категории"""
        track_name = item.text()
        self.play_track(track_name)

        # Выделяем трек в основном списке
        for i in range(self.track_list.count()):
            if self.track_list.item(i).text() == track_name:
                self.track_list.setCurrentRow(i)
                break

    def play_track(self, track_name):
        try:
            pygame.mixer.music.stop()
            pygame.mixer.music.load(os.path.join("music", track_name))

            # Используем -1 для бесконечного зацикливания если loop_mode включен
            if self.loop_mode:
                pygame.mixer.music.play(-1)  # Бесконечное повторение
            else:
                pygame.mixer.music.play()

            self.current_track = track_name
            self.is_playing = True
            self.is_paused = False
            self.current_track_label.setText(f"Now playing: {track_name}")

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось воспроизвести трек: {str(e)}")

    def play(self):
        if self.is_paused:
            pygame.mixer.music.unpause()
            self.is_paused = False
            self.is_playing = True
        else:
            current_item = self.track_list.currentItem()
            if current_item:
                self.current_category_playing = None
                self.update_active_drumpad(None)
                self.play_track(current_item.text())

    def pause(self):
        if self.is_playing and not self.is_paused:
            pygame.mixer.music.pause()
            self.is_paused = True

    def stop(self):
        pygame.mixer.music.stop()
        self.is_playing = False
        self.is_paused = False
        self.current_category_playing = None
        self.update_active_drumpad(None)
        self.current_track_label.setText("Не воспроизводится")

    def next_track(self):
        if self.current_category_playing and self.current_category_playing in self.categories:
            self.play_next_in_category(self.current_category_playing)
        else:
            current_row = self.track_list.currentRow()
            if current_row < self.track_list.count() - 1:
                self.track_list.setCurrentRow(current_row + 1)
                self.play_track(self.track_list.currentItem().text())

    def toggle_loop(self):
        self.loop_mode = not self.loop_mode
        self.loop_btn.setChecked(self.loop_mode)

        if self.loop_mode:
            self.loop_btn.setStyleSheet("""
                QPushButton {
                    background-color: #4a0080;
                    color: #e4e4e7;
                    border: 2px solid #e4e4e7;
                    border-radius: 8px;
                    font-size: 14px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #5a0090;
                }
            """)
        else:
            self.loop_btn.setStyleSheet("""
                QPushButton {
                    background-color: #0f3460;
                    color: #e4e4e7;
                    border: 2px solid #1f4068;
                    border-radius: 8px;
                    font-size: 14px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #1f4068;
                    border-color: #e4e4e7;
                }
                QPushButton:pressed {
                    background-color: #0a2540;
                }
            """)

        # Если музыка играет, перезапускаем с нужным режимом зацикливания
        if self.is_playing and not self.is_paused and self.current_track:
            # Сохраняем текущую позицию
            pos = pygame.mixer.music.get_pos()
            pygame.mixer.music.stop()
            pygame.mixer.music.load(os.path.join("music", self.current_track))
            if self.loop_mode:
                pygame.mixer.music.play(-1)
            else:
                pygame.mixer.music.play()
            # Пытаемся вернуться к позиции (может не работать для всех форматов)
            if pos > 0:
                try:
                    pygame.mixer.music.set_pos(pos / 1000.0)
                except:
                    pass  # Некоторые форматы не поддерживают seek

    def set_volume(self, value):
        volume = value / 100.0
        pygame.mixer.music.set_volume(volume)
        if hasattr(self, 'volume_label'):
            self.volume_label.setText(f"{value}%")

    def play_random_from_category_by_name(self, category_name):
        tracks = self.categories[category_name].get('tracks', [])
        if tracks:
            self.current_category_playing = category_name
            self.update_active_drumpad(category_name)

            random_index = random.randint(0, len(tracks) - 1)
            self.category_track_index[category_name] = random_index
            random_track = tracks[random_index]

            self.play_track(random_track)

            for i in range(self.track_list.count()):
                if self.track_list.item(i).text() == random_track:
                    self.track_list.setCurrentRow(i)
                    break
        else:
            QMessageBox.warning(self, "Внимание", f"В категории '{category_name}' нет треков")

    def update_active_drumpad(self, active_category):
        """Обновляет активное состояние drumpad кнопок"""
        for category_name, btn in self.drumpad_buttons.items():
            btn.set_active(category_name == active_category)

    def play_next_in_category(self, category_name):
        tracks = self.categories[category_name].get('tracks', [])
        if tracks:
            self.category_track_index[category_name] = (self.category_track_index[category_name] + 1) % len(tracks)
            next_track = tracks[self.category_track_index[category_name]]

            self.play_track(next_track)

            for i in range(self.track_list.count()):
                if self.track_list.item(i).text() == next_track:
                    self.track_list.setCurrentRow(i)
                    break
        else:
            QMessageBox.warning(self, "Внимание", f"В категории '{category_name}' нет треков")

    def check_track_end(self):
        """Проверяет окончание трека и запускает следующий при необходимости"""
        if self.is_playing and not self.is_paused and not pygame.mixer.music.get_busy():
            # Трек закончился
            if self.loop_mode:
                # При loop_mode музыка должна зацикливаться сама (play(-1))
                # Этот случай не должен происходить, но на всякий случай
                pass
            elif self.current_category_playing:
                # Если воспроизводим категорию без зацикливания - следующий трек
                self.play_next_in_category(self.current_category_playing)
            else:
                # Трек закончился сам, обновляем статус
                self.is_playing = False
                self.current_track_label.setText("Не воспроизводится")

    def closeEvent(self, event):
        self.stop()
        self.save_settings()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    player = MusicPlayer()
    player.show()
    sys.exit(app.exec_())
