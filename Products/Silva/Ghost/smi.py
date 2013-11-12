# -*- coding: utf-8 -*-
# Copyright (c) 2013  Infrae. All rights reserved.
# See also LICENSE.txt

# Zope 3
from five import grok
from zeam.form import silva as silvaforms
from zeam.form.base.errors import Error
from zeam.form.base.widgets import widgetId
from zeam.component import getComponent

# Silva
from silva.core.conf.interfaces import IIdentifiedContent
from silva.core.interfaces import IGhost, IContent, IGhostManager
from silva.core.references.reference import Reference
from silva.core.references.reference import get_content_from_id
from silva.translations import translate as _


class IGhostSchema(IIdentifiedContent):

    haunted = Reference(
        IContent,
        title=_(u"Target"),
        description=_(u"The internal item the ghost is mirroring."),
        required=True)


def TargetValidator(field_name, wanted, adding=False):

    class Validator(object):

        def __init__(self, form, fields):
            self.form = form
            self.fields = fields

        def validate(self, data):
            """Validate ghost target before setting it.
            """
            # This is not beauty, but it works.
            content_id = data.get(field_name)
            if content_id is silvaforms.NO_VALUE:
                # If there value is required it is already checked
                return []
            getManager = getComponent((wanted,), IGhostManager)
            if adding:
                manager = getManager(container=self.form.context)
            else:
                manager = getManager(ghost=self.form.context)
            error = manager.validate(get_content_from_id(content_id), adding)
            if error is not None:
                identifier = widgetId(self.form, self.fields[field_name])
                return [Error(error.doc(), identifier)]
            return []

    return Validator


class GhostAddForm(silvaforms.SMIAddForm):
    """Add form for a ghost
    """
    grok.name(u"Silva Ghost")
    grok.context(IGhost)

    fields = silvaforms.Fields(IGhostSchema)
    fields['haunted'].referenceNotSetLabel = _(
        u"Click the Lookup button to select an item to haunt.")
    dataValidators = [TargetValidator('haunted', IContent, adding=True)]

    def _add(self, parent, data):
        factory = parent.manage_addProduct['Silva']
        return factory.manage_addGhost(
            data['id'], None, haunted=data['haunted'])


class GhostEditForm(silvaforms.SMIEditForm):
    """ Edit form for Ghost
    """
    grok.context(IGhost)
    fields = silvaforms.Fields(IGhostSchema).omit('id')
    dataValidators = [TargetValidator('haunted', IContent, adding=False)]
