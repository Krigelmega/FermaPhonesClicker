import sys
import subprocess
import time

import cv2
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QDialog, QGridLayout, QMenu, QAction
from PyQt5.QtGui import QPixmap, QImage, QFont
from PyQt5.QtCore import QTimer, Qt, QRect, QPoint
from devices import ips

class DeviceSelectionDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Выбор устройства')
        self.resize(230, 105)

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.selected_device = None
        self.row_count = 4  # По умолчанию для телевизора

        computer_button = QPushButton('Телевизор')
        computer_button.clicked.connect(self.select_computer)
        layout.addWidget(computer_button)

        phone_button = QPushButton('Компьютер')
        phone_button.clicked.connect(self.select_phone)
        layout.addWidget(phone_button)

    def select_computer(self):
        self.selected_device = "computer"
        self.row_count = 10  # Для компьютера
        self.accept()

    def select_phone(self):
        self.selected_device = "phone"
        self.row_count = 8  # Для телефона
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
                '--window-height', str(self.geometry().height()),
                '--window-borderless'
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


class MultiPhoneViewer(QWidget):
    def __init__(self, device_type, max_columns):
        super().__init__()
        self.setWindowTitle('Multi Phone Viewer')
        self.layout = QGridLayout()
        self.setLayout(self.layout)
        self.devices = []
        self.device_type = device_type
        self.width, self.height = (70, 273) if self.device_type == "computer" else (70, 270)
        self.max_columns = max_columns  # Максимальное количество столбцов
        self.current_row = 0  # Текущая строка
        self.current_column = 0  # Текущий столбец
        self.update_devices()
        self.timer = QTimer(self)

        self.timer.timeout.connect(self.update_devices)
        self.timer.start(5000)

    def update_devices(self):
        screens = QApplication.screens()
        primary_screen = screens[0]
        second_screen = screens[2] if len(screens) > 2 else None

        connected_devices = get_connected_devices()
        devices = sort_connected_devices(connected_devices, phone_ips)
        ip_addresses = ips

        result = subprocess.run(['adb', 'devices'], stdout=subprocess.PIPE)
        output = result.stdout.decode('utf-8').strip().split('\n')[1:]
        connected_devices = [line.split('\t')[0] for line in output if 'device' in line]
        print(f'Подключенных устройств: {len(connected_devices)}/{len(ip_addresses)}')

        if len(ip_addresses) != len(connected_devices):
            new_two = []
            spisok_ip = []
            for element in ip_addresses:
                new_two.append(element + ':5555')

            set1 = set(connected_devices)
            set2 = set(new_two)
            unique_elements = set1.symmetric_difference(set2)
            for e in unique_elements:
                spisok_ip.append(e[-7:-5])
            print(f'\nТелефоны с номерами {spisok_ip} не были подключены')
        print(f"Обновление списка устройств... ({len(devices)})")

        # Очищаем сетку перед обновлением
        for i in reversed(range(self.layout.count())):
            widget = self.layout.itemAt(i).widget()
            self.layout.removeWidget(widget)
            widget.deleteLater()

        for index, device_id in enumerate(ip_addresses):
            if device_id not in self.devices:
                print(f"Новое устройство ACTIVE: {device_id}")
                self.devices.append(device_id)
                x, y = self.calculate_position(index, primary_screen.geometry())
                if self.device_type == 'computer' and second_screen:
                    x, y = self.calculate_position(index, second_screen.geometry())
                phone_screen = PhoneScreenWidget(device_id, x, y, self.width, self.height)
                self.layout.addWidget(phone_screen, self.current_row, self.current_column)
                time.sleep(3)
                self.current_column += 1
                if self.current_column == self.max_columns:  # Если достигнут максимальный столбец
                    self.current_row += 1
                    self.current_column = 0


    def calculate_position(self, index, geometry):
        row = index // self.max_columns
        column = index % self.max_columns
        x = geometry.x() + column * self.width
        y = geometry.y() + row * self.height
        return x, y


phone_ips = ips

def get_connected_devices():
    result = subprocess.run(['adb', 'devices'], stdout=subprocess.PIPE)
    output = result.stdout.decode('utf-8').strip().split('\n')[1:]
    devices = [line.split('\t')[0] for line in output if 'device' in line]
    return devices

def sort_connected_devices(connected_devices, phone_ips):
    ip_index = {ip: index for index, ip in enumerate(phone_ips)}
    sorted_devices = sorted(connected_devices, key=lambda ip: ip_index.get(ip, len(phone_ips)))
    return sorted_devices





def run_adb_command(command):
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout = result.stdout.decode('utf-8') if result.stdout else ''
    stderr = result.stderr.decode('utf-8') if result.stderr else ''
    return stdout, stderr


def wait_for_device():
    while True:
        output, _ = run_adb_command(['adb', 'devices'])
        lines = output.strip().split('\n')[1:]  # Пропускаем первую строку "List of devices attached"
        if lines:
            for line in lines:
                if 'device' in line and 'offline' not in line:
                    return line.split('\t')[0]
        time.sleep(1)


def configure_device(ip):
    while True:
        run_adb_command(['adb', 'kill-server'])
        time.sleep(2)
        run_adb_command(['adb', 'usb'])
        time.sleep(2)
        output, error = run_adb_command(['adb', 'tcpip', '5555'])
        print(output, error)

        if 'error: no devices/emulators found' in error:
            continue
        elif 'error: device offline' in error or 'device still authorizing' in error:
            print("Ошибка: устройство не найдено или offline. Повторная попытка...")
            print(f"\nПодключите устройство с IP {ip} по USB и нажмите Enter, Q для пропуска.")
            if input().lower() != 'q':
                continue
            else:
                return False
        else:
            time.sleep(2)
            result_stdout, result_stderr = run_adb_command(['adb', 'connect', ip])
            if 'cannot' not in result_stdout.lower():
                print("Successfully connected to the device.")
                return True
            else:
                print(f"\nПодключите устройство с IP {ip} по USB и нажмите Enter, Q для пропуска.")
                if input().lower() != 'q':
                    continue
                else:
                    return False


def maain():
    successful_ips = []
    skipped_ips = []
    failed_ips = []

    for ip in phone_ips:
        print(f"\nTrying to connect to device with IP: {ip}")
        result_stdout, result_stderr = run_adb_command(['adb', 'connect', ip])
        if 'cannot' in result_stdout.lower():
            print(f"Failed to connect to {ip}. Attempting to configure device...")
            if configure_device(ip):
                successful_ips.append(ip)
            else:
                skipped_ips.append(ip)
                failed_ips.append(ip)
        else:
            print("Successfully connected to the device.")
            successful_ips.append(ip)

        # Attempt to reconnect previously connected devices
        for connected_ip in successful_ips:
            if connected_ip != ip:  # Skip the current IP
                run_adb_command(['adb', 'connect', connected_ip])

        # If there are failed connections, try to reconnect them as well
        for failed_ip in failed_ips:
            if failed_ip != ip:  # Skip the current IP
                result_stdout, result_stderr = run_adb_command(['adb', 'connect', failed_ip])
                if 'cannot' not in result_stdout.lower():
                    successful_ips.append(failed_ip)
                    failed_ips.remove(failed_ip)

    print(f"{len(successful_ips)}/{len(phone_ips)} устройств подключены.")


def mainmain():
    try:
        app = QApplication(sys.argv)
        dialog = DeviceSelectionDialog()
        if dialog.exec_() == QDialog.Accepted:
            device_type = dialog.selected_device
            if device_type == 'computer':
                viewer = MultiPhoneViewer(device_type, max_columns=4)
            else:
                viewer = MultiPhoneViewer(device_type, max_columns=10)
            viewer.show()
    except Exception as e:
        print('Error PhoneCast: ', e)
    return 'Просмотр экранов устройств начался'


