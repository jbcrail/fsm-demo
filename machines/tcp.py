import time

from enums import UniqueIntEnum
from fsm import FSM
from registry import register


class ConnectionState(UniqueIntEnum):
    Closed = 1
    Listen = 2
    SynReceived = 3
    SynSent = 4
    Established = 5
    FinWait1 = 6
    FinWait2 = 7
    CloseWait = 8
    LastAck = 9
    Closing = 10
    TimeWait = 11

    @classmethod
    def default(cls):
        return cls.Closed


class ConnectionEvent(UniqueIntEnum):
    Connect = 1
    Listen = 2
    RST = 3
    SYN = 4
    ACK = 5
    FIN = 6
    SynAck = 7
    FinAck = 8
    Send = 9
    Close = 10
    Timeout = 11


class ConnectionFSM(FSM):
    """
    A FSM implementation for a TCP connection.

    States are enumerated values as defined by the UniqueIntEnum class. See
    ConnectionState class for full enumerated values.

    Based on https://en.wikipedia.org/wiki/Transmission_Control_Protocol#/media/File:Tcp_state_diagram_fixed_new.svg
    """

    def __init__(self):
        super(ConnectionFSM, self).__init__(ConnectionState, ConnectionEvent)

        self.add_transition(ConnectionState.Closed,
                            ConnectionEvent.Listen,
                            ConnectionState.Listen)

        self.add_transition(ConnectionState.Listen,
                            ConnectionEvent.SYN,
                            ConnectionState.SynReceived)

        self.add_transition(ConnectionState.Listen,
                            ConnectionEvent.Send,
                            ConnectionState.SynSent)

        self.add_transition(ConnectionState.SynReceived,
                            ConnectionEvent.RST,
                            ConnectionState.Listen)

        self.add_transition(ConnectionState.SynReceived,
                            ConnectionEvent.ACK,
                            ConnectionState.Established)

        self.add_transition(ConnectionState.SynReceived,
                            ConnectionEvent.Close,
                            ConnectionState.FinWait1)

        self.add_transition(ConnectionState.SynReceived,
                            ConnectionEvent.Timeout,
                            ConnectionState.Closed)

        self.add_transition(ConnectionState.Closed,
                            ConnectionEvent.Connect,
                            ConnectionState.SynSent)

        self.add_transition(ConnectionState.SynSent,
                            ConnectionEvent.Close,
                            ConnectionState.Closed)

        self.add_transition(ConnectionState.SynSent,
                            ConnectionEvent.Timeout,
                            ConnectionState.Closed)

        self.add_transition(ConnectionState.SynSent,
                            ConnectionEvent.SYN,
                            ConnectionState.SynReceived)

        self.add_transition(ConnectionState.SynSent,
                            ConnectionEvent.SynAck,
                            ConnectionState.Established)

        self.add_transition(ConnectionState.Established,
                            ConnectionEvent.Close,
                            ConnectionState.FinWait1)

        self.add_transition(ConnectionState.FinWait1,
                            ConnectionEvent.ACK,
                            ConnectionState.FinWait2)

        self.add_transition(ConnectionState.FinWait2,
                            ConnectionEvent.FIN,
                            ConnectionState.TimeWait)

        self.add_transition(ConnectionState.FinWait1,
                            ConnectionEvent.FinAck,
                            ConnectionState.TimeWait)

        self.add_transition(ConnectionState.FinWait1,
                            ConnectionEvent.FIN,
                            ConnectionState.Closing)

        self.add_transition(ConnectionState.Closing,
                            ConnectionEvent.ACK,
                            ConnectionState.TimeWait)

        self.add_transition(ConnectionState.Established,
                            ConnectionEvent.FIN,
                            ConnectionState.CloseWait)

        self.add_transition(ConnectionState.CloseWait,
                            ConnectionEvent.Close,
                            ConnectionState.LastAck)

        self.add_transition(ConnectionState.LastAck,
                            ConnectionEvent.ACK,
                            ConnectionState.Closed)

        self.add_transition(ConnectionState.TimeWait,
                            ConnectionEvent.Timeout,
                            ConnectionState.Closed)


@register
class Connection(object):
    __clsid__ = 'connections'

    def __init__(self):
        self.fsm = ConnectionFSM()
        self._state = self.fsm.states.default()

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value):
        self._state = value

    def connect(self):
        assert self.fsm.move(self, ConnectionEvent.Connect)

    def listen(self):
        assert self.fsm.move(self, ConnectionEvent.Listen)

    def wait_for_syn(self):
        time.sleep(1)
        assert self.fsm.move(self, ConnectionEvent.SYN)

    def wait_for_ack(self):
        time.sleep(1)
        assert self.fsm.move(self, ConnectionEvent.ACK)

    def wait_for_syn_ack(self):
        time.sleep(1)
        assert self.fsm.move(self, ConnectionEvent.SynAck)

    def wait_for_fin(self):
        time.sleep(1)
        assert self.fsm.move(self, ConnectionEvent.FIN)

    def close(self):
        assert self.fsm.move(self, ConnectionEvent.Close)

    def wait_for_close(self):
        self.wait_for_ack()
        self.wait_for_fin()
        self.wait_for_timeout()

    def wait_for_timeout(self):
        time.sleep(1)
        assert self.fsm.move(self, ConnectionEvent.Timeout)
