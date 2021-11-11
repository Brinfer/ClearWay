# import RPi.GPIO as GPIO
from threading import Thread
import time
import logging
from enum import auto, unique, Enum
from queue import Queue

from transitions import State
from transitions.core import Machine

# Only accept message equals or upper to WARNING from transitions packages
logging.getLogger("transitions").setLevel(logging.WARNING)

__state_machines = {}
__LOOP_KEY = "loop"
__QUEUE_KEY = "queue"


@unique
class _StateEnum(Enum):
    INIT = (0,)
    OFF = (auto(),)
    SIGNALING = (auto(),)
    STOP = auto()


@unique
class __EventEnum(Enum):
    STOP = (0,)
    SIGNAL = (auto(),)
    STOP_SIGNAL = auto()


class StateMachinePanel:
    STATES = (
        # State(name=_StateEnum.INIT),
        State(name=_StateEnum.OFF, on_enter="_stop_signal"),
        State(name=_StateEnum.SIGNALING, on_enter="_signal"),
        State(name=_StateEnum.STOP, on_enter="_stop_signal"),
    )

    TRANSITIONS = (
        # {"trigger": "startStateMachine", "source": _StateEnum.INIT, "dest": _StateEnum.OFF},
        # {"trigger": "stopStateMachine", "source": _StateEnum.INIT, "dest": _StateEnum.STOP},
        {
            "trigger": "startSignal",
            "source": _StateEnum.OFF,
            "dest": _StateEnum.SIGNALING,
        },
        {
            "trigger": "stopStateMachine",
            "source": _StateEnum.OFF,
            "dest": _StateEnum.STOP,
        },
        {
            "trigger": "stopSignal",
            "source": _StateEnum.SIGNALING,
            "dest": _StateEnum.OFF,
        },
        {
            "trigger": "stopStateMachine",
            "source": _StateEnum.SIGNALING,
            "dest": _StateEnum.STOP,
        },
    )

    def __init__(self, p_gpio: int) -> None:
        Machine(
            model=self,
            states=StateMachinePanel.STATES,
            initial=_StateEnum.OFF,
            transitions=StateMachinePanel.TRANSITIONS,
            queued=True,
        )
        self.__gpio = p_gpio
        self.__blinkThread = None

        # GPIO.setmode(GPIO.BOARD) #Définit le mode de numérotation (Board)
        # GPIO.setwarnings(False) #On désactive les messages d"signale
        # GPIO.setup(self.__led, GPIO.OUT) #Active le contrôle du GPIO

        # raise ValueError("A very specific bad thing happened.")

    def _signal(self):
        logging.info("[LED] - Action: start signaling")

        self.__blinkThread = Thread(target=self.__thread_run)
        self.__blinkThread.start()

    def _stop_signal(self):
        logging.info("[LED] - Action: stop signaling")

        if self.__blinkThread is not None:
            self.__blinkThread.join()

    def __turn_on(self):
        logging.debug("[LED] Turn hight the GPIO %s", self.__gpio)
        # GPIO.output(self.__led, GPIO.HIGH)

    def __turn_off(self):
        logging.debug("[LED] Turn down the GPIO %s", self.__gpio)
        # GPIO.output(self.__led, GPIO.LOW)

    def __thread_run(self):
        while self.is_SIGNALING() is True:
            self.__turn_on()
            time.sleep(1)
            self.__turn_off()
            time.sleep(1)


def new(p_gpio: int) -> None:
    global __state_machines

    logging.info("[LED] - Event: create new state machine for GPIO %s", p_gpio)

    queue = Queue()
    state_machine = StateMachinePanel(p_gpio)

    __state_machines[str(p_gpio)] = {
        __LOOP_KEY: Thread(
            target=__run,
            name="[LED] GPIO {}".format(str(p_gpio)),
            args=(queue, state_machine),
        ),
        __QUEUE_KEY: queue,
    }


def start(p_gpio: int) -> None:
    global __state_machines

    logging.info("[LED] - Event: start the state machine for GPIO %s", p_gpio)

    __state_machines[str(p_gpio)][__LOOP_KEY].start()


def stop(p_gpio: int) -> None:
    global __state_machines

    logging.info("[LED] - Event: stop the state machine for GPIO %s", p_gpio)
    __state_machines[str(p_gpio)][__QUEUE_KEY].put(__EventEnum.STOP)
    __state_machines[str(p_gpio)][__LOOP_KEY].join()


def free(p_gpio: int) -> None:
    global __state_machines

    logging.info("[LED] - Event: destroy the state machine for GPIO %s", p_gpio)
    # TODO


def signal(p_gpio: int) -> None:
    global __state_machines

    logging.info("[LED] - Event: make blinking the state machine for GPIO %s", p_gpio)
    __state_machines[str(p_gpio)][__QUEUE_KEY].put(__EventEnum.SIGNAL)


def end_signal(p_gpio: int) -> None:
    global __state_machines

    logging.info("[LED] - Event Make blinking the state machine for GPIO %s", p_gpio)
    __state_machines[str(p_gpio)][__QUEUE_KEY].put(__EventEnum.STOP_SIGNAL)


def __run(p_queue: Queue, p_state_machine: StateMachinePanel):
    l_last_event = None

    while l_last_event != __EventEnum.STOP:
        l_last_event = p_queue.get()

        if l_last_event is __EventEnum.SIGNAL:
            p_state_machine.startSignal()
        elif l_last_event is __EventEnum.STOP_SIGNAL:
            p_state_machine.stopSignal()
