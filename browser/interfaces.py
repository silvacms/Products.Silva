# Copyright (c) 2008-2009 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$


from zope.interface import Attribute, Interface
from zope.publisher.interfaces.browser import IBrowserView
from zope.viewlet.interfaces import IViewlet, IViewletManager

class ISMITab(IBrowserView):
    """A management tab in Silva management interface.
    """

    # XXX: Should use __name__ when SMI tab will be real views.
    tab_name = Attribute("Name of the current tab.")


class IEditTab(ISMITab):
    """Edit tab.
    """


class IAccessTab(ISMITab):
    """Access tab.
    """


class IGroupEditTab(IAccessTab):
    """Group edit tab.
    """


class IPropertiesTab(ISMITab):
    """Properties tab.
    """


class IPreviewTab(ISMITab):
    """Preview tab.
    """


class ISMIButtonManager(IViewletManager):
    """Where SMI button apprears.
    """


class ISMIButton(IViewlet):
    """A button which appears at the top of the management tab.
    """

    def available():
        """Is that button available ?
        """

    label = Attribute("Label of the button")
    tab = Attribute("Where does the button link to")
    accesskey = Attribute("Access key")
    help = Attribute("Description of the button")


class ISMISpecialButton(Interface):
    """A special button.
    """


class ISMIExecutorButton(ISMIButton, ISMISpecialButton):
    """This button executes a special action.
    """


