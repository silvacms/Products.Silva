# -*- coding: utf-8 -*-
# Copyright (c) 2011-2013 Infrae. All rights reserved.
# See also LICENSE.txt


from five import grok
from zope import schema
from zope.component import getUtility, queryMultiAdapter
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm

from silva.core.conf.interfaces import ITitledContent
from silva.core.interfaces import IContainer, IFolder
from silva.core.services.interfaces import IContainerPolicyService
from silva.core.views import views as silvaviews
from silva.core.views.interfaces import IView
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
        title=_(u"First item"),
        description=_(u"Choose an item to be created within the container."),
        source=silva_container_policy,
        required=True)


class FolderAddForm(silvaforms.SMIAddForm):
    """Add form for a Folder.
    """
    grok.context(IFolder)
    grok.name(u'Silva Folder')

    fields = silvaforms.Fields(IContainerSchema)
    # Prevent to call a folder index.
    fields['id'].validateForInterface = IFolder

    def _edit(self, parent, content, data):
        policies = getUtility(IContainerPolicyService)
        policy = policies.get_policy(data['default_item'])
        policy.createDefaultDocument(content, data['title'])


class ContainerView(silvaviews.View):
    """Default view for containers.
    """
    grok.context(IContainer)
    unavailable_message = _(u'This container has no index.')

    def render(self):
        default = self.context.get_default()
        if default is None:
            return self.unavailable_message
        view = queryMultiAdapter((default, self.request), name="content.html")
        if view is None:
            return self.unavailable_message
        if IView.providedBy(view) and view.content is None:
            return self.unavailable_message
        return view()


