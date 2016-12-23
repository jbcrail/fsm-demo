from enums import UniqueIntEnum
from fsm import FSM
from registry import register


class PatternState(UniqueIntEnum):
    Start = 1
    LeadingA = 2
    B = 3
    TrailingA = 4
    Accept = 5
    Reject = 6

    @classmethod
    def default(cls):
        return cls.Start


class PatternEvent(UniqueIntEnum):
    A = 1
    B = 2
    EOF = 3


class PatternFSM(FSM):
    """
    A FSM implementation for a regex pattern [A*BA*].

    States are enumerated values as defined by the UniqueIntEnum class. See
    PatternState class for full enumerated values.
    """

    def __init__(self):
        super(PatternFSM, self).__init__(PatternState, PatternEvent)

        self.add_transition(PatternState.Start,
                            PatternEvent.A,
                            PatternState.LeadingA)

        self.add_transition(PatternState.Start,
                            PatternEvent.B,
                            PatternState.B)

        self.add_transition(PatternState.Start,
                            PatternEvent.EOF,
                            PatternState.Reject)

        self.add_transition(PatternState.LeadingA,
                            PatternEvent.A,
                            PatternState.LeadingA)

        self.add_transition(PatternState.LeadingA,
                            PatternEvent.B,
                            PatternState.B)

        self.add_transition(PatternState.B,
                            PatternEvent.A,
                            PatternState.TrailingA)

        self.add_transition(PatternState.B,
                            PatternEvent.B,
                            PatternState.Reject)

        self.add_transition(PatternState.B,
                            PatternEvent.EOF,
                            PatternState.Accept)

        self.add_transition(PatternState.TrailingA,
                            PatternEvent.A,
                            PatternState.TrailingA)

        self.add_transition(PatternState.TrailingA,
                            PatternEvent.B,
                            PatternState.Reject)

        self.add_transition(PatternState.TrailingA,
                            PatternEvent.EOF,
                            PatternState.Accept)


@register
class Pattern(object):
    __clsid__ = 'patterns'

    def __init__(self):
        self.fsm = PatternFSM()
        self._state = self.fsm.states.default()

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value):
        self._state = value
