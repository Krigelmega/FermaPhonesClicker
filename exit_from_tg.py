import subprocess
import time
import threading
from concurrent.futures import ThreadPoolExecutor
from devices import ips

ACTIONS = [
    {'x': 537, 'y': 1548, 'delay': 1},  # недавние приложения
    {'x': 356, 'y': 1358, 'delay': 1},  # закрыть все
    {'x': 85, 'y': 1409, 'delay': 3}, # открыть тг
]

hot_actions = [
               {'x': 96, 'y': 420, 'delay': 2},  # недавние приложения
               {'x': 318, 'y': 1343, 'delay': 15},
               {'x': 643, 'y': 267, 'delay': 2},
               {'x': 643, 'y': 267, 'delay': 2},
               {'x': 309, 'y': 576, 'delay': 1},
]

tap_swap_actions = [{'x': 53, 'y': 158, 'delay': 3}, # открытие акков
                {'x': 136, 'y': 460, 'delay': 4} # выбор первого
                ]



def run_adb_command(command):
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout = result.stdout.decode('utf-8') if result.stdout else ''
    stderr = result.stderr.decode('utf-8') if result.stderr else ''
    return stdout, stderr


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

def connect_device(IP_ADDRESSES):
    successful_ips = []
    skipped_ips = []
    failed_ips = []

    for ip in IP_ADDRESSES:
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

    print(f"{len(successful_ips)}/{len(IP_ADDRESSES)} устройств подключены.")




def disconnect_device(ip_address):
    try:
        command = f"adb disconnect {ip_address}"
        subprocess.run(command, shell=True, check=True)
        print(f"Disconnecting from {ip_address}")
    except subprocess.CalledProcessError as e:
        print(f"Ошибка при отключении устройства с IP {ip_address}: {e}")


def perform_tap(ip_address, action, retries=3):
    for attempt in range(retries):
        try: # Wait for resume signal if paused
            command = f'adb -s {ip_address} shell input tap {action["x"]} {action["y"]}'
            result = subprocess.run(command, shell=True, check=False)
            time.sleep(action.get("delay", 1))
            return True
        except subprocess.CalledProcessError as e:
            print(f"Command failed on {ip_address}: {e}")
            if "device offline" in str(e) or "error: closed" in str(e) or 'not found' in str(e):
                disconnect_device(ip_address)
                if connect_device(ip_address):
                    print(f"Reconnected to {ip_address}")
                else:
                    print(f"Failed to reconnect to {ip_address}")
                    return False
            else:
                time.sleep(3)  # задержка перед повторной попыткой
    return False

def execute_actions(ip_address, actions):
    for action in actions:
        if not perform_tap(ip_address, action):
            return False
    return True
def exit_tg(ip_address, actions):
    if not execute_actions(ip_address, actions):
        print("Telegram был перезагружен")
        return


IP_ADDRESSES = ips  # Добавьте сюда IP-адреса своих устройств

def main():
    treads = []
    for ip_address in IP_ADDRESSES:
        thread = threading.Thread(target=exit_tg, args=(ip_address, ACTIONS))
        thread.start()
        treads.append(thread)
    for tread in treads:
        tread.join()


def post_main():
    treads = []
    for ip_address in IP_ADDRESSES:
        if ip_address == '192.168.0.132' or ip_address == '192.168.0.75' or ip_address == '192.168.0.115' or ip_address == '192.168.0.99' or ip_address == '192.168.0.79':
            thread = threading.Thread(target=exit_tg, args=(ip_address, tap_swap_actions))
            thread.start()
            treads.append(thread)

    for tread in treads:
        tread.join()
def get_text():
    main()
    time.sleep(2)
    post_main()
    print('--------------------------------------')
    print('ВСЕ ТЕЛЕФОНЫ БЫЛИ ПЕРЕЗАГРУЖЕНЫ ')
    print('--------------------------------------')
    return 'Устройства готовы к работе'

