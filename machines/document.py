from enums import UniqueIntEnum
from fsm import FSM
from registry import register


class DocumentState(UniqueIntEnum):
    Draft = 1
    Validating = 2
    Validated = 3
    Approval = 4
    Approved = 5
    Publishing = 6
    Published = 7

    @classmethod
    def default(cls):
        return cls.Draft


class DocumentEvent(UniqueIntEnum):
    Submit = 1
    Continue = 2
    Cancel = 3
    Recall = 4
    Disapprove = 5
    Approve = 6
    Publish = 7


class DocumentFSM(FSM):
    """
    A FSM implementation for a document workflow.

    States are enumerated values as defined by the UniqueIntEnum class. See
    DocumentState class for full enumerated values.
    """

    def __init__(self):
        super(DocumentFSM, self).__init__(DocumentState, DocumentEvent)

        self.add_transition(DocumentState.Draft,
                            DocumentEvent.Submit,
                            DocumentState.Validating)

        self.add_transition(DocumentState.Validating,
                            DocumentEvent.Continue,
                            DocumentState.Validated)

        self.add_transition(DocumentState.Validating,
                            DocumentEvent.Cancel,
                            DocumentState.Draft)

        self.add_transition(DocumentState.Validated,
                            DocumentEvent.Continue,
                            DocumentState.Approval)

        self.add_transition(DocumentState.Validated,
                            DocumentEvent.Recall,
                            DocumentState.Draft)

        self.add_transition(DocumentState.Approval,
                            DocumentEvent.Recall,
                            DocumentState.Draft)

        self.add_transition(DocumentState.Approval,
                            DocumentEvent.Disapprove,
                            DocumentState.Draft)

        self.add_transition(DocumentState.Approval,
                            DocumentEvent.Approve,
                            DocumentState.Approved)

        self.add_transition(DocumentState.Approved,
                            DocumentEvent.Recall,
                            DocumentState.Draft)

        self.add_transition(DocumentState.Approved,
                            DocumentEvent.Publish,
                            DocumentState.Publishing)

        self.add_transition(DocumentState.Publishing,
                            DocumentEvent.Cancel,
                            DocumentState.Approved)

        self.add_transition(DocumentState.Publishing,
                            DocumentEvent.Continue,
                            DocumentState.Published)


@register
class Document(object):
    __clsid__ = 'documents'

    def __init__(self):
        self.fsm = DocumentFSM()
        self._state = self.fsm.states.default()

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value):
        self._state = value
