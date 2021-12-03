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

from threading import Thread
import time
import logging
from enum import auto, unique, Enum
from queue import Queue

from transitions import State
from transitions.core import Machine
import clearway.gpio as gpio


# Only accept message equals or upper to WARNING from transitions packages
logging.getLogger("transitions").setLevel(logging.WARNING)

__state_machines = {}
__LOOP_KEY = "loop"
__QUEUE_KEY = "queue"

_FREQUENCY = 2


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
    The state machine is based on the transitions [1] package licenced by MIT


    .. uml::
        [*] --> Off : start
        Off --> Signaling : signal / signal()
        Off --> [*] : stop
        Signaling --> Off : end_signal / stop_signal()
        Signaling --> [*] : stop / stop_signal()

    .. [1] https://github.com/pytransitions/transitions
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
            The  to be set high
        """
        logging.debug("[-%s] Turn hight", p_gpio)

        if gpio.GPIO is not None:
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
        logging.debug("[GPIO-%s] Turn down", p_gpio)

        if gpio.GPIO is not None:
            gpio.GPIO.output(p_gpio, gpio.GPIO.LOW)

    def __init__(self, p_gpio: int) -> None:
        logging.debug("[GPIO-%s] - Create the state machine", p_gpio)

        Machine(
            model=self,
            states=StateMachinePanel.STATES,
            initial=_StateEnum.OFF,
            transitions=StateMachinePanel.TRANSITIONS,
            queued=True,
            ignore_invalid_triggers=True,
        )
        self.__gpio = p_gpio  # type: int
        self.__blinkThread = None  # type: Thread

        if gpio.GPIO is not None:
            gpio.GPIO.setmode(gpio.GPIO.BCM)
            gpio.GPIO.setwarnings(False)  # Disable warning messages
            gpio.GPIO.setup(self.__gpio, gpio.GPIO.OUT)

        StateMachinePanel.turn_off(self.__gpio)  # Force at low level

    def __del__(self) -> None:
        """Destroys the state machine.

        Set the gpio to low level.
        """
        logging.debug("[GPIO-%s] - Destroy the state machine", self.__gpio)

        StateMachinePanel.turn_off(self.__gpio)

    def _signal(self) -> None:
        if self.__blinkThread is None:
            logging.info("[GPIO-%s] - Action: start signaling", self.__gpio)
            self.__blinkThread = Thread(target=self.__thread_run)
            self.__blinkThread.start()
        else:
            logging.warning("[GPIO-%s] - Action: already signaling", self.__gpio)

    def _stop_signal(self) -> None:
        if self.__blinkThread is not None and self.__blinkThread.is_alive():
            logging.info("[GPIO-%s] - Action: stop signaling", self.__gpio)
            self.__blinkThread.join()
            self.__blinkThread = None
        else:
            logging.warning("[GPIO-%s] - Action: is not signaling", self.__gpio)

    def __thread_run(self) -> None:
        while self.is_SIGNALING() is True:  # Test the actual state of the state machine
            StateMachinePanel.turn_on(self.__gpio)
            time.sleep(_FREQUENCY / 2)
            StateMachinePanel.turn_off(self.__gpio)
            time.sleep(_FREQUENCY / 2)


def new(p_gpio: int) -> StateMachinePanel:
    """Create a new state machine for the given port.

    Parameters
    ----------
    p_gpio : `int`
        The port that will be controlled by the state machine.

    Returns
    -------
    StateMachinePanel
        The new state machine created
    """
    global __state_machines

    logging.info("[GPIO-%s] - Event: create new state machine", p_gpio)

    queue = Queue()
    state_machine = StateMachinePanel(p_gpio)

    __state_machines[str(p_gpio)] = {
        __LOOP_KEY: Thread(
            target=__run,
            name="[GPIO-{}]".format(str(p_gpio)),
            args=(queue, state_machine),
        ),
        __QUEUE_KEY: queue,
    }

    return state_machine


def start(p_gpio: int) -> None:
    """Start the state machine for the given port.

    Parameters
    ----------
    p_gpio : `int`
        The port controlled by the state machine

    Raises
    ------
    KeyError
        The state machine was not created
    """
    global __state_machines

    logging.info("[GPIO-%s] - Event: start the state machine", p_gpio)

    __state_machines[str(p_gpio)][__LOOP_KEY].start()


def stop(p_gpio: int) -> None:
    """Stop the state machine for the given port.

    The current thread will be blocked until the state machine is stopped.

    Parameters
    ----------
    p_gpio : `int`
        The port that will be controlled by the state machine.

    Raises
    ------
    KeyError
        The state machine was not created.
    """
    global __state_machines

    logging.info("[GPIO-%s] - Event: stop the state machine", p_gpio)
    __state_machines[str(p_gpio)][__QUEUE_KEY].put(__EventEnum.STOP)
    __state_machines[str(p_gpio)][__LOOP_KEY].join()


def free(p_gpio: int) -> None:
    """Destroy the state machine for the given port.

    Parameters
    ----------
    p_gpio : `int`
        The port that will be controlled by the state machine.

    Raises
    ------
    KeyError
        The state machine was not created.
    """
    global __state_machines

    logging.info("[GPIO-%s] - Event: destroy the state machine", p_gpio)

    del __state_machines[str(p_gpio)]


def signal(p_gpio: int) -> None:
    """Signal to the state machine of the given port to emit the signal.

    Parameters
    ----------
    p_gpio : `int`
        The port that will be controlled by the state machine.

    Raises
    ------
    KeyError
        The state machine was not created.
    """
    global __state_machines

    logging.info("[GPIO-%s] - Event: make blinking the state machine", p_gpio)
    __state_machines[str(p_gpio)][__QUEUE_KEY].put(__EventEnum.SIGNAL)


def end_signal(p_gpio: int) -> None:
    """Signal to the given port state machine to stop transmitting the signal.

    Parameters
    ----------
    p_gpio : `int`
        The port that will be controlled by the state machine.

    Raises
    ------
    KeyError
        The state machine was not created.
    """
    global __state_machines

    logging.info("[GPIO-%s] - Event: stop blinking the state machine", p_gpio)
    __state_machines[str(p_gpio)][__QUEUE_KEY].put(__EventEnum.STOP_SIGNAL)


def __run(p_queue: Queue, p_state_machine: StateMachinePanel) -> None:
    l_last_event = None

    while l_last_event is not __EventEnum.STOP:
        l_last_event = p_queue.get()

        if l_last_event is __EventEnum.SIGNAL:
            p_state_machine.startSignal()
        elif l_last_event is __EventEnum.STOP_SIGNAL:
            p_state_machine.stopSignal()
        elif l_last_event is __EventEnum.STOP:
            p_state_machine.stopStateMachine()
