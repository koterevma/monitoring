import sqlite3
from pathlib import Path

working_directory = Path(__file__).parent.parent


def sensors(device_name, device_serial):
    conn = sqlite3.connect(working_directory / "mon.db")
    cur = conn.cursor()
    cur.execute("SELECT sensors.name FROM sensors LEFT JOIN devices ON devices.deviceid=sensors.deviceid WHERE devices.uname=? AND devices.serial=?", (device_name, device_serial))
    return cur.fetchall()


def sensors_with_units(device_name, device_serial):
    conn = sqlite3.connect(working_directory / "mon.db")
    cur = conn.cursor()
    cur.execute("SELECT sensors.name, sensors.units FROM sensors LEFT JOIN devices ON devices.deviceid=sensors.deviceid WHERE devices.uname=? AND devices.serial=?", (device_name, device_serial))
    return cur.fetchall()


def units(sensor_name):
    conn = sqlite3.connect(working_directory / "mon.db")
    cur = conn.cursor()
    cur.execute("SELECT sensors.units FROM sensors WHERE sensors.name=?", (sensor_name,))
    return cur.fetchone()


def devices():
    conn = sqlite3.connect(working_directory / "mon.db")
    cur = conn.cursor()
    cur.execute("SELECT uname, serial FROM devices")
    return cur.fetchall()


if __name__ == '__main__':  # Пример работы
    f = devices()[2]
    print(str(f))
    print(sensors(*f))  # Разыменование f, берем названия датчиков для прибора полученного 
    print()
    print("Sensors and units for device {}, serial {}".format(*f))
    print(*sensors_with_units(*f), sep='\n')
    print()
    print("Units for BMP280_temp")
    print(units("BMP280_temp"))
