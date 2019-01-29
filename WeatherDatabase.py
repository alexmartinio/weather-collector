import pymysql.cursors


class WeatherDatabase:
    database_name = 'weather'

    def __init__(self):
        self.__setup_database()

    @staticmethod
    def __connect():
        connection = pymysql.connect(host='localhost',
                                     user='weather',
                                     password='weather',
                                     db='mysql',
                                     charset='utf8mb4',
                                     cursorclass=pymysql.cursors.DictCursor)
        return connection

    @staticmethod
    def __setup_database():

        connection = WeatherDatabase.__connect()
        database_name = WeatherDatabase.database_name
        try:
            with connection.cursor() as check_cursor:
                sql = 'SELECT SCHEMA_NAME FROM information_schema.SCHEMATA WHERE SCHEMA_NAME = "{}"'.format(
                    database_name)
                check_cursor.execute(sql)
                result = check_cursor.fetchone()

                if not result:
                    with connection.cursor() as cursor:
                        # Create database
                        sql = 'CREATE OR REPLACE DATABASE {}'.format(database_name)
                        cursor.execute(sql)
                        connection.select_db(database_name)
                        sql = 'SELECT DATABASE();'
                        cursor.execute(sql)
                        result = cursor.fetchone()
                        print('Selected database: {}'.format(result["DATABASE()"]))

                    with connection.cursor() as cursor:
                        # Create table
                        sql = (
                            'CREATE TABLE `weather_data` ('
                            '   `id` int(11) NOT NULL AUTO_INCREMENT,   '
                            '   `timestamp` TIMESTAMP NOT NULL,         '
                            '   `ambient_temperature` FLOAT,            '
                            '   `ground_temperature` FLOAT,             '
                            '   `humidity` FLOAT,                       '
                            '   `pressure` FLOAT,                       '
                            '   `rainfall` FLOAT,                       '
                            '   `wind_speed` FLOAT,                     '
                            '   `wind_gust` FLOAT,                      '
                            '   `wind_direction` FLOAT,                 '
                            '   `air_quality` FLOAT,                    '
                            '   `gas_resistance` FLOAT,                 '
                            '   PRIMARY KEY (`id`)                      '
                            ')                                          '
                        )
                        cursor.execute(sql)
        finally:
            connection.close()

    def insert(self, ambient_temperature, ground_temperature: object, humidity, pressure, rainfall, wind_speed: object,
               wind_gust: object, wind_direction: object, air_quality, gas_resistance) -> object:
        # self.__setup_database()
        connection = self.__connect()
        database_name = self.database_name
        try:
            with connection.cursor() as cursor:
                # Create table
                sql = (
                    'INSERT INTO {}.`weather_data` (                                          '
                    '   `ambient_temperature`, `ground_temperature`, `humidity`, `pressure`, `rainfall`, `wind_speed`, `wind_gust`, `wind_direction`, `air_quality`, `gas_resistance` )   '
                    '   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)                                               '
                    ''.format(database_name)
                )
                cursor.execute(sql, (
                    ambient_temperature, ground_temperature, humidity, pressure, rainfall, wind_speed, wind_gust,
                    wind_direction, air_quality, gas_resistance))
                connection.commit()
        finally:
            connection.close()
        return

    def get_last_result(self):
        connection = self.__connect()
        database_name = self.database_name
        try:
            with connection.cursor() as cursor:
                # Create table
                sql = (
                    'SELECT * FROM {}.`weather_data` ORDER BY id DESC'.format(database_name)
                )
                cursor.execute(sql)
                result = cursor.fetchone()
                print(result)
        finally:
            connection.close()

    def get_db_version(self):
        connection = self.__connect()
        try:
            with connection.cursor() as cursor:
                sql = 'SELECT VERSION();'
                cursor.execute(sql)
                result = cursor.fetchone()
                version = result["VERSION()"]
                print('Version: {}'.format(version))
        finally:
            connection.close()
