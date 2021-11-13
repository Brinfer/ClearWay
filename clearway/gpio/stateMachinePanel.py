"""Module to control the state machines controlling the input and output of the card."""

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

_use_gpio = False
_GpioModule = None
_FREQUENCY = 2


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
    STOP_SIGNAL = (auto(),)


class StateMachinePanel:
    """State machine driving an input/output of the card.

    In the signaling state, the input output alternates between high and low with a frequency of
    py:attribute::_FREQUENCY.

    Attributes
    ----------
    __gpio : int
        The gpio driven by the state machine.
    __blinkThread : Thread
        The thread handler where the signaling state drives the gpio.
    STATES : tuple(State)
        The list of states that can be taken by the state machine.
    TRANSITIONS : tuple(Transition)
        The list of transitions between states of the state machine.

    .. uml::
        [*] --> Off : start
        Off --> Signaling : signal / signal()
        Off --> [*] : stop
        Signaling --> Off : end_signal / stop_signal()
        Signaling --> [*] : stop / stop_signal()
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

    def __init__(self, p_gpio: int) -> None:
        """Create a new state machine for the given GPIO.

        Parameters
        ----------
        p_gpio : int
            The GPIO to be driven.
        """
        global _use_gpio, _GpioModule

        logging.debug("[GPIO-%s] - Create the state machine", p_gpio)

        Machine(
            model=self,
            states=StateMachinePanel.STATES,
            initial=_StateEnum.OFF,
            transitions=StateMachinePanel.TRANSITIONS,
            queued=True,
        )
        self.__gpio = p_gpio
        self.__blinkThread = None

        if _use_gpio is True:
            _GpioModule.setmode(_GpioModule.BOARD)
            _GpioModule.setwarnings(False)  # Disable warning messages
            _GpioModule.setup(self.__gpio, _GpioModule.OUT)

            self.__turn_off()  # Force at low level

    def __del__(self) -> None:
        """Destroys the state machine.

        Set the gpio to low level.
        """
        logging.debug("[GPIO-%s] - Destroy the state machine", self.__gpio)

        self.__turn_off()

    def _signal(self) -> None:
        logging.info("[GPIO-%s] - Action: start signaling", self.__gpio)

        self.__blinkThread = Thread(target=self.__thread_run)
        self.__blinkThread.start()

    def _stop_signal(self) -> None:
        logging.info("[GPIO-%s] - Action: stop signaling", self.__gpio)

        if self.__blinkThread is not None:
            self.__blinkThread.join()

    def __turn_on(self) -> None:
        global _use_gpio, _GpioModule

        logging.debug("[GPIO-%s] Turn hight", self.__gpio)

        if _use_gpio:
            _GpioModule.output(self.__gpio, _GpioModule.HIGH)

    def __turn_off(self) -> None:
        global _use_gpio, _GpioModule

        logging.debug("[GPIO-%s] Turn down", self.__gpio)

        if _use_gpio:
            _GpioModule.output(self.__gpio, _GpioModule.LOW)

    def __thread_run(self) -> None:
        while self.is_SIGNALING() is True:
            self.__turn_on()
            time.sleep(_FREQUENCY / 2)
            self.__turn_off()
            time.sleep(_FREQUENCY / 2)


def use_gpio(p_value: bool) -> None:
    """Tells all state machines if they can modify the GPIO level.

    If the passed parameter is `True`, then the module `RPi.GPIO` is imported.
    This function must be called at the beginning of the program.

    Parameters
    ----------
    p_value : bool
        `True` if you want to use GPIOs, `False` otherwise.
    """
    global _use_gpio, _GpioModule

    _use_gpio = p_value

    if _use_gpio is True:
        import RPi.GPIO as _GpioModule
        # Import RPi.GPIO and save it in a protected variable


def new(p_gpio: int) -> None:
    """Create a new state machine for the given port.

    Parameters
    ----------
    p_gpio : int
        The port that will be controlled by the state machine.
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


def start(p_gpio: int) -> None:
    """Start the state machine for the given port.

    Parameters
    ----------
    p_gpio : int
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
    p_gpio : int
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
    p_gpio : int
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
    p_gpio : int
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
    p_gpio : int
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

    while l_last_event != __EventEnum.STOP:
        l_last_event = p_queue.get()

        if l_last_event is __EventEnum.SIGNAL:
            p_state_machine.startSignal()
        elif l_last_event is __EventEnum.STOP_SIGNAL:
            p_state_machine.stopSignal()