import os
import socket
import requests
from scapy.all import ARP, Ether, srp
from bs4 import BeautifulSoup

# Функция для получения локального IP-адреса
def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(0)
    try:
        s.connect(('10.254.254.254', 1))
        local_ip = s.getsockname()[0]
    except Exception:
        local_ip = '127.0.0.1'
    finally:
        s.close()
    return local_ip


# Функция для получения информации о MAC-адресе с macvendors.com
def get_device_info(mac):
    """Получение информации о MAC-адресе с macvendors.com"""
    url = f"https://api.macvendors.com/{mac}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            return response.text  # Возвращаем информацию о производителе
        else:
            return "Ошибка при запросе к сайту"
    except requests.exceptions.RequestException as e:
        return f"Ошибка запроса: {e}"


# Функция для сканирования сети
def scan_network(target_ip):
    """Сканирование сети для получения списка устройств"""
    # Формирование запроса ARP для сканирования сети
    arp_request = ARP(pdst=target_ip)
    broadcast = Ether(dst="ff:ff:ff:ff:ff:ff")
    arp_request_broadcast = broadcast/arp_request
    answered_list = srp(arp_request_broadcast, timeout=1, verbose=False)[0]

    devices = []
    for element in answered_list:
        device_info = {
            'IP': element[1].psrc,
            'MAC': element[1].hwsrc
        }
        devices.append(device_info)
    return devices

# Функция для вывода списка устройств в виде таблицы
def print_devices(devices):
    """Вывод списка устройств в виде таблицы"""
    print("+---------------+-------------------+-----------------------------+")
    print("|    IP-адрес   |     MAC-адрес     |     Производитель/Модель    |")
    print("+---------------+-------------------+-----------------------------+")
    for device in devices:
        mac = device['MAC']
        info = get_device_info(mac)  # Получаем информацию о MAC-адресе
        print(f"| {device['IP']: <15} | {mac: <17} | {info: <27} |")
    print("+---------------+-------------------+-----------------------------+")

# Основная логика программы
def main():
    local_ip = get_local_ip()
    print(f"Ваш локальный IP: {local_ip}")
    while True:
        print("\nМеню:")
        print("1. Сканировать сеть")
        print("5. Информация о MAC-адресе")
        print("6. Выход")
        choice = input("Выберите действие: ")

        if choice == "1":
            # Сканируем сеть, предполагаем, что сетевая маска 255.255.255.0
            target_ip = local_ip.rsplit('.', 1)[0] + ".1/24"
            print("\nСканирование сети...")
            devices = scan_network(target_ip)
            print_devices(devices)

        elif choice == "5":
            mac_address = input("\nВведите MAC-адрес для получения информации: ")
            device_info = get_device_info(mac_address)
            print(f"Информация по MAC-адресу {mac_address}: {device_info}")

        elif choice == "6":
            print("Выход из программы.")
            break

        else:
            print("Неверный выбор. Попробуйте снова.")

if __name__ == "__main__":
    main()
