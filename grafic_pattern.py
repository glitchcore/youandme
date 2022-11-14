from time import sleep, time
import random
from math import *

from grafic_emulate import draw_scene

TIME_BASE = 0.1
time_for_seance = 10 * 60 * TIME_BASE
time_befor_next_lighting = 5 * 60 *TIME_BASE


def make_format(value, min_val=1, max_val=31):
    """
    типа договорились, что макс и мин - на 1 меньше степени двойки
    TODO: нужно будет переделать нормально
    """
    return (value & max_val) + min_val


def me_random(number):
    # 13 ^ 7 ^ 3
    result = number
    for _ in range(4):
        increment = ((result >> 3) & 1) ^ ((result >> 7) & 1) ^ ((result >> 13) & 1)
        result = (result << 1) + increment
    return result & 32767


def get_delay(key, prev_delay):
    new_delay = me_random(key + prev_delay)
    return new_delay


def get_leds(key, prev_led_value):
    new_leds = [
        me_random(led + key) for led in prev_led_value
    ]
    return new_leds


def next_seance_init():
    """
    TODO: планирую тут написать мега-логику по рассчёту параметров следующего сеанса

    1 - номара диодов, которые будут задействованы
    2 - время до следующего мигания (time_befor_next_lighting)
    3 - ...


    возможно, нужно будет что-то вынести в глобальные переменные (delsy, e.t.c)
    """
    pass


if __name__ == "__main__":
    # от 0 до 120
    led_value = [120, 40, 20, 30, 70, 65]
    KEY = random.randint(0, 65536)
    time_start = time()
    delay = 0

    while time() - time_start < time_for_seance:
        led_value = get_leds(KEY, led_value)
        real_led_value = [make_format(led, 0, 127) for led in led_value]
        print(real_led_value)
        delay = get_delay(KEY, delay)
        draw_scene(real_led_value)
        real_delay = make_format(delay, min_val=1, max_val=31)
        sleep(TIME_BASE * real_delay)

    next_seance_init(KEY)
