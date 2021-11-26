"""Allows you to test the module clearway.gpio.stateMachinePanel.

Yields
------
`stateMachinePanel.StateMachinePanel`
    The tested state machine, using gpio number 5.
"""

from time import sleep

import pytest
from pytest_mock.plugin import MockerFixture
from clearway.gpio import stateMachinePanel


@pytest.fixture()
def state_machine_gpio5() -> None:
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
    stateMachinePanel.start(5)

    yield state_machine

    stateMachinePanel.stop(5)
    stateMachinePanel.free(5)


def test_state_machine_nominal(mocker: MockerFixture, state_machine_gpio5: stateMachinePanel.StateMachinePanel) -> None:
    """Checks that the state machine works in a nominal scenario.

    The `signal` and `end_signal` will be sent successively, the good change of the pins state will be checked

    Parameters
    ----------
    mocker : MockerFixture
        The interface for the mock module functions
    state_machine_gpio5 : stateMachinePanel.StateMachinePanel
        The state machine on which the tests are executed, this one must be in the initial state.
    """
    spy_turn_on = mocker.spy(stateMachinePanel.StateMachinePanel, "turn_on")
    spy_turn_off = mocker.spy(stateMachinePanel.StateMachinePanel, "turn_off")
    spy_action_signal = mocker.spy(state_machine_gpio5, "_signal")
    spy_action_stop_signal = mocker.spy(state_machine_gpio5, "_stop_signal")

    assert spy_turn_off.call_count == 0
    assert spy_turn_on.call_count == 0
    assert spy_action_stop_signal.call_count == 0
    assert spy_action_signal.call_count == 0

    stateMachinePanel.signal(5)
    sleep(1)  # Give the state machine time to react

    assert spy_turn_off.call_count == 0
    assert spy_turn_on.call_count == 1
    assert spy_action_stop_signal.call_count == 0
    assert spy_action_signal.call_count == 1

    stateMachinePanel.end_signal(5)
    sleep(1)  # Give the state machine time to react

    assert spy_turn_off.call_count == 1
    assert spy_turn_on.call_count == 1
    assert spy_action_stop_signal.call_count == 1
    assert spy_action_signal.call_count == 1

    stateMachinePanel.signal(5)
    sleep(1)  # Give the state machine time to react

    assert spy_turn_off.call_count == 1
    assert spy_turn_on.call_count == 2
    assert spy_action_stop_signal.call_count == 1
    assert spy_action_signal.call_count == 2

    stateMachinePanel.end_signal(5)
    sleep(1)  # Give the state machine time to react

    assert spy_turn_off.call_count == 2
    assert spy_turn_on.call_count == 2
    assert spy_action_stop_signal.call_count == 2
    assert spy_action_signal.call_count == 2
