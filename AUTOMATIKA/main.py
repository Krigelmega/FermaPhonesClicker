import subprocess
import threading
import time
import tkinter as tk
import customtkinter
from tkinter.scrolledtext import ScrolledText
from tkinter import scrolledtext
import sys
from concurrent.futures import ThreadPoolExecutor
import logging
import queue



from exit_from_tg import get_text
from PhonesConnect import maim
from PhoneCast import mainmain
from OpenOne import maain
from AUTOMATIKA.auto import bot
# Список IP-адресов устройств
IP_ADDRESSES = ['192.168.0.52', '192.168.0.133',
                '192.168.0.93', '192.168.0.128',
                '192.168.0.76', '192.168.0.124',
                '192.168.0.94', '192.168.0.119',
                '192.168.0.73', '192.168.0.140',
                '192.168.0.44', '192.168.0.58',
                '192.168.0.77', '192.168.0.88',
                '192.168.0.65', '192.168.0.109',
                '192.168.0.127', '192.168.0.66',
                 '192.168.0.145', '192.168.0.45',
                '192.168.0.80', '192.168.0.72',
                '192.168.0.36', '192.168.0.113',
                '192.168.0.48', '192.168.0.121',
                '192.168.0.120', '192.168.0.53',
                '192.168.0.91', '192.168.0.54',
                '192.168.0.46', '192.168.0.102',
                '192.168.0.90', '192.168.0.134',
                '192.168.0.122', '192.168.0.47',
                '192.168.0.71', '192.168.0.123',
                '192.168.0.51'
                ]

SWAP_ADDRESSES = ['192.168.0.75', '192.168.0.99', '192.168.0.115', '192.168.0.158']



ALL_IP_ADDRESSES = IP_ADDRESSES + SWAP_ADDRESSES

running_flags = {}
pause_flags = {}
# До начала фарма хомяков
ACTIONS = [
    {'x': 90, 'y': 857, 'delay': 4}, # ЗАПУСК ЧАТА
    {'x': 91, 'y': 1155, 'delay': 2}, # ЗАПУСК ХОМЯКОВ
    {'x': 578, 'y': 910, 'delay': 30}, # начать
    {'x': 358, 'y': 1322, 'delay': 5}, # CLAIM
    {'x': 358, 'y': 1330, 'delay': 10}, # CLAIM
]

# Координаты для повторяющихся кликов и количество повторений
REPEATED_ACTIONS = [
    {'x': 300, 'y': 940, 'delay': 0.2},
    {'x': 274, 'y': 930, 'delay': 0.2},
    {'x': 480, 'y': 920, 'delay': 0.2},
]
REPEATS = 200  # Количество повторений

# ДЕЙСТВИЯ ПОСЛЕ ФАРМА ХОМЯКОВ
EXIT_ACTION = [{'x': 661, 'y': 161, 'delay': 3}, {'x': 661, 'y': 161, 'delay': 3}]

# ВЫХОД ИЗ ХОМЯКОВ
SWIPE_ACTION = [{'start_x': 90, 'start_y': 550, 'end_x': 550, 'end_y': 550, 'duration': 1000},
                {'start_x': 90, 'start_y': 550, 'end_x': 550, 'end_y': 550, 'duration': 1000}]

BACKSWIPE_ACTION = [{'start_x': 550, 'start_y': 1400, 'end_x': 90, 'end_y': 1400, 'duration': 1000},]

UNDER_SWIPE = [{'start_x': 350, 'start_y': 1300, 'end_x': 350, 'end_y': 250, 'duration': 1000},
               {'start_x': 350, 'start_y': 1300, 'end_x': 350, 'end_y': 250, 'duration': 1000},] # пролистывание hot вниз

MEME_ACTIONS = [{'x': 87, 'y': 718, 'delay': 5}, # запуск чата
                {'x': 91, 'y': 1155, 'delay': 2}, # запуск игры
                {'x': 578, 'y': 910, 'delay': 30}, # начать
                {'x': 671, 'y': 147, 'delay': 4}, # настройки
                {'x': 606, 'y': 256, 'delay': 4}, # обновить
                {'x': 373, 'y': 900, 'delay': 4}, # подготовительные клики
                {'x': 373, 'y': 900, 'delay': 4}, # подготовительные клики
                {'x': 373, 'y': 900, 'delay': 4}] # подготовительные клики


HOT_ACTIONS = [{'x': 520, 'y': 247, 'delay': 4}, # storage
                {'x': 540, 'y': 1040, 'delay': 20},
                {'x': 540, 'y': 690, 'delay': 4}, # если вылезает табличка
               ] # claim

HOT_ACTIONS2 = [{'x': 360, 'y': 830, 'delay': 3}, # еще раз claim

                {'x': 60, 'y': 152, 'delay': 4}, # назад
                {'x': 656, 'y': 270, 'delay': 4}, # настройки
                {'x': 656, 'y': 270, 'delay': 4}, # выбор акка
                {'x': 620, 'y': 710, 'delay': 4},] # выбор следующего акка

hot2_actions = [{'x': 620, 'y': 570, 'delay': 3},] # переключение на аккаунт krigelmega

hot_new_actions = [
               {'x': 96, 'y': 420, 'delay': 2},  # недавние приложения
               {'x': 318, 'y': 1343, 'delay': 15},
               {'x': 643, 'y': 267, 'delay': 2},
               {'x': 643, 'y': 267, 'delay': 2},
               {'x': 309, 'y': 576, 'delay': 1},
]

BLUM_ACTIONS = [
               {'x': 79, 'y': 563, 'delay': 5}, # вход в чат
               {'x': 79, 'y': 1250, 'delay': 2}, # вход в игру
               {'x': 578, 'y': 910, 'delay': 30}, # начать
               {'x': 150, 'y': 1448, 'delay': 4}] # если вылетает табличка с дневной наградой

new_blum_actions = [
               {'x': 370, 'y': 1287, 'delay': 5}, # claim
               {'x': 380, 'y': 1287, 'delay': 5}, # claim
               {'x': 390, 'y': 1287, 'delay': 5}, # claim
               {'x': 65, 'y': 153, 'delay': 5}, # выход
               {'x': 65, 'y': 153, 'delay': 5} # еще раз выход
]


VERTUS_ACTIONS = [
                {'x': 79, 'y': 260, 'delay': 3}, # вход в чат
                {'x': 79, 'y': 1155, 'delay': 2}, # вход в игру
                {'x': 578, 'y': 910, 'delay': 30}, # начать
                {'x': 380, 'y': 1247, 'delay': 2}, # сбор за день
                {'x': 380, 'y': 1247, 'delay': 10}, # сбор за день
                {'x': 505, 'y': 807, 'delay': 10}, # нажатие на хранилище
                {'x': 569, 'y': 1203, 'delay': 10}, # claim
                {'x': 198, 'y': 1087, 'delay': 10}, # claim
                {'x': 672, 'y': 171, 'delay': 10}, # выход
                {'x': 672, 'y': 171, 'delay': 10}, # выход
]


RESTART_ACTIONS = [
                {'x': 537, 'y': 1548, 'delay': 5}, # недавние приложения
                {'x': 356, 'y': 1358, 'delay': 5}, # закрыть все
                {'x': 85, 'y': 1409, 'delay': 10}, # открыть тг

]

TAPSWAP_ACTIONS = [{'x': 485, 'y': 1389, 'delay': 4}, # открытие boost
                   {'x': 217, 'y': 691, 'delay': 2}, # tapping guru
                   {'x': 366, 'y': 1397, 'delay': 2}, # get it

]

first_akk_actions = [{'x': 200, 'y': 470, 'delay': 5},]

SECOND_AKK_actions = [{'x': 200, 'y': 533, 'delay': 5},] # переключение на второй аккаунт

THIRD_AKK_actions = [{'x': 200, 'y': 627, 'delay': 5},] # переключение на третий аккаунт

TAPSWAP_FIRST_ACTIONS = [{'x': 165, 'y': 423, 'delay': 2}, #Заход в чат
                        {'x': 210, 'y': 1156, 'delay': 20}, #Заход в игру
                        {'x': 317, 'y': 1075, 'delay': 15}, #Проверка на бота
                        {'x': 620, 'y': 560, 'delay': 3}, #Проверка на бота
]

tap_swap_actions_nice = [{'x': 53, 'y': 158, 'delay': 3}, # открытие акков
                {'x': 136, 'y': 460, 'delay': 4} # выбор первого
                ]

TAPSWAP_ACTIONS2 = [{'x': 485, 'y': 1389, 'delay': 4}, # открытие boost
                   {'x': 542, 'y': 691, 'delay': 2}, # full tank
                   {'x': 366, 'y': 1397, 'delay': 2}, # get it

]

ICEBERG_ACTIONS = [{'x': 90, 'y': 990, 'delay': 4}, # открытие чата
                   {'x': 175, 'y': 1347, 'delay': 15}, # открытие игры
                   {'x': 265, 'y': 1078, 'delay': 2}, # CLAIM
                   {'x': 265, 'y': 1078, 'delay': 2}, # CLAIM
                   {'x': 265, 'y': 1078, 'delay': 2}, # CLAIM
                   {'x': 265, 'y': 1078, 'delay': 2}, # CLAIM
                   {'x': 265, 'y': 1078, 'delay': 3}, # CLAIM
                   {'x': 667, 'y': 160, 'delay': 2}, # выход
                   {'x': 667, 'y': 160, 'delay': 2}, # выход
                   ]



for ip_address in ALL_IP_ADDRESSES:
    running_flags[ip_address] = threading.Event()
    pause_flags[ip_address] = threading.Event()
threadss = {}

barrier_group_1 = threading.Barrier(len(IP_ADDRESSES), timeout=1000)
barrier_group_2 = threading.Barrier(len(SWAP_ADDRESSES), timeout=1000)

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

                
def connect_device(ip_address):
    successful_ips = []
    skipped_ips = []
    failed_ips = []

    for ip in ip_address:
        print(f"\nTrying to connect to device with IP: {ip}")
        result_stdout, result_stderr = run_adb_command(['adb', 'connect', ip])
        if 'cannot' in result_stdout.lower() or 'not found' in result_stdout.lower():
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

    print(f"{len(successful_ips)}/{len(ip_address)} устройств подключены.")




def perform_tap_hot(ip_address, action, swipe_action):
    if not running_flags[ip_address].is_set():
        return False
    pause_flags[ip_address].wait()  # Wait for resume signal if paused

    command = f'adb -s {ip_address} shell input tap {action["x"]} {action["y"]}'
    result = subprocess.run(command, shell=True, check=False)  # Изменено check=True на check=False для отладки
    if result.returncode != 0:
        print(f"Command failed on {ip_address}: {command}")
        reconnect_device(ip_address)
        # Повторяем операцию после успешного переподключения
        subprocess.run(command, shell=True, check=True)
    time.sleep(action["delay"])
    return True


def perform_swipe_hot(ip_address, swipe):
    if not running_flags[ip_address].is_set():
        return False
    pause_flags[ip_address].wait()  # Wait for resume signal if paused

    command = f'adb -s {ip_address} shell input swipe {swipe["start_x"]} {swipe["start_y"]} {swipe["end_x"]} {swipe["end_y"]} {swipe["duration"]}'
    result = subprocess.run(command, shell=True, check=False)  # Изменено check=True на check=False для отладки
    if result.returncode != 0:
        print(f"Command failed on {ip_address}: {command}")
        reconnect_device(ip_address)
        # Повторяем операцию после успешного переподключения
        subprocess.run(command, shell=True, check=True)
    time.sleep(swipe["duration"] / 1000)
    return True


def perform_tap(ip_address, action):
    if not running_flags[ip_address].is_set():
        return False
    pause_flags[ip_address].wait()  # Wait for resume signal if paused

    command = f'adb -s {ip_address} shell input tap {action["x"]} {action["y"]}'
    result = subprocess.run(command, shell=True, check=False)  # Изменено check=True на check=False для отладки
    if result.returncode != 0:
        print(f"Command failed on {ip_address}: {command}")
        reconnect_device(ip_address)
        # Повторяем операцию после успешного переподключения
        subprocess.run(command, shell=True, check=True)
    time.sleep(action["delay"])
    return True


def perform_swipe(ip_address, swipe):
    if not running_flags[ip_address].is_set():
        return False
    pause_flags[ip_address].wait()  # Wait for resume signal if paused

    command = f'adb -s {ip_address} shell input swipe {swipe["start_x"]} {swipe["start_y"]} {swipe["end_x"]} {swipe["end_y"]} {swipe["duration"]}'
    result = subprocess.run(command, shell=True, check=False)  # Изменено check=True на check=False для отладки
    if result.returncode != 0:
        print(f"Command failed on {ip_address}: {command}")
        reconnect_device(ip_address)
        # Повторяем операцию после успешного переподключения
        subprocess.run(command, shell=True, check=True)
    time.sleep(swipe["duration"] / 1000)
    return True


def reconnect_device(ip):
    successful_ips = []
    skipped_ips = []
    failed_ips = []
    print(f"\nTrying to connect to device with IP: {ip}")
    result_stdout, result_stderr = run_adb_command(['adb', 'connect', ip])
    if 'cannot' in result_stdout.lower() or 'closed' in result_stdout.lower() or 'not' in result_stdout.lower():
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
            if 'cannot' not in result_stdout.lower() or 'closed' not in result_stdout.lower() or 'not' not in result_stdout.lower():
                successful_ips.append(failed_ip)
                failed_ips.remove(failed_ip)

    print(f"{len(successful_ips)} устройств переподключены.")

def execute_actions(ip_address, actions):
    for action in actions:
        if not perform_tap(ip_address, action):
            if not perform_tap(ip_address, action):
                pass
    return True

def execute_repeated_actions(ip_address, repeated_actions, repeats):
    for _ in range(repeats):
        for action in repeated_actions:
            if not perform_tap(ip_address, action):
                return False
    return True

def execute_swipes(ip_address, swipe_actions):
    for swipe in swipe_actions:
        if not perform_swipe(ip_address, swipe):
            if not perform_swipe(ip_address, swipe):
                pass
    return True



def tap_device(ip_address, actions, repeated_actions, repeats, exit_action, swipe_actions, meme_actions, blum_actions, vertus_actions, restart_actions, barrier, check=False):
    try:
        n = 0
        while running_flags[ip_address].is_set() and n <= 500:
            if check:
                if not execute_actions(ip_address, RESTART_ACTIONS):
                    execute_actions(ip_address, RESTART_ACTIONS)
                barrier.wait(timeout=120)

            # ЗАПУСК ХОМЯКОВ
            if not execute_actions(ip_address, actions):
                execute_actions(ip_address, actions)


            # ЛЮТЫЙ ФАРМ ХОМЯКОВ
            time.sleep(60)
            # ЗАПУСК MEME FI
            barrier.wait(timeout=120)

            # ДЕЙСТВИЯ ПОСЛЕ ФАРМА
            if not execute_actions(ip_address, exit_action):
                execute_actions(ip_address, exit_action)
            barrier.wait(timeout=120)
            # ВЫХОД ИЗ ХОМЯКОВ
            if not execute_swipes(ip_address, swipe_actions):
                execute_swipes(ip_address, swipe_actions)
            barrier.wait(timeout=120)

            if not execute_swipes(ip_address, BACKSWIPE_ACTION):
                execute_swipes(ip_address, BACKSWIPE_ACTION)
            barrier.wait(timeout=120)
            # Запуск MEME FI И ВЫХОД
            if not execute_actions(ip_address, meme_actions):
                execute_actions(ip_address, meme_actions)
            # ФАРМ MEME FI И ВЫХОД
            time.sleep(60)

            barrier.wait(timeout=120)

            if not execute_actions(ip_address, exit_action):
                execute_actions(ip_address, exit_action)
            barrier.wait(timeout=120)
            if not execute_swipes(ip_address, swipe_actions):
                execute_swipes(ip_address, swipe_actions)

            barrier.wait(timeout=120)
            if not execute_swipes(ip_address, BACKSWIPE_ACTION):
                execute_swipes(ip_address, BACKSWIPE_ACTION)
            barrier.wait(timeout=120)
            # BLUM
            if not execute_actions(ip_address, blum_actions):
                execute_actions(ip_address, blum_actions)

            barrier.wait(timeout=120)

            if not execute_actions(ip_address, new_blum_actions):
                execute_actions(ip_address, new_blum_actions)

            barrier.wait(timeout=120)

            # VERTUS
            if not execute_actions(ip_address, vertus_actions):
                execute_actions(ip_address, vertus_actions)
            barrier.wait(timeout=120)
            if not execute_swipes(ip_address, swipe_actions):
                execute_swipes(ip_address, swipe_actions)

            if not execute_swipes(ip_address, BACKSWIPE_ACTION):
                execute_swipes(ip_address, BACKSWIPE_ACTION)
            barrier.wait(timeout=120)
            # ICEBERG
            if not execute_actions(ip_address, ICEBERG_ACTIONS):
                execute_actions(ip_address, ICEBERG_ACTIONS)
            barrier.wait(timeout=120)
            if not execute_swipes(ip_address, swipe_actions):
                execute_swipes(ip_address, swipe_actions)

            barrier.wait(timeout=120)
            # перезаход в тг
            if not execute_swipes(ip_address, BACKSWIPE_ACTION):
                execute_swipes(ip_address, BACKSWIPE_ACTION)
            barrier.wait(timeout=120)
            if not execute_actions(ip_address, restart_actions):
                execute_actions(ip_address, restart_actions)

            barrier.wait(timeout=120)

            n += 1
        else:
            return

    except Exception as ecc:
        if 'time to restart' in str(ecc):
            return
        else:
            print(f"Ошибка обработки потока (mb barrier error){ip_address}: {ecc}")
            time.sleep(10)
            reconnect_device(ip_address)
            pass

#
# def mine_hot(ip_address, hot_actions, hot2, hot3, under_swipe, check=False):
#     while running_flags[ip_address].is_set():
#         try:
#             i = 0
#             while i <= 7:  # Wait for resume signal if paused
#                 if check:
#                     if not execute_actions(ip_address, RESTART_ACTIONS):
#                         return
#                     if not execute_actions(ip_address, hot_new_actions):
#                         return
#
#                 # ЗАПУСК
#                 if not execute_swipes(ip_address, under_swipe):
#                     return
#                 print(f"Near Wallet swiped down on {ip_address}")
#
#
#
#                 if not execute_actions(ip_address, hot_actions):
#                     return
#                 print(f"Near Wallet claimed hot on {ip_address}")
#
#
#
#
#                 if not execute_swipes(ip_address, under_swipe):
#                     return
#                 print(f"Near Wallet swiped down on {ip_address}")
#
#
#                 if not execute_actions(ip_address, hot2):
#                     return
#                 print(f"Near Wallet changed account on {ip_address}")
#
#                 hot2[-1]['y'] += 130
#
#                 i += 1
#             if not execute_actions(ip_address, hot3):
#                 return
#             print(f"Near Wallet changed to krigelmega on {ip_address}")
#
#
#             hot2[-1]['y'] = 710
#             time.sleep(600)
#
#         except Exception as evv:
#             print(f"Ошибка обработки потока HOT {ip_address}: {evv}")
#             time.sleep(10)
#             continue


def tap_swap(ip_address, swap_actions, swap_actions2, repeated_actions, second_akk_actions, third_akk_actions, tapswap_first_actions, exit_actions, swipe_actions, barrier, check=False):
    i = 0
    try:
        while running_flags[ip_address].is_set() and i <= 500:
            if check:
                if not execute_actions(ip_address, RESTART_ACTIONS):
                    execute_actions(ip_address, RESTART_ACTIONS)
                if not execute_actions(ip_address, tap_swap_actions_nice):
                    execute_actions(ip_address, tap_swap_actions_nice)
                barrier.wait(timeout=120)
            # запуск и действия до фарма
            if not execute_actions(ip_address, tapswap_first_actions):
                execute_actions(ip_address, tapswap_first_actions)
            barrier.wait(timeout=120)
            # выход из тг чата
            if not execute_swipes(ip_address, swipe_actions):
                execute_swipes(ip_address, swipe_actions)
            barrier.wait(timeout=120)
            # фарм
            # claim full tank
            if not execute_actions(ip_address, swap_actions2):
                execute_actions(ip_address, swap_actions2)
            barrier.wait(timeout=120)
            # EXIT
            if not execute_actions(ip_address, exit_actions):
                execute_actions(ip_address, exit_actions)
            time.sleep(2)
            barrier.wait(timeout=120)
            # swipes to change account
            if not execute_swipes(ip_address, swipe_actions):
                execute_swipes(ip_address, swipe_actions)
            barrier.wait(timeout=120)
            # X2
            if not execute_swipes(ip_address, swipe_actions):
                execute_swipes(ip_address, swipe_actions)
            barrier.wait(timeout=120)
            # переключение на второй акк
            if not execute_actions(ip_address, second_akk_actions):
                execute_actions(ip_address, second_akk_actions)
            barrier.wait(timeout=120)
            # 2 АКК НАЧАЛО ДЕЙСТВИЙ
            if not execute_actions(ip_address, tapswap_first_actions):
                execute_actions(ip_address, tapswap_first_actions)
            barrier.wait(timeout=120)
            # выход из тг чата
            if not execute_swipes(ip_address, swipe_actions):
                execute_swipes(ip_address, swipe_actions)
            barrier.wait(timeout=120)
            # claim full tank
            if not execute_actions(ip_address, swap_actions2):
                execute_actions(ip_address, swap_actions2)
            # continue farm
            barrier.wait(timeout=120)
            # EXIT
            if not execute_actions(ip_address, exit_actions):
                execute_actions(ip_address, exit_actions)
            time.sleep(2)
            barrier.wait(timeout=120)
            # swipes to change account
            if not execute_swipes(ip_address, swipe_actions):
                execute_swipes(ip_address, swipe_actions)
            barrier.wait(timeout=120)
            # X2
            if not execute_swipes(ip_address, swipe_actions):
                execute_swipes(ip_address, swipe_actions)
            barrier.wait(timeout=120)
            # переклюключение на третий аккаунт
            if not execute_actions(ip_address, third_akk_actions):
                execute_actions(ip_address, third_akk_actions)
            barrier.wait(timeout=120)
            # 3 АКК НАЧАЛО ДЕЙСТВИЙ
            if not execute_actions(ip_address, tapswap_first_actions):
                execute_actions(ip_address, tapswap_first_actions)
            barrier.wait(timeout=120)
            # выход из тг чата
            if not execute_swipes(ip_address, swipe_actions):
                execute_swipes(ip_address, swipe_actions)

            barrier.wait(timeout=120)
            # claim full tank
            if not execute_actions(ip_address, swap_actions2):
                execute_actions(ip_address, swap_actions2)
            # continue farm
            barrier.wait(timeout=120)
            # EXIT
            if not execute_actions(ip_address, exit_actions):
                execute_actions(ip_address, exit_actions)
            time.sleep(2)
            barrier.wait(timeout=120)
            # swipes to change account
            if not execute_swipes(ip_address, swipe_actions):
                execute_swipes(ip_address, swipe_actions)
            barrier.wait(timeout=120)
            # X2
            if not execute_swipes(ip_address, swipe_actions):
                execute_swipes(ip_address, swipe_actions)
            barrier.wait(timeout=120)
            # переключение обратно на 1 акк
            if not execute_actions(ip_address, first_akk_actions):
                execute_actions(ip_address, first_akk_actions)
            barrier.wait(timeout=120)
            if not execute_actions(ip_address, RESTART_ACTIONS):
                execute_actions(ip_address, RESTART_ACTIONS)
            barrier.wait(timeout=120)
            if not execute_actions(ip_address, tap_swap_actions_nice):
                execute_actions(ip_address, tap_swap_actions_nice)
            barrier.wait(timeout=120)

            i += 1
        else:
            return
    except Exception as ecc:
        if 'time to restart' in str(ecc):
            return
        else:
            print(f"Ошибка обработки потока tap swap (mb barrier error){ip_address}: {ecc}")
            time.sleep(10)
            reconnect_device(ip_address)

            pass



def run_bot_mainnn():
    while True:
        text_label.configure(text='Запущен сбор Hamster Kombat')
        subprocess.run(["C:\\Users\\FARMERMARK\\AppData\\Local\\Programs\\Python\\Python311\\python.exe", "C:\\hamster\\main.py"])
        text_label.configure(text='Сбор Hamster Kombat завершен')
        time.sleep(300)

def run_bot_mainis():
    time.sleep(5)
    while True:
        text_label.configure(text='Запущен сбор MemeFI')
        subprocess.run(["C:\\Users\\FARMERMARK\\AppData\\Local\\Programs\\Python\\Python311\\python.exe", "C:\\memefi\\main.py"])
        text_label.configure(text='Сбор MemeFI завершен')
        time.sleep(600)

def run_yescoin():
    time.sleep(10)
    while True:
        text_label.configure(text='Запущен сбор YesCoin')
        subprocess.run(["C:\\Users\\FARMERMARK\\AppData\\Local\\Programs\\Python\\Python311\\python.exe", "C:\\yescoin\\main.py"])
        text_label.configure(text='Сбор YesCoin завершен')
        time.sleep(660)

def run_pocketfi():
    time.sleep(15)
    while True:
        text_label.configure(text='Запущен сбор PocketFI')
        subprocess.run(["C:\\Users\\FARMERMARK\\AppData\\Local\\Programs\\Python\\Python311\\python.exe", "C:\\pocketfi\\main.py"])
        text_label.configure(text='Сбор PocketFI завершен')
        time.sleep(540)

def run_blum():
    text_label.configure(text='Запущен сбор BLUM')
    subprocess.run(["C:\\Users\\FARMERMARK\\AppData\\Local\\Programs\\Python\\Python311\\python.exe", "C:\\blum\\blum.py"])
    text_label.configure(text='Сбор BLUM завершен')

def run_tg_bot():
    subprocess.run(["C:\\Users\\admin\\AppData\\Local\\Programs\\Python\\Python311\\python.exe", "C:\\fermabot\\bot.py"])


def start_all(check=False):
    # Запуск потоков для bot.mainnn и main.mainis
    if not check:
        threading.Thread(target=run_tg_bot, daemon=True).start()
    # threading.Thread(target=run_bot_mainnn, daemon=True).start()
    # threading.Thread(target=run_bot_mainis, daemon=True).start()
    #     threading.Thread(target=run_blum, daemon=True).start()
    # threading.Thread(target=run_yescoin, daemon=True).start()
    # threading.Thread(target=run_pocketfi, daemon=True).start()



    # Запуск циклов для IP_ADDRESSES и SWAP_ADDRESSES
    global threads
    threads = []

    for ip_address in IP_ADDRESSES:
        running_flags[ip_address].set()
        pause_flags[ip_address].set()
        thread = threading.Thread(target=tap_device, args=(
            ip_address, ACTIONS, REPEATED_ACTIONS, REPEATS, EXIT_ACTION, SWIPE_ACTION, MEME_ACTIONS, BLUM_ACTIONS,
            VERTUS_ACTIONS, RESTART_ACTIONS, barrier_group_1))
        threads.append(thread)
        thread.start()

    for ip_address in SWAP_ADDRESSES:
        running_flags[ip_address].set()
        pause_flags[ip_address].set()
        thread = threading.Thread(target=tap_swap, args=(
            ip_address, TAPSWAP_ACTIONS, TAPSWAP_ACTIONS2, REPEATED_ACTIONS, SECOND_AKK_actions, THIRD_AKK_actions,
            TAPSWAP_FIRST_ACTIONS, EXIT_ACTION, SWIPE_ACTION, barrier_group_2))
        threads.append(thread)
        thread.start()


    text_label.configure(text='Все устройства запущены')



def stop_all():
    for ip in ALL_IP_ADDRESSES:
        running_flags[ip].clear()
    print("All actions stopped.")
    text_label.configure(text='Все устройства отключены')

def display_text():
    text = get_text()
    text_label.configure(text=text)

def display_text2():
    w = root.winfo_screenwidth()
    h = root.winfo_screenheight()
    w = w // 2  # середина экрана
    h = h // 2
    w = w - 200  # смещение от середины
    h = h - 200
    def switch_to_main_interface():
        text_label.configure(text='Устройства подключены')
        print("Ожидание завершено. Устройства подключены.") # Создаем основной интерфейс


    # Запуск функции connect_device в отдельном потоке
    def run_connection():
        connect_device(ALL_IP_ADDRESSES)
        root.after(100, switch_to_main_interface)
        # Переключаем интерфейс после завершения подключения


    threading.Thread(target=run_connection).start()

    root.mainloop()

    text = 'Устройства подключены'
    text_label.configure(text=text)



def display_text3():
    text = threading.Thread(target=mainmain).start()
    text_label.configure(text=text)

def display_text4():
    text = maain()
    text_label.configure(text=text)

def create_button_actions(ip, button):
    def pause_action():
        button.configure(fg_color='orange')
        if ip not in pause_flags:
            return
        pause_flags[ip].clear()

    def resume_action():
        button.configure(fg_color='blue')
        if ip not in pause_flags:
            return
        pause_flags[ip].set()

    def restart_action():
        threads = []
        button.configure(fg_color='blue')
        running_flags[ip].clear()
        threadss[ip].join()

        running_flags[ip].set()
        pause_flags[ip].set()


        if ip == '192.168.0.132' or ip == '192.168.0.75' or ip == '192.168.0.115' or ip == '192.168.0.99' or ip == '192.168.0.79':
            thread = threading.Thread(target=tap_swap, args=(ip, TAPSWAP_ACTIONS, TAPSWAP_ACTIONS2, REPEATED_ACTIONS, SECOND_AKK_actions, THIRD_AKK_actions, TAPSWAP_FIRST_ACTIONS, EXIT_ACTION, SWIPE_ACTION, barrier_group_2, True))
        else:
            thread = threading.Thread(target=tap_device, args=(ip, ACTIONS, REPEATED_ACTIONS, REPEATS, EXIT_ACTION, SWIPE_ACTION, MEME_ACTIONS, BLUM_ACTIONS, VERTUS_ACTIONS, RESTART_ACTIONS, barrier_group_1, True))
        threadss[ip_address] = thread
        threads.append(thread)
        thread.start()

        print(f"Restarting actions for {ip}")

    return pause_action, resume_action, restart_action

def create_button_actions2(ips, button):
    def pause_allaction():
        button.configure(fg_color='orange')
        for ip in ALL_IP_ADDRESSES:
            pause_flags[ip].clear()
        text_label.configure(text='Устройства приостановлены')

    def resume_allaction():
        button.configure(fg_color='blue')
        for ip in ALL_IP_ADDRESSES:
            pause_flags[ip].set()
        text_label.configure(text='Устройства продолжили работу')
    return pause_allaction, resume_allaction

class TextRedirector(object):
    def __init__(self, widget, tag="stdout"):
        self.widget = widget
        self.tag = tag

    def write(self, str):
        self.widget.configure(state='normal')
        self.widget.insert("end", str, (self.tag,))
        self.widget.configure(state='disabled')
        self.widget.see("end")

    def flush(self):
        pass

class InputRedirector(object):
    def __init__(self, widget):
        self.widget = widget
        self.input_queue = queue.Queue()

    def write(self, str):
        self.input_queue.put(str)

    def readline(self):
        self.widget.configure(state='normal')
        self.widget.insert("end", "\n> ", ("stdin",))
        self.widget.configure(state='disabled')
        self.widget.see("end")
        return self.input_queue.get()

    def clear_input(self):
        self.widget.configure(state='normal')
        self.widget.delete('input_start', 'end')
        self.widget.configure(state='disabled')

def on_enter(event):
    input_text = log_text.get("input_start", 'end-1c')
    log_text.mark_set("insert", "input_start")
    log_text.insert("insert", '\n', "stdin")
    input_redirector.write(input_text)
    log_text.mark_set("input_start", "end-1c linestart")
    log_text.delete("input_start", "end-1c")
    log_text.mark_gravity("input_start", tk.LEFT)
    return 'break'


class TextHandler(logging.Handler):
    def __init__(self, widget):
        super().__init__()
        self.widget = widget

    def emit(self, record):
        msg = self.format(record)
        self.widget.configure(state='normal')
        self.widget.insert("end", msg + '\n')
        self.widget.configure(state='disabled')
        self.widget.see("end")


def create_main_interface():
    global text_label, log_text  # Добавить log_text



    customtkinter.set_appearance_mode('dark')
    customtkinter.set_default_color_theme('dark-blue')

    num_rows = min(9, len(ALL_IP_ADDRESSES))  # Максимум 9 строк
    num_columns = (len(ALL_IP_ADDRESSES) + num_rows - 1) // num_rows  # Вычисляем количество столбцов

    for i in range(num_rows):
        frame = customtkinter.CTkFrame(root)
        frame.pack(anchor='w', padx=10, pady=10)  # anchor='w' для выравнивания по левому краю

        for j in range(num_columns):
            index = i + j * num_rows
            if index >= len(ALL_IP_ADDRESSES):
                break

            ips = ALL_IP_ADDRESSES[index]
            label = customtkinter.CTkLabel(frame, text=ips)
            label.pack(side='left', padx=10)  # side='left' для выравнивания по левому краю

            pause_button = customtkinter.CTkButton(frame, text="Pause")
            resume_button = customtkinter.CTkButton(frame, text="Resume")
            restart_button = customtkinter.CTkButton(frame, text="Restart")

            pause_action, resume_action, restart_action = create_button_actions(ips, pause_button)

            pause_button.configure(command=pause_action)
            pause_button.pack(side='left', padx=10)  # side='left' для выравнивания по левому краю

            resume_button.configure(command=resume_action)
            resume_button.pack(side='left', padx=10)  # side='left' для выравнивания по левому краю

            restart_button.configure(command=restart_action)
            restart_button.pack(side='left', padx=10)

    w = root.winfo_screenwidth()
    h = root.winfo_screenheight()
    w = w // 2  # середина экрана
    h = h // 2
    w = w - 200  # смещение от середины
    h = h - 200
    root.geometry(f'1771x896+{w}+{h}')

    bottom_frame = customtkinter.CTkFrame(root)
    bottom_frame.pack(pady=20)

    start_all_button = customtkinter.CTkButton(bottom_frame, text="Запустить все", command=start_all)
    start_all_button.pack(side='left', padx=10)  # side='left' для выравнивания по левому краю

    stop_all_button = customtkinter.CTkButton(bottom_frame, text="Прервать все", command=stop_all)
    stop_all_button.pack(side='left', padx=10)  # side='left' для выравнивания по левому краю

    stop_all_button1 = customtkinter.CTkButton(bottom_frame, text="Приостановить все")
    stop_all_button1.pack(side='left', padx=10)  # side='left' для выравнивания по левому краю

    stop_all_button2 = customtkinter.CTkButton(bottom_frame, text="Возобновить все")
    stop_all_button2.pack(side='left', padx=10)  # side='left' для выравнивания по левому краю

    create_pause_all_action, create_resume_all_action = create_button_actions2(ALL_IP_ADDRESSES, stop_all_button1)

    stop_all_button1.configure(command=create_pause_all_action)
    stop_all_button2.configure(command=create_resume_all_action)

    additional_button_1 = customtkinter.CTkButton(bottom_frame, text="Подключение устройств", command=display_text2)
    additional_button_1.pack(side='left', padx=10)  # side='left' для выравнивания по левому краю

    additional_button_2 = customtkinter.CTkButton(bottom_frame, text="Перезапуск Telegram", command=display_text)
    additional_button_2.pack(side='left', padx=10)  # side='left' для выравнивания по левому краю

    additional_button_3 = customtkinter.CTkButton(bottom_frame, text="PhoneCast", command=display_text3)
    additional_button_3.pack(side='left', padx=10)  # side='left' для выравнивания по левому краю

    additional_button_4 = customtkinter.CTkButton(bottom_frame, text="PhoneCast (one)", command=display_text4)
    additional_button_4.pack(side='left', padx=10)  # side='left' для выравнивания по левому краю

    # Пустой виджет для создания пространства между кнопками
    new_row_frame = customtkinter.CTkFrame(root)
    new_row_frame.pack(side='left', pady=20)

    additional_button_5 = customtkinter.CTkButton(new_row_frame, text="Hamster Kombat", command=additional_function)
    additional_button_5.pack(side='left', padx=10)  # side='left' для выравнивания по лев

    text_label = customtkinter.CTkLabel(root, text="")
    text_label.pack(pady=10)

    display_text()
    print('Telegram был перезагружен')
    time.sleep(2)
    display_text()
    print('Telegram был перезагружен')
    start_all(check=False)
    # # Область для вывода лога
    # log_text = scrolledtext.ScrolledText(root, state='disabled', wrap='word', height=10, bg='#2b2b2b', fg='white')
    # log_text.pack(fill='both', expand=True, padx=10, pady=10)
    # sys.stdout = TextRedirector(log_text)
    # input_redirector = InputRedirector(log_text)
    # sys.stdin = input_redirector
    #
    # log_text.bind("<Return>", on_enter)
    # log_text.mark_set("input_start", "end-1c")
    # log_text.mark_gravity("input_start", tk.LEFT)
    #
    # # Настройка логирования
    # log_handler = TextHandler(log_text)
    # log_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    # logging.getLogger().addHandler(log_handler)
    # logging.getLogger().setLevel(logging.INFO)



def additional_function():
    def run_bot_main():
        text_label.configure(text='Запущена авто прокачка Hamster Kombat')
        bot.main()
        text_label.configure(text='Автопрокачка завершила свою работу')
    threading.Thread(target=run_bot_main).start()
def create_gui():
    global root, log_text, input_redirector
    customtkinter.set_appearance_mode("dark")  # Устанавливаем темный режим
    customtkinter.set_default_color_theme("blue")
    root = customtkinter.CTk()
    root.title("TRADE AUTO FARM 2.0")
    root.iconbitmap('appicon.ico')

    # Начальный экран с белым фоном и надписью "Ожидайте, устройства подключаются"
    initial_frame = customtkinter.CTkFrame(root)
    initial_frame.pack(fill='both', expand=True)

    initial_label = customtkinter.CTkLabel(initial_frame, text="Ожидайте, устройства подключаются...",
                                           font=("Helvetica", 16))
    initial_label.pack()

    log_text = scrolledtext.ScrolledText(initial_frame, state='normal', wrap='word', height=10, bg='#2b2b2b',
                                         fg='white')
    log_text.pack(fill='both', expand=True)
    log_text.tag_configure("stdin", foreground="cyan")

    sys.stdout = TextRedirector(log_text)
    input_redirector = InputRedirector(log_text)
    sys.stdin = input_redirector

    log_text.bind("<Return>", on_enter)
    log_text.mark_set("input_start", "end-1c")
    log_text.mark_gravity("input_start", tk.LEFT)

    def switch_to_main_interface():
        initial_frame.pack_forget()  # Удаляем начальный экран
        print("Ожидание завершено. Устройства подключены.")
        create_main_interface()  # Создаем основной интерфейс

    # Запуск функции connect_device в отдельном потоке
    def run_connection():
        connect_device(ALL_IP_ADDRESSES)
        root.after(100, switch_to_main_interface)  # Переключаем интерфейс после завершения подключения

    threading.Thread(target=run_connection).start()

    root.mainloop()

if __name__ == "__main__":
    end_time = time.time() + 30
    create_gui()