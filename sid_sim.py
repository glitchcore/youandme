from time import sleep
from random import random
import threading

pin_pulls = [False, False]

# чтение пина
def read_pin():
    return int(pin_pulls[0] or pin_pulls[1])

# передача 0 или 1
def pull_pin(n, pull):
    global pin_pulls
    pin_pulls[n] = pull


statuses = [None, None]


def checkin(n, status):
    global statuses
    statuses[n] = status


TIME_BASE = 0.002

MIN_LEN_ACTIVE_SIGNAL = 4
ONE_BIT_LENGTH = 4 * TIME_BASE

def is_get_master_signal(pin_states):
    result = False
    signal_length = 0
    max_signal_length = 0

    for i in range(len(pin_states)):
        if pin_states[i] == 1:
            signal_length += 1
        if pin_states[i] == 0 or i == len(pin_states) - 1:
            if signal_length > max_signal_length:
                max_signal_length = signal_length
            signal_length = 0

    if max_signal_length >= MIN_LEN_ACTIVE_SIGNAL:
        result = True

    return result


def actor(*args):
    n = args[0]

    while True:
        print(n, "start round")

        if random() > 0.5:
            print(n, "active")
            pull_pin(n, True)
            sleep(TIME_BASE * 20)
            pull_pin(n, False)
            print("listen for result:")
            sleep(TIME_BASE * 20)
            pin_states = []
            for _ in range(20):
                pin_states.append(read_pin())
                sleep(TIME_BASE * 1)
            print(n, "master result:", pin_states)
            prev = 0
            diffs = []
            for i in pin_states:
                diffs.append(abs(prev - i))
                prev = i
            print(n, "diffs:", diffs)
            if sum(diffs) >= 7:
                print(n, "get master role")
                checkin(n, 1)
                # отправляем ключ
                break

        else:
            print(n, "passive")
            # check hold for 0.5 sec
            pin_states = []
            for _ in range(10):
                pin_states.append(read_pin())
                sleep(TIME_BASE * 4)
            print(n, "result:", pin_states)
            # make magicanian
            if is_get_master_signal(pin_states):
                # old logic
                # if sum(pin_states) > 4:
                print(n, "get slave role")
                for _ in range(10):
                    pull_pin(n, True)
                    sleep(TIME_BASE * 2)
                    pull_pin(n, False)
                    sleep(TIME_BASE * 2)
                checkin(n, 0)

                # ждём ключ
                break
        sleep(random() * TIME_BASE * 3)


while True:
    statuses = [None, None]

    s_0 = threading.Thread(name='subs', target=actor, args=(0,), daemon=True)
    s_0.start()
    sleep(random() * TIME_BASE * 100)
    s_1 = threading.Thread(name='subs', target=actor, args=(1,), daemon=True)
    s_1.start()

    s_0.join()
    s_1.join()

    print("-------------")

    if statuses[0] is None or statuses[1] is None or statuses[0] == statuses[1]:
        print("procedure error")
        break
