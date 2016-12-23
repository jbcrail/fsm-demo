from enums import UniqueIntEnum
from fsm import FSM
from registry import register


class TurnstileState(UniqueIntEnum):
    Locked = 1
    Unlocked = 2

    @classmethod
    def default(cls):
        return cls.Locked


class TurnstileEvent(UniqueIntEnum):
    Push = 1
    Coin = 2


class TurnstileFSM(FSM):
    """
    A FSM implementation for a simple turnstile.

    States are enumerated values as defined by the UniqueIntEnum class. See
    TurnstileState class for full enumerated values.
    """

    def __init__(self):
        super(TurnstileFSM, self).__init__(TurnstileState, TurnstileEvent)

        self.add_transition(TurnstileState.Locked,
                            TurnstileEvent.Push,
                            TurnstileState.Locked)

        self.add_transition(TurnstileState.Locked,
                            TurnstileEvent.Coin,
                            TurnstileState.Unlocked)

        self.add_transition(TurnstileState.Unlocked,
                            TurnstileEvent.Coin,
                            TurnstileState.Unlocked)

        self.add_transition(TurnstileState.Unlocked,
                            TurnstileEvent.Push,
                            TurnstileState.Locked)


@register
class Turnstile(object):
    __clsid__ = 'turnstiles'

    def __init__(self):
        self.fsm = TurnstileFSM()
        self._state = self.fsm.states.default()

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value):
        self._state = value
