from enums import UniqueIntEnum
from fsm import FSM
from registry import register


class ButtonState(UniqueIntEnum):
    IdleUp = 1
    IdleDown = 2
    Hover = 3
    HoverPressed = 4
    Pressed = 5
    HeldOutside = 6
    Fire = 7

    @classmethod
    def default(cls):
        return cls.IdleUp


class ButtonEvent(UniqueIntEnum):
    Press = 1
    Release = 2
    Enter = 3
    Leave = 4


class ButtonFSM(FSM):
    """
    A FSM implementation for a standard pushbutton control.

    States are enumerated values as defined by the UniqueIntEnum class. See
    ButtonState class for full enumerated values.

    Based on http://web.stanford.edu/class/archive/cs/cs103/cs103.1142/button-fsm/
    """

    def __init__(self):
        super(ButtonFSM, self).__init__(ButtonState, ButtonEvent)

        self.add_transition(ButtonState.IdleUp,
                            ButtonEvent.Press,
                            ButtonState.IdleDown)

        self.add_transition(ButtonState.IdleUp,
                            ButtonEvent.Enter,
                            ButtonState.Hover)

        self.add_transition(ButtonState.IdleDown,
                            ButtonEvent.Release,
                            ButtonState.IdleUp)

        self.add_transition(ButtonState.IdleDown,
                            ButtonEvent.Enter,
                            ButtonState.HoverPressed)

        self.add_transition(ButtonState.HoverPressed,
                            ButtonEvent.Leave,
                            ButtonState.IdleDown)

        self.add_transition(ButtonState.HoverPressed,
                            ButtonEvent.Release,
                            ButtonState.Hover)

        self.add_transition(ButtonState.Hover,
                            ButtonEvent.Leave,
                            ButtonState.IdleUp)

        self.add_transition(ButtonState.Hover,
                            ButtonEvent.Press,
                            ButtonState.Pressed)

        self.add_transition(ButtonState.Pressed,
                            ButtonEvent.Release,
                            ButtonState.Fire)

        self.add_transition(ButtonState.Pressed,
                            ButtonEvent.Leave,
                            ButtonState.HeldOutside)

        self.add_transition(ButtonState.HeldOutside,
                            ButtonEvent.Enter,
                            ButtonState.Pressed)

        self.add_transition(ButtonState.HeldOutside,
                            ButtonEvent.Release,
                            ButtonState.IdleUp)


@register
class Button(object):
    __clsid__ = 'buttons'

    def __init__(self):
        self.fsm = ButtonFSM()
        self._state = self.fsm.states.default()

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value):
        self._state = value
