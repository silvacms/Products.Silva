from five import grok

from silva.core import interfaces
from Products.SilvaMetadata.Index import MetadataCatalogingAttributes


class CatalogingAttributes(MetadataCatalogingAttributes):
    grok.context(interfaces.ISilvaObject)

    @property
    def version_status(self):
        return 'public'


class CatalogingAttributesPublishable(CatalogingAttributes):
    grok.context(interfaces.IPublishable)

    @property
    def version_status(self):
        if self.context.is_published():
            return 'public'
        else:
            return 'unapproved'


class CatalogingAttributesVersion(CatalogingAttributes):
    grok.context(interfaces.IVersion)

    @property
    def version_status(self):
        """Returns the status of the current version
        Can be 'unapproved', 'approved', 'public', 'last_closed' or 'closed'
        """
        status = None
        unapproved_version = self.context.get_unapproved_version(0)
        approved_version = self.context.get_approved_version(0)
        public_version = self.context.get_public_version(0)
        previous_versions = self.context.get_previous_versions()
        if unapproved_version and unapproved_version == self.context.id:
            status = "unapproved"
        elif approved_version and approved_version == self.context.id:
            status = "approved"
        elif public_version and public_version == self.context.id:
            status = "public"
        else:
            if previous_versions and previous_versions[-1] == self.context.id:
                status = "last_closed"
            elif self.context.id in previous_versions:
                status = "closed"
            else:
                # this is a completely new version not even registered
                # with the machinery yet
                status = 'unapproved'
        return status

