"""Allows you to test the module clearway.gpio.stateMachinePanel.

Yields
------
`stateMachinePanel.StateMachinePanel`
    The tested state machine.
"""

from time import sleep

import pytest
from pytest_mock.plugin import MockerFixture
from clearway.gpio import stateMachinePanel

"""The number of the GPIO driven by the state machine."""
GPIO = 5

"""The time allowed for the triggers to run before continuing the tests."""
DELAY = 0.7


@pytest.fixture()
def state_machine_tested() -> None:
    """Provide a state machine using GPIO number 5.

    The function takes care of creating and launching the report machine.
    Once it is not used anymore, it is then stopped and deleted.

    Yields
    ------
    `stateMachinePanel.StateMachinePanel`
        A state machine, using gpio number 5.
    """
    stateMachinePanel.use_gpio(False)

    state_machine = stateMachinePanel.new(5)
    stateMachinePanel.start(GPIO)

    yield state_machine

    stateMachinePanel.stop(GPIO)
    stateMachinePanel.free(GPIO)


def test_state_machine_nominal(
    mocker: MockerFixture, state_machine_tested: stateMachinePanel.StateMachinePanel
) -> None:
    """Checks that the state machine works in a nominal scenario.

    The `signal` and `end_signal` will be sent successively, the good change of the pins state will be checked

    Parameters
    ----------
    mocker : MockerFixture
        The interface for the mock module functions
    state_machine_tested : stateMachinePanel.StateMachinePanel
        The state machine on which the tests are executed, this one must be in the initial state.
    """
    spy_action_signal = mocker.spy(state_machine_tested, "_signal")
    spy_action_stop_signal = mocker.spy(state_machine_tested, "_stop_signal")

    action_signal_counter = 0
    action_stop_signal_counter = 0

    assert spy_action_stop_signal.call_count == action_stop_signal_counter
    assert spy_action_signal.call_count == 0

    stateMachinePanel.signal(GPIO)
    sleep(DELAY)
    action_signal_counter += 1

    assert spy_action_stop_signal.call_count == action_stop_signal_counter
    assert spy_action_signal.call_count == action_signal_counter

    stateMachinePanel.end_signal(GPIO)
    sleep(DELAY)
    action_stop_signal_counter += 1

    assert spy_action_stop_signal.call_count == action_stop_signal_counter
    assert spy_action_signal.call_count == action_signal_counter

    stateMachinePanel.signal(GPIO)
    sleep(DELAY)
    action_signal_counter += 1

    assert spy_action_stop_signal.call_count == action_stop_signal_counter
    assert spy_action_signal.call_count == action_signal_counter

    stateMachinePanel.end_signal(GPIO)
    sleep(DELAY)
    action_stop_signal_counter += 1

    assert spy_action_stop_signal.call_count == action_stop_signal_counter
    assert spy_action_signal.call_count == action_signal_counter


def test_repeat_same_command(mocker: MockerFixture, state_machine_tested: stateMachinePanel.StateMachinePanel) -> None:
    """Checks that no action is executed during an unsupported event.

    The state machine is placed in a specific state and events not taken into account by the state are not executed.

    Parameters
    ----------
    mocker : MockerFixture
        The interface for the mock module functions
    state_machine_tested : stateMachinePanel.StateMachinePanel
        The state machine on which the tests are executed, this one must be in the initial state.
    """
    spy_action_signal = mocker.spy(state_machine_tested, "_signal")
    spy_action_stop_signal = mocker.spy(state_machine_tested, "_stop_signal")

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
