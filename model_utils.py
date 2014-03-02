from django.db.models import Manager


def manager_from_qs(qs, bases=()):
    """Creates a Django Manager subclass with get_query_set returning `qs`"""
    def contribute_to_class(self, cls, name=None):
        """Throw a more meaningful exception when user forgets to instatiate
        the returned manager"""
        nonlocal manager
        if not isinstance(self, Manager):
            raise TypeError(
                "contribute_to_class should only be used with "
                "*instances* of Manager. "
                "Have you forgot the () in objects = manager_from_qs({})()?"
                .format(qs.__name__))
        return super(manager, self).contribute_to_class(cls, name)
    manager = type('QuerySetManager', bases + (Manager, ), {
        'get_query_set': lambda self: qs(self.model, using=self._db),
        'contribute_to_class': contribute_to_class,
        '__getattr__': lambda self, attr, **kw: getattr(self.get_query_set(),
                                                        attr, **kw),
    })
    return manager
