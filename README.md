# Network Scanner

## Описание

Эта программа позволяет сканировать локальную сеть, выводить список подключенных устройств с их IP- и MAC-адресами, а также получать информацию о производителе устройства по его MAC-адресу, используя API macvendors.com.

## Установка

Перед началом работы убедитесь, что у вас установлен Python версии 3.10 или выше.

### Установка зависимостей

Для работы программы требуется установить следующие библиотеки:

```bash
pip install requests scapy beautifulsoup4
```

## Использование

Запустите скрипт командой:

```bash
python main.py
```

### Меню программы
После запуска программы вам будет предложено выбрать действие из меню:

1. **Сканировать сеть**: Выполняет сканирование локальной сети и выводит таблицу с информацией об устройствах.
2. **Информация о MAC-адресе**: Позволяет получить производителя устройства, указав его MAC-адрес.
3. **Выход**: Завершает работу программы.

## Примечания по коду

### 1. Получение локального IP-адреса
Функция `get_local_ip` определяет локальный IP-адрес устройства, чтобы использовать его в процессе сканирования сети.

```python
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
```

### 2. Сканирование сети
Функция `scan_network` использует Scapy для выполнения ARP-запросов и получения списка устройств в указанной подсети.

```python
def scan_network(target_ip):
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
```

### 3. Получение информации о MAC-адресе
Функция `get_device_info` выполняет HTTP-запрос к API macvendors.com, чтобы получить информацию о производителе устройства.

```python
def get_device_info(mac):
    url = f"https://api.macvendors.com/{mac}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            return response.text
        else:
            return "Ошибка при запросе к сайту"
    except requests.exceptions.RequestException as e:
        return f"Ошибка запроса: {e}"
```

### 4. Вывод данных в таблице
Функция `print_devices` форматирует вывод информации об устройствах в удобной для чтения таблице.

```python
def print_devices(devices):
    print("+---------------+-------------------+-----------------------------+")
    print("|    IP-адрес   |     MAC-адрес     |     Производитель/Модель    |")
    print("+---------------+-------------------+-----------------------------+")
    for device in devices:
        mac = device['MAC']
        info = get_device_info(mac)
        print(f"| {device['IP']: <15} | {mac: <17} | {info: <27} |")
    print("+---------------+-------------------+-----------------------------+")
```
