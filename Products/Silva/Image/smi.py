# -*- coding: utf-8 -*-
# Copyright (c) 2002-2013 Infrae. All rights reserved.
# See also LICENSE.txt

from five import grok
from zope import schema
from zope.component import getMultiAdapter
from zope.interface import Interface
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from zope.event import notify
from zope.lifecycleevent import ObjectModifiedEvent

from Products.Silva.Asset import AssetEditTab
from Products.Silva.Asset import SMIAssetPortlet
from silva.core.conf import schema as silvaschema
from silva.core.conf.interfaces import ITitledContent
from silva.core.interfaces import IImage
from silva.core.smi.preview import Preview
from silva.translations import translate as _
from silva.ui.rest import PageREST
from silva.ui.rest.container import ListingPreview
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
    fields['id'].validateForInterface = IImage
    fields['image'].fileNotSetLabel = _(
        u"Click the Upload button to select an image.")

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
    fields['image'].fileSetLabel = _(
        u"Click the Upload button to replace the current image with a new image.")
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
                      u'height in pixels, or one axis length, '
                      u'or a percentage (100x200, 100x*, *x200, 40%).'
                      u'Use 100% to scale back to the orginal format.'),
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

    @silvaforms.action(
        title=_(u'Change'),
        description=_(u'Scale and/or crop the image with the new settings'),
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

        notify(ObjectModifiedEvent(self.context))
        self.send_message(_('Scaling and/or format changed.'),
                          type='feedback')
        return silvaforms.SUCCESS


class InfoPortlet(SMIAssetPortlet):
    grok.context(IImage)
    grok.order(10)

    def update(self):
        self.thumbnail = None
        self.dimensions = None
        self.original_available = False
        self.original_dimensions = None
        self.web_format = self.context.web_format.lower()
        dimensions = self.context.get_dimensions(hires=False)
        if dimensions != (0, 0):
            self.dimensions = dict(zip(['width', 'height'], dimensions))

        if self.context.hires_image is not None:
            self.original_available = True
            original_dimensions = self.context.get_dimensions(hires=True)
            if original_dimensions not in (dimensions, (0, 0)):
                self.original_dimensions = dict(
                    zip(['width', 'height'], original_dimensions))

        if self.context.thumbnail_image:
            self.thumbnail = self.context.tag(request=self.request,
                                              preview=True,
                                              thumbnail=True)

        self.orientation = self.context.get_orientation()
        self.orientation_cls = unicode(self.orientation)


class ImageHiresPreview(PageREST):
    grok.adapts(Preview, IImage)
    grok.name('hires')
    grok.require('silva.ReadSilvaContent')

    def payload(self):
        content = getMultiAdapter(
            (self.context, self.request), name='content.html')
        content.hires = True
        return {"ifaces": ["preview"],
                "html": content()}


class ImageListingPreview(ListingPreview):
    grok.context(IImage)

    def preview(self):
        return self.context.tag(thumbnail=1)

