# -*- coding: utf-8 -*-
# Copyright (c) 2002-2010 Infrae. All rights reserved.
# See also LICENSE.txt

from five import grok
from zope import schema
from zope.interface import Interface
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm

from Products.Silva.Asset import SMIAssetPortlet
from Products.Silva.Asset import AssetEditTab
from silva.ui.rest.container import ListingPreview
from silva.core.conf.interfaces import ITitledContent
from silva.core.interfaces import IImage
from silva.core.conf import schema as silvaschema
from silva.translations import translate as _
from zeam.form import silva as silvaforms
from zeam.form.base import NO_VALUE


class IImageAddFields(ITitledContent):
    image = silvaschema.Bytes(title=_(u"Image"), required=True)


class ImageAddForm(silvaforms.SMIAddForm):
    """Add form for an image.
    """
    grok.context(IImage)
    grok.name(u'Silva Image')

    fields = silvaforms.Fields(IImageAddFields)
    fields['id'].required = False

    def _add(self, parent, data):
        default_id = data['id'] is not NO_VALUE and data['id'] or u''
        factory = parent.manage_addProduct['Silva']
        return factory.manage_addImage(
            default_id, data['title'], file=data['image'])


class ImageEditForm(silvaforms.SMISubForm):
    """ Edit image attributes
    """
    grok.context(IImage)
    grok.view(AssetEditTab)
    grok.order(10)

    label = _(u'Edit')
    ignoreContent = False
    dataManager = silvaforms.SilvaDataManager

    fields = silvaforms.Fields(IImageAddFields).omit('id')
    actions  = silvaforms.Actions(silvaforms.CancelEditAction(),
                                  silvaforms.EditAction())

image_formats = SimpleVocabulary([SimpleTerm(title=u'jpg', value='JPEG'),
                                  SimpleTerm(title=u'png', value='PNG'),
                                  SimpleTerm(title=u'gif', value='GIF')])


class IFormatAndScalingFields(Interface):
    web_format = schema.Choice(
        source=image_formats,
        title=_(u"Web format"),
        description=_(u"Image format for web."))
    web_scale = schema.TextLine(
        title=_(u"Scaling"),
        description=_(u'Image scaling for web: use width x  '
                      u'height in pixels, or one axis length, ',
                      u'or a percentage (100x200, 100x*, *x200, 40%).'),
        required=False)
    web_crop = silvaschema.CropCoordinates(
        title=_(u"Cropping"),
        description=_(u"Image cropping for web: use the"
                      u" ‘set crop coordinates’ "
                      u"button, or enter X1xY1-X2xY2"
                      u" to define the cropping box."),
        required=False)


class ImageFormatAndScalingForm(silvaforms.SMISubForm):
    """ form to resize / change format of image.
    """
    grok.context(IImage)
    grok.view(AssetEditTab)
    grok.order(20)

    ignoreContent = False
    dataManager = silvaforms.SilvaDataManager

    label = _('Format and scaling')
    actions = silvaforms.Actions(silvaforms.CancelEditAction())
    fields = silvaforms.Fields(IFormatAndScalingFields)
    fields['web_format'].mode = 'radio'
    fields['web_scale'].defaultValue = '100%'

    @silvaforms.action(title=_('Change'),
                       implements=silvaforms.IDefaultAction)
    def set_properties(self):
        data, errors = self.extractData()
        if errors:
            return silvaforms.FAILURE
        try:
            self.context.set_web_presentation_properties(
                data.getWithDefault('web_format'),
                data.getWithDefault('web_scale'),
                data.getWithDefault('web_crop'))
        except ValueError as e:
            self.send_message(e.args[0], type='error')
            return silvaforms.FAILURE

        self.send_message(_('Scaling and/or format changed.'),
                          type='feedback')
        return silvaforms.SUCCESS


class InfoPortlet(SMIAssetPortlet):
    grok.context(IImage)
    grok.order(10)

    def update(self):
        self.format = self.context.web_format.lower()
        self.dimensions = None
        try:
            dimensions = self.context.get_dimensions()
            self.dimensions = dict(zip(['width', 'height'], dimensions))
        except ValueError:
            dimensions = None
        self.scaling = None
        if self.context.hires_image is not None:
            try:
                scaled_dimensions = self.context.get_canonical_web_scale()
                if scaled_dimensions != dimensions:
                    self.scaling = dict(
                        zip(['width', 'height'], scaled_dimensions))
            except ValueError:
                scaled_dimensions = None
        self.thumbnail = None
        if self.context.thumbnail_image:
            self.thumbnail = self.context.tag(thumbnail=1)
        self.original =self.context.url(hires=1)
        self.orientation = self.context.get_orientation()
        self.orientation_cls = unicode(self.orientation)


class ImageListingPreview(ListingPreview):
    grok.context(IImage)

    def preview(self):
        return self.context.tag(thumbnail=1)

