# -*- coding: utf-8 -*-
# Copyright (c) 2011 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$


from five import grok
from zope import schema
from zope.component import getUtility, getMultiAdapter
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm

from silva.core.conf.interfaces import ITitledContent
from silva.core.interfaces import IContainer, IFolder
from silva.core.services.interfaces import IContainerPolicyService
from silva.core.views import views as silvaviews
from silva.translations import translate as _
from zeam.form import silva as silvaforms


@grok.provider(IContextSourceBinder)
def silva_container_policy(context):
    contents = []
    policies = getUtility(IContainerPolicyService)
    for policy in policies.list_addable_policies(context):
        contents.append(SimpleTerm(
                value=policy,
                token=policy,
                title=policy))
    return SimpleVocabulary(contents)


class IContainerSchema(ITitledContent):
    """Add a select for the default item.
    """
    default_item = schema.Choice(
        title=_(u"first item"),
        description=_(u"Choose an item to be created within the container"),
        source=silva_container_policy,
        required=True)


class FolderAddForm(silvaforms.SMIAddForm):
    """Add form for a Folder.
    """
    grok.context(IFolder)
    grok.name(u'Silva Folder')

    fields = silvaforms.Fields(IContainerSchema)

    def _edit(self, parent, content, data):
        policies = getUtility(IContainerPolicyService)
        policy = policies.get_policy(data['default_item'])
        policy.createDefaultDocument(content, data['title'])


class ContainerView(silvaviews.View):
    """Default view for containers.
    """
    grok.context(IContainer)

    def render(self):
        default = self.context.get_default()
        if default is not None:
            return getMultiAdapter(
                (default, self.request), name="content.html")()
        return _(u'This container has no index.')


