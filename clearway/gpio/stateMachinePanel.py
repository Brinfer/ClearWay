"""Module to control the state machines controlling the input and output of the card.

All state machines are asynchronous and independent.

Examples
--------
>>> from clearway.gpio import stateMachinePanel
>>> from time import sleep
>>> GPIO = 5
>>> stateMachinePanel.new(GPIO)
>>> stateMachinePanel.start(GPIO)
>>> for _ in range(5):
...     stateMachinePanel.signal(GPIO)
...     sleep(5)
...     stateMachinePanel.end_signal(GPIO)
...     sleep(5)
>>> stateMachinePanel.stop(GPIO)
>>> stateMachinePanel.free(GPIO)
"""

from threading import Thread, Lock
import time
import logging
from enum import auto, unique, Enum
from queue import Queue
from typing import Any, Dict, Iterable, Optional, Union

from transitions import State
from transitions.core import Machine
import clearway.gpio as gpio


# Only accept message equals or upper to WARNING from transitions packages
logging.getLogger("transitions").setLevel(logging.WARNING)

__state_machines: Dict[str, Any] = {}
__running_thread: Thread
__queue: Queue
__mutex: Optional[Lock] = None
_FREQUENCY: int = 2


@unique
class _StateEnum(Enum):
    INIT = 0
    OFF = auto()
    SIGNALING = auto()
    STOP = auto()


@unique
class __EventEnum(Enum):
    STOP = 0
    SIGNAL = auto()
    STOP_SIGNAL = auto()
    FINISH_THREAD = auto()


class StateMachinePanel:
    """State machine driving an input/output of the card.

    Attributes
    ----------
    STATES : `tuple(transitions.State)`
        The list of states that can be taken by the state machine.
    TRANSITIONS : `tuple(transitions.Transition)`
        The list of transitions between states of the state machine.

    Parameters
    ----------
    p_gpio : `int`
        The GPIO to be driven.

    Methods
    -------
    turn_on(p_gpio: int)
        Set the GPIO to high level
    turn_off(p_gpio: int)
        Set the GPIO to low level

    Notes
    -----
    The state machine is based on the transitions [1]_ package licensed by MIT

    .. uml::

        [*] --> Off : start
        Off --> Signaling : signal / signal()
        Off --> [*] : stop
        Signaling --> Off : end_signal / stop_signal()
        Signaling --> [*] : stop / stop_signal()

    .. _[1]:
        https://github.com/pytransitions/transitions
    """

    STATES = (
        State(name=_StateEnum.OFF, on_enter="_stop_signal"),
        State(name=_StateEnum.SIGNALING, on_enter="_signal"),
        State(name=_StateEnum.STOP, on_enter="_stop_signal"),
    )

    TRANSITIONS = (
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

    @staticmethod
    def turn_on(p_gpio: int) -> None:
        """Set the GPIO to high level.

        If the `use_gpio` function not called with the argument at `True`, then the GPIO will not be modified

        Parameters
        ----------
        p_gpio : `int`
            The GPIO to be set high
        """
        logging.debug("[PANEL-%s] Turn hight", p_gpio)

        gpio.GPIO.output(p_gpio, gpio.GPIO.HIGH)

    @staticmethod
    def turn_off(p_gpio: int) -> None:
        """Set the GPIO to low level.

        If the `use_gpio` function not called with the argument at `True`, then the GPIO will not be modified

        Parameters
        ----------
        p_gpio : `int`
            The GPIO to be set low
        """
        logging.debug("[PANEL-%s] Turn down", p_gpio)

        gpio.GPIO.output(p_gpio, gpio.GPIO.LOW)

    def __init__(self, p_gpio: int) -> None:
        logging.debug("[PANEL-%s] - Create the state machine", p_gpio)

        Machine(
            model=self,
            states=StateMachinePanel.STATES,
            initial=_StateEnum.OFF,
            transitions=StateMachinePanel.TRANSITIONS,
            queued=True,
            ignore_invalid_triggers=True,
        )
        self.__gpio: int = p_gpio
        self.__blinkThread: Optional[Thread] = None

        gpio.GPIO.setup(self.__gpio, gpio.GPIO.OUT)

        StateMachinePanel.turn_off(self.__gpio)  # Force at low level

    def __del__(self) -> None:
        """Destroys the state machine.

        Set the gpio to low level.
        """
        logging.debug("[PANEL-%s] - Destroy the state machine", self.__gpio)

        StateMachinePanel.turn_off(self.__gpio)

    def _signal(self) -> None:
        if self.__blinkThread is None:
            logging.info("[PANEL-%s] - Action: start signaling", self.__gpio)
            self.__blinkThread = Thread(
                target=self.__thread_run,
                name="[PANEL-{}-SIGNALING]".format(str(self.__gpio)),
            )
            self.__blinkThread.start()
        else:
            logging.info("[PANEL-%s] - Action: already signaling", self.__gpio)

    def _stop_signal(self) -> None:
        if self.__blinkThread is not None and self.__blinkThread.is_alive():
            logging.info("[PANEL-%s] - Action: stop signaling", self.__gpio)
            self.__blinkThread.join()
            self.__blinkThread = None
        else:
            logging.info("[PANEL-%s] - Action: is not signaling", self.__gpio)

    def __thread_run(self) -> None:
        while self.is_SIGNALING() is True:  # type: ignore
            # The current state is signaling
            StateMachinePanel.turn_on(self.__gpio)
            time.sleep(_FREQUENCY / 2)
            StateMachinePanel.turn_off(self.__gpio)
            time.sleep(_FREQUENCY / 2)


def new(p_gpio: Union[int, Iterable[int]]) -> None:
    """Create a new state machine for the given GPIOs.

    Parameters
    ----------
    p_gpio : Union[int, Iterable[int]]
        The GPIOs that will be controlled by a state machine.
    """
    global __state_machines, __mutex

    if __mutex is None:
        logging.debug("[PANEL] Create the mutex")
        __mutex = Lock()

    l_gpios: set

    if isinstance(p_gpio, int):
        l_gpios = set([p_gpio])
    elif not isinstance(p_gpio, set):
        l_gpios = set(p_gpio)
    else:
        l_gpios = p_gpio

    for l_gpio in l_gpios:
        logging.info("[PANEL-%s] - Event: create new state machine", l_gpio)

        state_machine = StateMachinePanel(l_gpio)

        __mutex.acquire()
        __state_machines[str(l_gpio)] = state_machine
        __mutex.release()


def start() -> None:
    """Start all the state machine."""
    global __state_machines, __running_thread, __queue, __mutex

    logging.info("[PANEL] - Event: start the thread for %d state machine", len(__state_machines.keys()))

    if __mutex is None:
        logging.debug("[PANEL] Create the mutex")
        __mutex = Lock()

    __queue = Queue()

    __running_thread = Thread(
        target=__run,
        name="[PANEL]",
    )

    __running_thread.start()


def stop() -> None:
    """Stop all the state machine.

    The current thread will be blocked until the state machine are stopped.
    """
    global __state_machines, __running_thread, __queue

    logging.info("[PANEL] - Event: stop all the state machine")

    l_gpio_list = tuple(__state_machines.keys())

    for l_gpio in l_gpio_list:
        __queue.put((__EventEnum.STOP, l_gpio))

    __queue.put((__EventEnum.FINISH_THREAD, None))
    __running_thread.join()


def free() -> None:
    """Destroy all the state machine."""
    global __state_machines

    logging.info("[GPIO] Free all the state machine")

    l_gpio_list = tuple(__state_machines.keys())

    for l_gpio in l_gpio_list:
        del __state_machines[l_gpio]


def signal(p_gpio: Union[int, Iterable[int]]) -> None:
    """Signal to the state machine of the given GPIOs to emit the signal.

    Parameters
    ----------
    p_gpio : Union[int, Iterable[int]]
        The GPIOs that will be controlled by the state machine.

    Raises
    ------
    KeyError
        The state machine was not created.
    """
    global __queue

    l_gpios: set

    if isinstance(p_gpio, int):
        l_gpios = set([p_gpio])
    elif not isinstance(p_gpio, set):
        l_gpios = set(p_gpio)
    else:
        l_gpios = p_gpio

    for l_gpio in l_gpios:
        logging.info("[PANEL-%s] - Event: make blinking the state machine", l_gpio)
        __queue.put((__EventEnum.SIGNAL, str(l_gpio)))


def end_signal(p_gpio: Union[int, Iterable[int]]) -> None:
    """Signal to the given GPIOs state machine to stop transmitting the signal.

    Parameters
    ----------
    p_gpio : Union[int, Iterable[int]]
        The GPIOs that will be controlled by the state machine.

    Raises
    ------
    KeyError
        The state machine was not created.
    """
    global __queue

    l_gpios: set

    if isinstance(p_gpio, int):
        l_gpios = set([p_gpio])
    elif not isinstance(p_gpio, set):
        l_gpios = set(p_gpio)
    else:
        l_gpios = p_gpio

    for l_gpio in l_gpios:
        logging.info("[PANEL-%s] - Event: stop blinking the state machine", l_gpio)
        __queue.put((__EventEnum.STOP_SIGNAL, str(l_gpio)))


def __run() -> None:
    global __queue, __mutex, __state_machines
    l_last_event: Optional[__EventEnum] = None

    while l_last_event is not __EventEnum.FINISH_THREAD:
        l_last_event, l_gpio = __queue.get()

        __mutex.acquire()  # type: ignore[union-attr]
        if l_last_event is __EventEnum.SIGNAL:
            __state_machines[l_gpio].startSignal()  # type: ignore[attr-defined]
        elif l_last_event is __EventEnum.STOP_SIGNAL:
            __state_machines[l_gpio].stopSignal()  # type: ignore[attr-defined]
        elif l_last_event is __EventEnum.STOP:
            __state_machines[l_gpio].stopStateMachine()  # type: ignore[attr-defined]
        __mutex.release()  # type: ignore[union-attr]
