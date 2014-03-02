from django_fsm.db.fields import FSMField
from django_fsm.db.fields.fsmfield import FSMFieldDescriptor


class ManyTransitions(AttributeError):
    """Raised when AutoFSMField has too many transitions to choose from"""


class NoTransitions(AttributeError):
    """Raised when AutoFSMField can't find any matching transitions"""


class AutoFSMFieldDescriptor(FSMFieldDescriptor):
    """Descriptor for AutoFSMField"""

    def __set__(self, instance, value):
        """Find and fire the transition methods"""
        if not self.field.name in instance.__dict__:
            """Instance is just being created, it's not a value change"""
            instance.__dict__[self.field.name] = self.field.to_python(value)
            return

        new_value = self.field.to_python(value)
        old_value = self.field.to_python(instance.__dict__[self.field.name])
        if old_value == new_value:
            return

        if old_value is None:
            if self.field.default:
                """Try to change from default state if none is set"""
                try:
                    instance.__dict__[self.field.name] = self.field
                    self._find_and_run_transition(instance, new_value)
                except:
                    instance.__dict__[self.field.name] = None
                    raise
            else:
                """If there is no default, just set this value"""
                instance.__dict__[self.field.name] = new_value
        else:
            """Old value is available - just try to run a transition"""
            self._find_and_run_transition(instance, new_value)

    def _find_and_run_transition(self, instance, new_value):
        available_transitions = [
            t for t in self.field.transitions
            if t._django_fsm.next_state(instance) == new_value
            and t._django_fsm.conditions_met(instance)]
        if len(available_transitions) > 1:
            raise ManyTransitions(
                'Too many potential transitions for {}: {}'.format(
                    self.field, available_transitions))
        elif not available_transitions:
            raise NoTransitions('No transitions for {}'.format(self.field))
        else:
            available_transitions[0](instance)


class AutoFSMField(FSMField):
    """FSM field that runs transition functions on assignment"""

    descriptor_class = AutoFSMFieldDescriptor

    def __init__(self, *args, **kwargs):
        """Whine about `protected`"""
        if 'protected' in kwargs:
            raise ValueError(
                '"protected" kwarg is not supported by AutoFSMField"')
        super(AutoFSMField, self).__init__(*args, **kwargs)
