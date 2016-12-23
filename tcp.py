import time

from enums import UniqueIntEnum
from fsm import FSM


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
        super(ConnectionFSM, self).__init__(list(ConnectionState))

        event_close = self.add_event(ConnectionEvent.Close)
        event_connect = self.add_event(ConnectionEvent.Connect)
        event_listen = self.add_event(ConnectionEvent.Listen)
        event_receive_ack = self.add_event(ConnectionEvent.ACK)
        event_receive_fin = self.add_event(ConnectionEvent.FIN)
        event_receive_fin_ack = self.add_event(ConnectionEvent.FinAck)
        event_receive_rst = self.add_event(ConnectionEvent.RST)
        event_receive_syn = self.add_event(ConnectionEvent.SYN)
        event_receive_syn_ack = self.add_event(ConnectionEvent.SynAck)
        event_send = self.add_event(ConnectionEvent.Send)
        event_timeout = self.add_event(ConnectionEvent.Timeout)

        self.add_transition(ConnectionState.Closed,
                            event_listen,
                            ConnectionState.Listen)

        self.add_transition(ConnectionState.Listen,
                            event_receive_syn,
                            ConnectionState.SynReceived)

        self.add_transition(ConnectionState.Listen,
                            event_send,
                            ConnectionState.SynSent)

        self.add_transition(ConnectionState.SynReceived,
                            event_receive_rst,
                            ConnectionState.Listen)

        self.add_transition(ConnectionState.SynReceived,
                            event_receive_ack,
                            ConnectionState.Established)

        self.add_transition(ConnectionState.SynReceived,
                            event_close,
                            ConnectionState.FinWait1)

        self.add_transition(ConnectionState.SynReceived,
                            event_timeout,
                            ConnectionState.Closed)

        self.add_transition(ConnectionState.Closed,
                            event_connect,
                            ConnectionState.SynSent)

        self.add_transition(ConnectionState.SynSent,
                            event_close,
                            ConnectionState.Closed)

        self.add_transition(ConnectionState.SynSent,
                            event_timeout,
                            ConnectionState.Closed)

        self.add_transition(ConnectionState.SynSent,
                            event_receive_syn,
                            ConnectionState.SynReceived)

        self.add_transition(ConnectionState.SynSent,
                            event_receive_syn_ack,
                            ConnectionState.Established)

        self.add_transition(ConnectionState.Established,
                            event_close,
                            ConnectionState.FinWait1)

        self.add_transition(ConnectionState.FinWait1,
                            event_receive_ack,
                            ConnectionState.FinWait2)

        self.add_transition(ConnectionState.FinWait2,
                            event_receive_fin,
                            ConnectionState.TimeWait)

        self.add_transition(ConnectionState.FinWait1,
                            event_receive_fin_ack,
                            ConnectionState.TimeWait)

        self.add_transition(ConnectionState.FinWait1,
                            event_receive_fin,
                            ConnectionState.Closing)

        self.add_transition(ConnectionState.Closing,
                            event_receive_ack,
                            ConnectionState.TimeWait)

        self.add_transition(ConnectionState.Established,
                            event_receive_fin,
                            ConnectionState.CloseWait)

        self.add_transition(ConnectionState.CloseWait,
                            event_close,
                            ConnectionState.LastAck)

        self.add_transition(ConnectionState.LastAck,
                            event_receive_ack,
                            ConnectionState.Closed)

        self.add_transition(ConnectionState.TimeWait,
                            event_timeout,
                            ConnectionState.Closed)


class Connection(object):
    def __init__(self):
        self._state = ConnectionState.default()
        self.fsm = ConnectionFSM()

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
