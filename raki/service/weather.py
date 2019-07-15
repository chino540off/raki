import argparse
import collections
import datetime
import pyowm
import time
import sqlite3

from pytz import reference


# Temperature coneversion constants
KELVIN_OFFSET = 273.15
FAHRENHEIT_OFFSET = 32.0
FAHRENHEIT_DEGREE_SCALE = 1.8


def kelvin_to_celsius(kelvintemp):
    """
    Converts a numeric temperature from Kelvin degrees to Celsius degrees
    :param kelvintemp: the Kelvin temperature
    :type kelvintemp: int/long/float
    :returns: the float Celsius temperature
    :raises: *TypeError* when bad argument types are provided
    """
    if kelvintemp < 0:
        raise ValueError(__name__ + \
                         ": negative temperature values not allowed")
    celsiustemp = kelvintemp - KELVIN_OFFSET
    return float("{0:.2f}".format(celsiustemp))


def kelvin_to_fahrenheit(kelvintemp):
    """
    Converts a numeric temperature from Kelvin degrees to Fahrenheit degrees
    :param kelvintemp: the Kelvin temperature
    :type kelvintemp: int/long/float
    :returns: the float Fahrenheit temperature
    :raises: *TypeError* when bad argument types are provided
    """
    if kelvintemp < 0:
        raise ValueError(__name__ + \
                         ": negative temperature values not allowed")
    fahrenheittemp = (kelvintemp - KELVIN_OFFSET) * \
        FAHRENHEIT_DEGREE_SCALE + FAHRENHEIT_OFFSET
    return float("{0:.2f}".format(fahrenheittemp))


Observation = collections.namedtuple('Observation', [
    'ts',
    'status',
    'sunrise',
    'sunset',
    'temp',
    'clouds',
    'humidity',
    'pressure',
    'rain_3h',
])


def make_observation(data):
    return Observation(
        ts=data.get_reference_time('date').astimezone(),
        status=data.get_detailed_status(),
        sunrise=data.get_sunrise_time('date').astimezone(),
        sunset=data.get_sunset_time('date').astimezone(),
        temp=data.get_temperature().get('temp'),
        clouds=data.get_clouds(),
        humidity=data.get_humidity(),
        pressure=data.get_pressure().get('press'),
        rain_3h=data.get_rain().get('3h', 0),
    )


class Backend:
    pass


class OpenWeatherMap(Backend):
    def __init__(self, **kwargs):
        self._owm = pyowm.OWM(kwargs.get('api_key'))
        self._place = kwargs.get('place')

    def get_observation(self):
        observation = self._owm.weather_at_place(self._place)
        w = observation.get_weather()
        return make_observation(w)

    def get_forecast(self):
        forecaster = self._owm.three_hours_forecast(self._place)
        return [
            make_observation(observation)
            for observation in forecaster.get_forecast()
        ]


class ORM:
    pass


class Sqlite(ORM):
    def __init__(self, **kwargs):
        self._conn = sqlite3.connect(kwargs.get('file', ':memory:'))
        self._c = self._conn.cursor()

        try:
            self._create_observation_table()
        except Exception as exce:
            print(exce)
            pass

    def _create_observation_table(self):
        self._c.execute('''CREATE TABLE observations (
            ts date,
            status text,
            sunrise date,
            sunset date,
            temp real,
            clouds integer,
            humidity integer,
            pressure integer,
            rain_3h real
        )''')

    def insert_observation(self, observation):
        print(observation)
        self._c.execute('''INSERT
                INTO observations
                VALUES (?,?,?,?,?,?,?,?,?)
        ''', observation)
        self._conn.commit()

    def dump_observations(self):
        recs = self._c.execute('SELECT * FROM observations')
        for row in recs:
            print(Observation(*row))


def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest='command')

    crawl_parser = subparsers.add_parser('crawl')
    crawl_parser.add_argument("--db",  type=str)
    crawl_parser.add_argument("--key", type=str)
    crawl_parser.add_argument("place", type=str)

    dump_parser = subparsers.add_parser('dump')
    dump_parser.add_argument("--db",  type=str)

    forecast_parser = subparsers.add_parser('forecast')
    forecast_parser.add_argument("--key", type=str)
    forecast_parser.add_argument("place", type=str)

    args = parser.parse_args()

    if args.command == 'crawl':
        weather = OpenWeatherMap(
            api_key=args.key,
            place=args.place
        )

        orm = Sqlite(file=args.db)
        while True:
            observation = weather.get_observation()
            orm.insert_observation(observation)
            time.sleep(60*60*3)

    elif args.command == 'dump':
        orm = Sqlite(file=args.db)
        orm.dump_observations()

    elif args.command == 'forecast':
        weather = OpenWeatherMap(
            api_key=args.key,
            place=args.place
        )

        for observation in weather.get_forecast():
            print(observation)


if __name__ == "__main__":
    main()
