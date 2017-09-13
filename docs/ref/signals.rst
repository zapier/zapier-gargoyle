Signals
=======

.. currentmodule:: gargoyle.signals

.. data:: gargoyle.signals.switch_added
    :noindex:

    This signal is sent when a switch is added (similar to Django's ``post_save``, when created is ``True``).

    Example subscriber:

    .. code-block:: python

        def switch_added_callback(sender, request, switch, **extra):
            logging.debug('Switch was added: %r', switch.label)

        from gargoyle.signals import switch_added
        switch_added.connect(switch_added_callback)

.. data:: gargoyle.signals.switch_deleted
    :noindex:

    This signal is sent when a switch is deleted (similar to Django's ``post_delete``).

    Example subscriber:

    .. code-block:: python

        def switch_deleted_callback(sender, request, switch, **extra):
            logging.debug('Switch was deleted: %r', switch.label)

        from gargoyle.signals import switch_deleted
        switch_deleted.connect(switch_deleted_callback)

.. data:: gargoyle.signals.switch_updated
    :noindex:

    This signal is sent when a switch is updated (similar to Django's ``post_save``, when created is ``False``).

    Example subscriber:

    .. code-block:: python

        def switch_updated_callback(sender, request, switch, **extra):
            logging.debug('Switch was updated: %r', switch.label)

        from gargoyle.signals import switch_updated
        switch_updated.connect(switch_updated_callback)

.. data:: gargoyle.signals.switch_status_updated
    :noindex:

    This signal is sent when a condition is updated in a switch.

    Example subscriber:

    .. code-block:: python

        def switch_status_updated_callback(sender, request, switch, status, **extra):
            logging.debug('Switch has updated status: %r; %r', switch.label, status)

        from gargoyle.signals import switch_status_updated
        switch_status_updated.connect(switch_status_updated_callback)

.. data:: gargoyle.signals.switch_condition_added
    :noindex:

    This signal is sent when a condition is added to a switch.

    Example subscriber:

    .. code-block:: python

        def switch_condition_added_callback(sender, request, switch, condition, **extra):
            logging.debug('Switch has new condition: %r; %r', switch.label, condition)

        from gargoyle.signals import switch_condition_added
        switch_condition_added.connect(switch_condition_added_callback)

.. data:: gargoyle.signals.switch_condition_deleted
    :noindex:

    This signal is sent when a condition is removed from a switch.

    Example subscriber:

    .. code-block:: python

        def switch_condition_deleted_callback(sender, request, switch, condition, **extra):
            logging.debug('Switch has deleted condition: %r; %r', switch.label, condition)

        from gargoyle.signals import switch_condition_deleted
        switch_condition_deleted.connect(switch_condition_deleted_callback)
