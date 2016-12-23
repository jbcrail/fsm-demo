class FSM(object):
    """
    A simple finite state machine (FSM).

    Each FSM has three main items: states, events, and transitions.

    First, a state can be any value that can be contained in a set. Each state
    assigned to a FSM must be unique. A FSM can only be in one state at a given
    time.

    Second, an event can be any value that can be contained in a set. Each
    event assigned to a FSM must be unique. Duplicates will be silently
    ignored.

    Third, a transition is a one-to-one mapping between a (state, event) pair
    and another state. You can define a circular transition that remains at the
    same state given an event. Transitions define what events trigger a FSM to
    move from one state to another.

    To define a new FSM, you can either subclass FSM (as seen in this module)
    or you can manually create a FSM object.

    Other FSM properties like actions are not supported. Users of a FSM must
    determine when to perform actions based on particular events.
    """

    def __init__(self, states, events):
        """
        Create a FSM given unique collections of states and events.

        Raises exception if states contain duplicates.
        """
        self.states = states
        self.events = events
        self.transitions = {}

    @property
    def edges(self):
        transitions = [(state0, self.transitions[(state0, event)]['state'], event)
                       for state0, event in self.transitions]
        return sorted(transitions, key=lambda t: t[2].value)

    def add_transition(self, state0, event, state1, data=None):
        """
        Add a transition to FSM.

        Arbitrary data can be attached so that a registered callback will
        receive this data when triggered by a state transition.

        Raises exception for invalid states and/or events.
        """
        assert state0 in self.states
        assert state1 in self.states
        assert event in self.events

        self.transitions[(state0, event)] = dict(state=state1, data=data)

    def is_valid(self, state, event):
        """
        Verify if state and event are a valid transition.
        """
        if state not in self.states:
            return False
        if event not in self.events:
            return False
        return (state, event) in self.transitions

    def peek(self, state, event):
        """
        Find the next valid state.

        Returns None if a state does not exist.
        """
        if not self.is_valid(state, event):
            return None
        return self.transitions[(state, event)]['state']

    def move(self, obj, event, callback=None):
        """
        Move given object to the next state and trigger callback if available.

        This method expects the given object to have a state attribute.

        The optional callback must take two parameters. The first parameter is
        the updated object. The second parameter is the arbitrary data attached
        when defining a transition. The callback will only be called after the
        object state has been saved.

        Returns boolean indicating whether the move was successful.
        """
        assert hasattr(obj, 'state'), "object does not contain a state attribute"

        state0 = obj.state
        if not self.is_valid(state0, event):
            return False
        obj.state = self.transitions[(state0, event)]['state']
        if callback is not None:
            callback(obj, self.transitions[(state0, event)]['data'])
        return True
