"""Allows you to test the module `clearway.gpio.stateMachinePanel`.

Yields
------
`stateMachinePanel.StateMachinePanel`
    The tested state machine.
"""

from time import sleep

import pytest
import clearway.gpio as gpio
from pytest_mock.plugin import MockerFixture
from clearway.gpio import stateMachinePanel

GPIO: int = [5, 6]
"""The number of the GPIOs driven by the state machine."""

DELAY: float = 2.0
"""The time allowed for the triggers to run before continuing the tests."""


def setup() -> None:
    """Set up the test.

    The function is called before every test.
    """
    gpio.use_gpio(False)

    stateMachinePanel.new(GPIO)
    stateMachinePanel.start()


def teardown() -> None:
    """Tear down the test.

    The function is called after every test.
    """
    stateMachinePanel.stop()
    stateMachinePanel.free()


def test_state_machine_nominal(mocker: MockerFixture) -> None:
    """Checks that the state machine works in a nominal scenario.

    The `signal` and `end_signal` will be sent successively, the good change of the GPIOs state will be checked.
    The GPIOs will receive signals in a staggered way to verify that they are all independent.

    Parameters
    ----------
    mocker : `MockerFixture`
        The interface for the mock module functions
    """
    spy_action_signal_0 = mocker.spy(stateMachinePanel.__state_machines[str(GPIO[0])], "_signal")
    spy_action_stop_signal_0 = mocker.spy(stateMachinePanel.__state_machines[str(GPIO[0])], "_stop_signal")
    spy_action_signal_1 = mocker.spy(stateMachinePanel.__state_machines[str(GPIO[1])], "_signal")
    spy_action_stop_signal_1 = mocker.spy(stateMachinePanel.__state_machines[str(GPIO[1])], "_stop_signal")

    action_signal_counter_0 = 0
    action_stop_signal_counter_0 = 0
    action_signal_counter_1 = 0
    action_stop_signal_counter_1 = 0

    assert spy_action_stop_signal_0.call_count == action_stop_signal_counter_0
    assert spy_action_signal_0.call_count == action_signal_counter_0
    assert spy_action_stop_signal_1.call_count == action_stop_signal_counter_1
    assert spy_action_signal_1.call_count == action_signal_counter_1

    # Pass to SIGNAL state
    stateMachinePanel.signal(GPIO)
    sleep(DELAY)
    action_signal_counter_0 += 1
    action_signal_counter_1 += 1

    assert spy_action_stop_signal_0.call_count == action_stop_signal_counter_0
    assert spy_action_signal_0.call_count == action_signal_counter_0
    assert spy_action_stop_signal_1.call_count == action_stop_signal_counter_1
    assert spy_action_signal_1.call_count == action_signal_counter_1

    # Pass to OFF state
    stateMachinePanel.end_signal(GPIO)
    sleep(DELAY)
    action_stop_signal_counter_0 += 1
    action_stop_signal_counter_1 += 1

    assert spy_action_stop_signal_0.call_count == action_stop_signal_counter_0
    assert spy_action_signal_0.call_count == action_signal_counter_0
    assert spy_action_stop_signal_1.call_count == action_stop_signal_counter_1
    assert spy_action_signal_1.call_count == action_signal_counter_1

    # Pass to SIGNAL state
    stateMachinePanel.signal(GPIO)
    sleep(DELAY)
    action_signal_counter_0 += 1
    action_signal_counter_1 += 1

    assert spy_action_stop_signal_0.call_count == action_stop_signal_counter_0
    assert spy_action_signal_0.call_count == action_signal_counter_0
    assert spy_action_stop_signal_1.call_count == action_stop_signal_counter_1
    assert spy_action_signal_1.call_count == action_signal_counter_1

    # Pass to OFF state for state machine 0
    stateMachinePanel.end_signal(GPIO[0])
    sleep(DELAY)
    action_stop_signal_counter_0 += 1

    assert spy_action_stop_signal_0.call_count == action_stop_signal_counter_0
    assert spy_action_signal_0.call_count == action_signal_counter_0
    assert spy_action_stop_signal_1.call_count == action_stop_signal_counter_1
    assert spy_action_signal_1.call_count == action_signal_counter_1

    # Pass to OFF state for state machine 1
    stateMachinePanel.end_signal(GPIO[1])
    sleep(DELAY)
    action_stop_signal_counter_1 += 1

    assert spy_action_stop_signal_0.call_count == action_stop_signal_counter_0
    assert spy_action_signal_0.call_count == action_signal_counter_0
    assert spy_action_stop_signal_1.call_count == action_stop_signal_counter_1
    assert spy_action_signal_1.call_count == action_signal_counter_1

    # Pass to ON state for state machine 0
    stateMachinePanel.signal(GPIO[0])
    sleep(DELAY)
    action_signal_counter_0 += 1

    assert spy_action_stop_signal_0.call_count == action_stop_signal_counter_0
    assert spy_action_signal_0.call_count == action_signal_counter_0
    assert spy_action_stop_signal_1.call_count == action_stop_signal_counter_1
    assert spy_action_signal_1.call_count == action_signal_counter_1

    # Pass to ON state for state machine 1
    stateMachinePanel.signal(GPIO[1])
    sleep(DELAY)
    action_signal_counter_1 += 1

    assert spy_action_stop_signal_0.call_count == action_stop_signal_counter_0
    assert spy_action_signal_0.call_count == action_signal_counter_0
    assert spy_action_stop_signal_1.call_count == action_stop_signal_counter_1
    assert spy_action_signal_1.call_count == action_signal_counter_1

    # Pass to STOP
    stateMachinePanel.stop()
    sleep(DELAY)
    action_stop_signal_counter_0 += 1
    action_stop_signal_counter_1 += 1

    assert spy_action_stop_signal_0.call_count == action_stop_signal_counter_0
    assert spy_action_signal_0.call_count == action_signal_counter_0
    assert spy_action_stop_signal_1.call_count == action_stop_signal_counter_1
    assert spy_action_signal_1.call_count == action_signal_counter_1


def test_repeat_same_command(mocker: MockerFixture) -> None:
    """Checks that no action is executed during an unsupported event.

    The state machine is placed in a specific state and events not taken into account by the state are not executed.

    Parameters
    ----------
    mocker : `MockerFixture`
        The interface for the mock module functions
    """
    spy_action_signal = mocker.spy(stateMachinePanel.__state_machines[str(GPIO[0])], "_signal")
    spy_action_stop_signal = mocker.spy(stateMachinePanel.__state_machines[str(GPIO[0])], "_stop_signal")

    action_signal_counter = 0
    action_stop_signal_counter = 0

    assert spy_action_stop_signal.call_count == action_stop_signal_counter
    assert spy_action_signal.call_count == action_signal_counter

    # Change to SIGNAL state

    stateMachinePanel.signal(GPIO)
    sleep(DELAY)
    action_signal_counter += 1

    assert spy_action_stop_signal.call_count == action_stop_signal_counter
    assert spy_action_signal.call_count == action_signal_counter

    # Should not execute the action signal
    stateMachinePanel.signal(GPIO)
    sleep(DELAY)

    assert spy_action_stop_signal.call_count == action_stop_signal_counter
    assert spy_action_signal.call_count == action_signal_counter

    # Change to OFF state

    stateMachinePanel.end_signal(GPIO)
    sleep(DELAY)
    action_stop_signal_counter += 1

    assert spy_action_stop_signal.call_count == action_stop_signal_counter
    assert spy_action_signal.call_count == action_signal_counter

    # Should not execute the action stop_signal
    stateMachinePanel.end_signal(GPIO)
    sleep(DELAY)

    assert spy_action_stop_signal.call_count == action_stop_signal_counter
    assert spy_action_signal.call_count == action_signal_counter

    # Change to STOP state

    stateMachinePanel.stop()
    sleep(DELAY)
    action_stop_signal_counter += 1

    assert spy_action_stop_signal.call_count == action_stop_signal_counter
    assert spy_action_signal.call_count == action_signal_counter

    # Should not execute the action stop_signal
    stateMachinePanel.end_signal(GPIO)
    sleep(DELAY)

    assert spy_action_stop_signal.call_count == action_stop_signal_counter
    assert spy_action_signal.call_count == action_signal_counter

    # Should not execute the action signal
    stateMachinePanel.signal(GPIO)
    sleep(DELAY)

    assert spy_action_stop_signal.call_count == action_stop_signal_counter
    assert spy_action_signal.call_count == action_signal_counter
