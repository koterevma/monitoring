from pathlib import Path
import sqlite3
import requests
import json

working_directory = Path(__file__).parent


def get_sensors(serial, uname):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 '
                      'Safari/537.36', }
    # serial, uname = serial_uname.split()
    url = 'http://webrobo.mgul.ac.ru:3000/db_api_REST/not_calibr/last_measurement/'
    url += uname + '/' + serial + '/'
    # print(url)
    try:
        f = requests.get(url, headers=headers)
    except requests.exceptions.RequestException as e:
        print(e)
        return None
    else:
        data = json.loads(f.text)
        sens_list = []
        for r in data:
            for s in data[r]['data']:
                try:
                    float(data[r]['data'][s])
                except ValueError:
                    pass
                else:
                    sens_list.append(s)

    return sens_list


def main():
    conn = sqlite3.connect("mon.db")
    cur = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS devices(
        deviceid INT PRIMARY KEY,
        serial TEXT,
        uname TEXT);
    """)
    conn.commit()
    devices = [
        ( 1,  "01",      "РОСА%20К-2" ),
        ( 2,  "01",      "Роса-К-1" ),
        ( 3,  "schHome", "Тест%20Студии" ),
        ( 4,  "schHome", "Тест%20воздуха" ),
        ( 5,  "01",      "Hydra-L" ),
        ( 6,  "02",      "Hydra-L" ),
        ( 7,  "03",      "Hydra-L" ),
        ( 8,  "04",      "Hydra-L" ),
        ( 9,  "05",      "Hydra-L" ),
        ( 10, "06",      "Hydra-L" ),
        ( 11, "07",      "Hydra-L" ),
        ( 12, "08",      "Hydra-L" ),
        ( 13, "01",      "Сервер%20СЕВ" ),
        ( 14, "02",      "Сервер%20СЕВ" ),
        ( 15, "03",      "Сервер%20СЕВ" ),
        ( 16, "01",      "КЛОП_МН" ),
        ( 17, "02",      "КЛОП_МН" ),
        ( 18, "03",      "КЛОП_МН" ),
        ( 18, "04",      "КЛОП_МН" )
    ]
    # cur.executemany("INSERT INTO devices VALUES(?, ?, ?);", devices)
    # conn.commit()
    # cur.execute("SELECT * FROM devices;")
    # devs = cur.fetchall()

    # n = 1
    # cur.execute("DROP TABLE sensors")

    cur.execute("""CREATE TABLE IF NOT EXISTS sensors(
        sensorid INT PRIMARY KEY,
        deviceid INT,
        name TEXT,
        units TEXT
    );
    """)

    
    # for id, serial, uname in devs:
    #     sens_list = get_sensors(serial, uname)
    #     for s in sens_list:
    #         cur.execute("INSERT INTO sensors VALUES(?, ?, ?, ?)", (n, id, s, "UNKNOWN"))
    #         n += 1
        
    # conn.commit()
    # cur.execute("SELECT devices.uname, sensors.name FROM sensors LEFT JOIN devices ON devices.deviceid=sensors.deviceid WHERE devices.uname='Hydra-L'")
    # cur.execute("SELECT devices.uname, sensors.name FROM sensors LEFT JOIN devices ON devices.deviceid=sensors.deviceid")
    cur.execute("UPDATE sensors SET units='lux' WHERE name='BH1750_lux'")
    conn.commit()
    cur.execute("SELECT * FROM sensors")
    rez = cur.fetchall()
    print(*rez, sep='\n')
    # print(rez)


if __name__ == '__main__':
    main()
