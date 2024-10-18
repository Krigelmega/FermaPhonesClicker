import subprocess
import time
from devices import ips

# Список IP-адресов телефонов
phone_ips = ips


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
            # if input().lower() != 'q':
            continue
            # else:
            #     return False
        else:
            time.sleep(2)
            result_stdout, result_stderr = run_adb_command(['adb', 'connect', ip])
            if 'cannot' not in result_stdout.lower():
                print("Successfully connected to the device.")
                return True
            else:
                print(f"\nПодключите устройство с IP {ip} по USB и нажмите Enter, Q для пропуска.")
                # if input().lower() != 'q':
                continue
                # else:
                #     return False


def main():
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


def maim():
    main()
    return 'Устройства перезапущены'

#
# import sys
# import subprocess
# import time
#
# phone_ips = [
#     '192.168.0.28',
#     '192.168.0.18',
#     '192.168.0.47',
#     '192.168.0.88',
#     '192.168.0.90',
#     '192.168.0.38',
#     '192.168.0.22',
#     '192.168.0.14',
#     '192.168.0.71',
#     '192.168.0.91',
#     '192.168.0.85',
#     '192.168.0.93',
#     '192.168.0.63',
#     '192.168.0.62',
#     '192.168.0.59',
#     '192.168.0.77'
# ]
#
# def run_adb_command(command):
#     result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
#     stdout = result.stdout.decode('utf-8') if result.stdout else ''
#     stderr = result.stderr.decode('utf-8') if result.stderr else ''
#     return stdout, stderr
#
# def wait_for_device():
#     while True:
#         output, _ = run_adb_command(['adb', 'devices'])
#         lines = output.strip().split('\n')[1:]  # Пропускаем первую строку "List of devices attached"
#         if lines:
#             for line in lines:
#                 if 'device' in line and 'offline' not in line:
#                     return line.split('\t')[0]
#         time.sleep(1)
#
# def connect_to_phone(ip):
#     print(f"Trying to connect to device with IP: {ip}")
#     result_stdout, result_stderr = run_adb_command(['adb', 'connect', ip])
#     time.sleep(1)
#     if 'cannot' in result_stdout.lower():
#         while 'cannot' in result_stdout.lower():
#             print("Failed to connect to the device. Restarting ADB server...")
#             print(f'Подключите устройство {ip} и нажмите Enter или q для пропуска')
#             inn = input()
#             if inn.lower() == 'q':
#                 return False
#             usb_device = wait_for_device()
#             print(f"Устройство {usb_device} подключено. Выполняю команды...")
#             run_adb_command(['adb', 'kill-server'])
#             time.sleep(1)
#             print(run_adb_command(['adb', 'usb']))
#             time.sleep(1)
#             output, error = run_adb_command(['adb', 'tcpip', '5555'])
#             print(output, error)
#             if 'error: no devices/emulators found' in error or 'error: device offline' in error or 'device still authorizing' in error:
#                 print("Ошибка: устройство не найдено или offline. Повторная попытка...")
#                 continue
#             else:
#                 result_stdout, result_stderr = run_adb_command(['adb', 'connect', ip])
#                 print(result_stdout, result_stderr)
#                 if 'cannot' not in result_stdout.lower():
#                     print("Successfully connected to the device.")
#                     print('---------------------------------------')
#                     return True
#     else:
#         print("Successfully connected to the device.")
#         print('---------------------------------------')
#         return True
#
# def main():
#     run_adb_command(['adb', 'kill-server'])
#     print("Switching ADB to USB mode...")
#     run_adb_command(['adb', 'usb'])
#     print("Switching ADB to TCP/IP mode...")
#     run_adb_command(['adb', 'tcpip', '5555'])
#
#     successful_connections = 0
#
#     for ip in phone_ips:
#         connected = connect_to_phone(ip)
#         if connected:
#             successful_connections += 1
#
#     print(f"Successfully connected to {successful_connections} out of {len(phone_ips)} devices.")
#
# if __name__ == '__main__':
#     main()
