# import RPi.GPIO as GPIO
from threading import Thread
import time
import logging
from transitions import State
from enum import auto, unique, Enum
from transitions.core import Machine
from queue import Queue

# Only accept message equals or upper to WARNING from transitions packages
logging.getLogger("transitions").setLevel(logging.WARNING)

__stateMachines = {}
__LOOP_KEY = "loop"
__QUEUE_KEY = "queue"


@unique
class _StateEnum(Enum):
    INIT = 0,
    OFF = auto(),
    SIGNALING = auto(),
    STOP = auto()


@unique
class __EventEnum(Enum):
    STOP = 0;
    SIGNAL = auto(),
    STOP_SIGNAL = auto()


class LEDStateMachine():
    STATES = (
        # State(name=_StateEnum.INIT),
        State(name=_StateEnum.OFF, on_enter="_stopSignal"),
        State(name=_StateEnum.SIGNALING, on_enter="_signal"),
        State(name=_StateEnum.STOP, on_enter="_stopSignal")
    )

    TRANSITIONS = (
        # {"trigger": "startStateMachine", "source": _StateEnum.INIT, "dest": _StateEnum.OFF},
        # {"trigger": "stopStateMachine", "source": _StateEnum.INIT, "dest": _StateEnum.STOP},

        {"trigger": "startSignal", "source": _StateEnum.OFF, "dest": _StateEnum.SIGNALING},
        {"trigger": "stopStateMachine", "source": _StateEnum.OFF, "dest": _StateEnum.STOP},

        {"trigger": "stopSignal", "source": _StateEnum.SIGNALING, "dest": _StateEnum.OFF},
        {"trigger": "stopStateMachine", "source": _StateEnum.SIGNALING, "dest": _StateEnum.STOP},
    )

    def __init__(self, p_gpio: int) -> None:
        Machine(model=self,
                states=LEDStateMachine.STATES,
                initial=_StateEnum.OFF,
                transitions=LEDStateMachine.TRANSITIONS,
                queued=True)
        self.__gpio = p_gpio
        self.__blinkThread = None

        # GPIO.setmode(GPIO.BOARD) #Définit le mode de numérotation (Board)
        # GPIO.setwarnings(False) #On désactive les messages d"signale
        # GPIO.setup(self.__led, GPIO.OUT) #Active le contrôle du GPIO

        # raise ValueError("A very specific bad thing happened.")

    def _signal(self):
        logging.info("[LED] - Action: start signaling")

        self.__blinkThread = Thread(target=self.__threadRun)
        self.__blinkThread.start()

    def _stopSignal(self):
        logging.info("[LED] - Action: stop signaling")

        if self.__blinkThread is not None:
            self.__blinkThread.join()

    def __turnOn(self):
        logging.debug("[LED] Turn hight the GPIO %s", self.__gpio)
        # GPIO.output(self.__led, GPIO.HIGH)

    def __turnOff(self):
        logging.debug("[LED] Turn down the GPIO %s", self.__gpio)
        # GPIO.output(self.__led, GPIO.LOW)

    def __threadRun(self):
        while self.is_SIGNALING() is True:
            self.__turnOn()
            time.sleep(1)
            self.__turnOff()
            time.sleep(1)


def new(p_gpio: int) -> None:
    global __stateMachines

    logging.info("[LED] - Event: create new state machine for GPIO %s", p_gpio)

    queue = Queue()
    stateMachine = LEDStateMachine(p_gpio)

    __stateMachines[str(p_gpio)] = {
        __LOOP_KEY: Thread(target=__run, name="[LED] GPIO {}".format(str(p_gpio)), args=(queue, stateMachine)),
        __QUEUE_KEY: queue
    }


def start(p_gpio: int) -> None:
    global __stateMachines

    logging.info("[LED] - Event: start the state machine for GPIO %s", p_gpio)

    __stateMachines[str(p_gpio)][__LOOP_KEY].start()


def stop(p_gpio: int) -> None:
    global __stateMachines

    logging.info("[LED] - Event: stop the state machine for GPIO %s", p_gpio)
    __stateMachines[str(p_gpio)][__QUEUE_KEY].put(__EventEnum.STOP)
    __stateMachines[str(p_gpio)][__LOOP_KEY].join()


def free(p_gpio: int) -> None:
    global __stateMachines

    logging.info("[LED] - Event: destroy the state machine for GPIO %s", p_gpio)
    # TODO


def signal(p_gpio: int) -> None:
    global __stateMachines

    logging.info("[LED] - Event: make blinking the state machine for GPIO %s", p_gpio)
    __stateMachines[str(p_gpio)][__QUEUE_KEY].put(__EventEnum.SIGNAL)


def endSignal(p_gpio: int) -> None:
    global __stateMachines

    logging.info("[LED] - Event Make blinking the state machine for GPIO %s", p_gpio)
    __stateMachines[str(p_gpio)][__QUEUE_KEY].put(__EventEnum.STOP_SIGNAL)


def __run(p_queue: Queue, p_stateMachie: LEDStateMachine):
    l_lastEvent = None

    while l_lastEvent != __EventEnum.STOP:
        l_lastEvent = p_queue.get()

        if l_lastEvent is __EventEnum.SIGNAL:
            p_stateMachie.startSignal()
        elif l_lastEvent is __EventEnum.STOP_SIGNAL:
            p_stateMachie.stopSignal()
