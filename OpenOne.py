import sys
import subprocess
import time
import cv2
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QDialog, QGridLayout, QMenu, QAction, QListWidget, QListWidgetItem
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import QTimer, Qt, QRect, QPoint
from devices import ips

def add_name(device):
    device = device.strip().split(':')[0]

    if device == '192.168.0.140':
        name = 'Baby Naste (1)'
    elif device == '192.168.0.44':
        name = 'Leonar 2 (2)'
    elif device == '192.168.0.58':
        name = 'Markus Volorant (3)'
    elif device == '192.168.0.77':
        name = 'Виктор Кутуз (4)'
    elif device == '192.168.0.88':
        name = "Марк (5)"
    elif device == '192.168.0.65':
        name = 'Валя Карнавал (6)'
    elif device == '192.168.0.109':
        name = 'Любовь Буркова (7)'
    elif device == '192.168.0.127':
        name = 'Benzo Gang'
    elif device == '192.168.0.66':
        name = 'Мария (8)'
    elif device == '192.168.0.132':
        name = 'Катя (9)'
    elif device == '192.168.0.75':
        name = 'Benzo Gang (10)'
    elif device == '192.168.0.115':
        name = 'Benzo Gang (12)'
    elif device == '192.168.0.99':
        name = 'Anastasia (11)'
    elif device == '192.168.0.93':
        name = 'Настасья (13)'
    elif device == '':
        name = 'Хайпажор (15)'
    elif device == '192.168.0.81':
        name = 'Мария (10)'
    elif device == '192.168.0.9':
        name = 'Юрий'
    else:
        name = 'None'
    return name


class DeviceSelectionDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Выбор устройства')
        layout = QVBoxLayout()
        self.setLayout(layout)

        self.devices_list = QListWidget()
        devices = get_connected_devices()  # Получаем список устройств
        sorted_devices = sorted(devices, key=lambda x: int(x[1].split('(')[-1].split(')')[0]))

        for ip_address in phone_ips:
            name = add_name(ip_address)
            combined_text = f"{ip_address} - {name}"
            item = QListWidgetItem(combined_text)
            self.devices_list.addItem(item)

        layout.addWidget(self.devices_list)

        select_button = QPushButton('Подключиться')
        select_button.clicked.connect(self.select_device)
        layout.addWidget(select_button)

        self.selected_device = None

    def select_device(self):
        selected_item = self.devices_list.currentItem()
        if selected_item:
            self.selected_device = selected_item.text().split(' - ')[0]  # Извлекаем IP-адрес устройства
            self.accept()


class PhoneScreenWidget(QWidget):
    def __init__(self, device_id, x, y, width, height):
        super().__init__()
        self.device_id = device_id
        self.original_geometry = QRect(x, y, width, height)
        self.setGeometry(self.original_geometry)
        self.is_fullscreen = False

        self.label = QLabel(self)
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.label)
        self.setLayout(self.layout)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)
        self.scrcpy_process = None
        self.start_scrcpy()

        self.label.setMouseTracking(True)
        self.label.mousePressEvent = self.mousePressEvent
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)

    def start_scrcpy(self):
        try:
            command = [
                'scrcpy',
                '--serial', self.device_id,
                '--stay-awake',
                '--tcpip', '--window-title', self.device_id,
                '--window-x', str(self.geometry().x()),
                '--window-y', str(self.geometry().y()),
                '--window-width', str(self.geometry().width()),
                '--window-height', str(self.geometry().height())
            ]
            self.scrcpy_process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except Exception as e:
            print(f"Ошибка при запуске scrcpy для устройства {self.device_id}: {e}")
            QTimer.singleShot(5000, self.start_scrcpy)  # Попробовать перезапустить через 5 секунд

    def update_frame(self):
        try:
            cap = cv2.VideoCapture('tcp://localhost:5555')
            ret, frame = cap.read()
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                height, width, channel = frame.shape
                step = channel * width
                qImg = QImage(frame.data, width, height, step, QImage.Format_RGB888)
                self.label.setPixmap(QPixmap.fromImage(qImg))
            cap.release()
        except Exception as e:
            print(f"Ошибка при обновлении кадра для устройства {self.device_id}: {e}")

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.send_event('tap', event)
        elif event.button() == Qt.RightButton:
            self.show_context_menu(event.pos())

    def send_event(self, event_type, event):
        try:
            x = event.x()
            y = event.y()
            width = self.label.width()
            height = self.label.height()
            device_x = int(x * 1080 / width)
            device_y = int(y * 1920 / height)

            if event_type == 'tap':
                subprocess.run(['adb', '-s', self.device_id, 'shell', 'input', 'tap', str(device_x), str(device_y)])
            elif event_type == 'move':
                subprocess.run(
                    ['adb', '-s', self.device_id, 'shell', 'input', 'swipe', str(device_x), str(device_y), str(device_x),
                     str(device_y), '100'])
        except Exception as e:
            print(f"Ошибка при отправке события для устройства {self.device_id}: {e}")

    def show_context_menu(self, position):
        context_menu = QMenu(self)
        toggle_fullscreen_action = QAction("Toggle Fullscreen", self)
        toggle_fullscreen_action.triggered.connect(self.toggle_fullscreen)
        context_menu.addAction(toggle_fullscreen_action)
        context_menu.exec_(self.mapToGlobal(position))

    def toggle_fullscreen(self):
        if self.is_fullscreen:
            self.setGeometry(self.original_geometry)
        else:
            primary_screen = QApplication.primaryScreen()
            primary_geometry = primary_screen.geometry()
            self.setGeometry(primary_geometry)
        self.is_fullscreen = not self.is_fullscreen

    def closeEvent(self, event):
        self.timer.stop()
        if self.scrcpy_process:
            self.scrcpy_process.terminate()
            self.scrcpy_process.wait()



phone_ips = ips
def get_connected_devices():
    result = subprocess.run(['adb', 'devices'], stdout=subprocess.PIPE)
    output = result.stdout.decode('utf-8').strip().split('\n')[1:]
    devices = [line.split('\t')[0] for line in output if 'device' in line]
    # Создаем словарь для быстрого доступа к индексам устройств по их IP-адресам
    device_index = {device: phone_ips.index(device) for device in devices if device in phone_ips}
    # Сортируем устройства по их индексам в списке phone_ips
    sorted_devices = sorted(devices, key=lambda x: device_index.get(x, len(phone_ips)))
    return sorted_devices


def main():
    app = QApplication(sys.argv)
    dialog = DeviceSelectionDialog()
    if dialog.exec_() == QDialog.Accepted:
        device_id = dialog.selected_device
        viewer = PhoneScreenWidget(device_id, 100, 100, 426, 470)
        viewer.show()

def maain():
    main()
    return 'Просмотр экрана одного устройства начался'

