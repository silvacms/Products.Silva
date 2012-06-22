# -*- coding: utf-8 -*-
# Copyright (c) 2002-2010 Infrae. All rights reserved.
# See also LICENSE.txt

import re
import logging
import mimetypes
from cStringIO import StringIO
from cgi import escape
import os.path

# Zope 3
from five import grok
from zope.component import getMultiAdapter, getUtility
from zope.event import notify
from zope.lifecycleevent import ObjectCreatedEvent
from zope.lifecycleevent.interfaces import IObjectMovedEvent

# Zope 2
from AccessControl import ClassSecurityInfo
from App.class_init import InitializeClass

# Silva
from Products.Silva import mangle, SilvaPermissions
from Products.Silva.Asset import Asset
from Products.Silva.MimetypeRegistry import mimetypeRegistry

from silva.core import conf as silvaconf
from silva.core import interfaces
from silva.core.interfaces import IMimeTypeClassifier
from silva.core.services.interfaces import IFilesService
from silva.translations import translate as _
from silva.core.views.interfaces import IContentURL, INonCachedLayer

try:
    from PIL import Image as PILImage
except ImportError:
    import Image as PILImage
havePIL = 1


logger = logging.getLogger('silva.image')


def validate_image(file):
    """Validate that file contains an image which is openable by PIL.
    """
    try:
        # Try to validate file format.
        file.seek(0)
        PILImage.open(file)
    except IOError, error:
        raise ValueError(error.args[-1].capitalize())
    # Come back at the begining..
    finally:
        file.seek(0)


def manage_addImage(context, identifier, title=None, file=None):
    """Add an Image.
    """
    if file is not None:
        validate_image(file)

    filename = None
    if hasattr(file, 'name'):
        filename = os.path.basename(file.name)
    identifier = mangle.Id(
        context, identifier or filename, file=file, interface=interfaces.IAsset)
    identifier.cook()
    if not identifier.isValid():
        raise ValueError(_(u"Invalid computed identifier."))
    identifier = str(identifier)
    if identifier in context.objectIds():
        raise ValueError(
            _(u"Duplicate id. Please provide an explicit id."))
    context._setObject(identifier, Image(identifier))
    content = context._getOb(identifier)
    if title is not None:
        content.set_title(title)
    if file is not None:
        content.set_image(file)
    notify(ObjectCreatedEvent(content))
    return content


from collections import namedtuple

Point = namedtuple('Point', ('x', 'y'))
SizeBase = namedtuple('SizeBase', ('width', 'height'))


class Format(object):

    JPEG = 'JPEG'
    PNG = 'PNG'
    GIF = 'GIF'


class Size(SizeBase):

    @classmethod
    def from_points(cls, p1, p2):
        return cls(abs(p1.x - p2.x), abs(p1.y - p2.y))

    @property
    def surface(self):
        return self.width * self.height

    def __lt__(self, other):
        return self.surface < other.surface

    def __lte__(self, other):
        return self.surface <= other.surface

    def __gt__(self, other):
        return self.surface > other.surface

    def __gte__(self, other):
        return self.surface >= other.surface


class Rect(object):

    _STR_RE = re.compile(r'^(?P<x1>[0-9]+)[Xx](?P<y1>[0-9]+)-(?P<x2>[0-9]+)[Xx](?P<y2>[0-9]+)')

    @classmethod
    def parse(cls, string):
        match = cls._STR_RE.match(string)
        if match:
            p1 = Point(int(match.group('x1')), int(match.group('y1')))
            p2 = Point(int(match.group('x2')), int(match.group('y2')))
            return cls.from_points(p1, p2)
        return None

    @classmethod
    def from_points(cls, p1, p2):
        lower_vertex = Point(min(p1.x, p2.x), min(p1.y, p2.y))
        higher_vertex = Point(max(p1.x, p2.x), max(p1.y, p2.y))
        return cls(lower_vertex, Size.from_points(lower_vertex, higher_vertex))

    def __init__(self, lower_edge, size):
        self.size = size
        self.lower_edge = lower_edge

    def to_string(self):
        higher_edge = self.higher_edge
        return "%dx%d-%dx%d" % (self.lower_edge.x, self.lower_edge.y,
                               higher_edge.x, higher_edge.y)

    @property
    def higher_edge(self):
        return Point(self.lower_edge.x + self.size.width,
                     self.lower_edge.y + self.size.height)


class Transformation(object):

    def validate(self):
        """Raise ValueError on failure.
        """
        pass

    def __call__(self, image):
        """Apply transformation on image and return new image
        if modified else False.
        """
        return False


def image_rect(image):
    x1, y1, x2, y2 = image.getbbox()
    return Rect.from_points(Point(x1, y1), Point(x2, y2))


class Crop(Transformation):

    def __init__(self, rect):
        self.rect = rect        

    def validate(self, image):
        rect = image_rect(image)
        if rect.size < self.rect.size:
            msg = _("'${crop}' defines an impossible cropping for the current image",
                    mapping={'crop': self.rect.to_string()})
            raise ValueError(msg)

    def __call__(self, image):
        cropbox = (self.rect.lower_edge.x,
                   self.rect.lower_edge.y,
                   self.rect.higher_edge.x,
                   self.rect.higher_edge.y)
        return image.crop(cropbox)


class Resize(Transformation):

    def __init__(self, spec):
        self.spec = spec

    def __call__(self, image):
        image_size = Size(*image.size)
        size = self.spec.get_size(image)
        if size == image_size:
            return False

        return image.resize((size.width, size.height), PILImage.ANTIALIAS)


class WebFormat(Transformation):

    def __init__(self, format):
        self.format = format

    def __call__(self, image):
        if self.format == Format.JPEG and image.mode != 'RGB':
            image.convert("RGB")
            return image
        return False


def save_image(image, format):
    data = StringIO()    
    image.save(data, format)
    data.seek(0)
    return data


class Transformer(object):

    def __init__(self, *transformations):
        self.transformations = list(transformations)

    def append(self, transform):
        self.transformations.append(transform)

    def transform(self, image, output_format, changed_on_format=False):
        pil_image = PILImageFactory(image)
        changed = False
        for transformation in self.transformations:
            new_image = transformation(pil_image)
            if new_image:
                changed = True
                pil_image = new_image

        if changed or (changed_on_format and
                       pil_image.format != output_format):
            return save_image(pil_image, output_format)
        return None


class ThumbnailResize(object):

    def __init__(self, size):
        self.size = size

    def __call__(self, image):
        image.thumbnail((self.size.width, self.size.height),
                        PILImage.ANTIALIAS)
        return image


class PercentResizeSpec(object):

    re_percentage = re.compile(r'^([0-9\.]+)\%$')

    @classmethod
    def parse(cls, string):
        match = cls.re_percentage.match(string)
        if match:
            try:
                return cls(float(match.group(1)))
            except (TypeError, ValueError):
                return None
        return None

    def __init__(self, percent):
        self.percent = percent

    def __eq__(self, other):
        if isinstance(other, PercentResizeSpec):
            return self.percent == other.percent
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def get_size(self, image):
        width, height = image.size
        return Size(int(width * self.percent / 100),
                    int(height * self.percent / 100))


class WHResizeSpec(object):
    
    re_WidthXHeight = re.compile(r'^([0-9]+|\*)[Xx]([0-9\*]+|\*)$')

    @classmethod
    def parse(cls, string):
        match = cls.re_WidthXHeight.match(string)
        width, height = (0, 0)
        if match:
            width = match.group(1)
            if width != '*':
                width = int(width)
            height = match.group(2)
            if height != '*':
                height = int(height)
            if '*' == width == height:
                return None
            return cls(width, height)
        return None

    def __init__(self, width, height):
        self.width = width
        self.height = height

    def __eq__(self, other):
        if isinstance(other, WHResizeSpec):
            return (self.width, self.height) == (other.width, other.height)
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def get_size(self, image):
        image_width, image_height = image.size
        width, height = (self.width, self.height)
        if width == '*':
            width = image_width
        if height == '*':
            height = image_height
        return Size(width, height)


def PILImageFactory(img):
    if img is None:
        raise ValueError("can't open None (PILImage)")
    image_reference = img.get_file_fd()
    try:
        image = PILImage.open(image_reference)
    except IOError, error:
        raise ValueError(error.args[-1].capitalize())
    return image


class Image(Asset):
    __doc__ = _("""Web graphics (gif, jpg, png) can be uploaded and inserted in
       documents, or used as viewable assets.
    """)
    security = ClassSecurityInfo()

    meta_type = "Silva Image"

    grok.implements(interfaces.IImage)

    re_WidthXHeight = re.compile(r'^([0-9]+|\*)[Xx]([0-9\*]+|\*)$')
    re_percentage = re.compile(r'^([0-9\.]+)\%$')
    re_box = re.compile(r'^([0-9]+)[Xx]([0-9]+)-([0-9]+)[Xx]([0-9]+)')

    thumbnail_size = Size(120, 120)

    image = None
    hires_image = None
    thumbnail_image = None
    web_scale = '100%'
    web_crop = ''
    web_format = Format.JPEG
    web_formats = (Format.JPEG, Format.GIF, Format.PNG)

    _web2ct = {
        Format.JPEG: 'image/jpeg',
        Format.GIF: 'image/gif',
        Format.PNG: 'image/png',
    }

    silvaconf.priority(-3)
    silvaconf.icon('www/silvaimage.gif')
    silvaconf.factory('manage_addImage')

    security.declareProtected(
        SilvaPermissions.ChangeSilvaContent, 'set_web_presentation_properties')
    def set_web_presentation_properties(self, web_format, web_scale, web_crop):
        """Sets format and scaling for web presentation.

        web_format (str): either JPEG or PNG (or whatever other format
        makes sense, must be recognised by PIL).
        web_scale (str): WidthXHeight or nn.n%.
        web_crop (str): X1xY1-X2xY2, crop-box or empty for no cropping.

        Raises ValueError if web_scale cannot be parsed.

        Automaticaly updates cached web presentation image.
        """
        update_cache = False
        if self.hires_image is None:
            update_cache = True
            self.hires_image = self.image
            self.image = None
        if web_format != 'unknown':
            if self.web_format != web_format and \
                    web_format in self.web_formats:
                self.web_format = web_format
                update_cache = True
        # check if web_scale can be parsed:
        self.get_canonical_web_scale(web_scale)
        if self.web_scale != web_scale:
            update_cache = True
            self.web_scale = web_scale
        # check if web_crop can be parsed:
        self.get_crop_box(web_crop)
        if self.web_crop != web_crop:
            update_cache = True
            # if web_crop is None it should be replaced by an empty string
            self.web_crop = web_crop and web_crop or ''
        if self.hires_image is not None and update_cache:
            self._create_derived_images()

    security.declareProtected(
        SilvaPermissions.ChangeSilvaContent, 'set_image')
    def set_image(self, file):
        """Set the image object.
        """
        validate_image(file)
        self._image_factory('hires_image', file)
        # Image change, reset scale, crop box: they can be invalid for
        # this new image.
        format = self.get_format()
        if format in self.web_formats:
            self.web_format = format
        self.web_scale = '100%'
        self.web_crop = ''
        self._create_derived_images()

        # XXX Should be on event
        self.update_quota()

    security.declareProtected(SilvaPermissions.View, 'get_image')
    def get_image(self, hires=True, webformat=False):
        """Return image data.
        """
        if hires and not webformat:
            image = self.hires_image
        elif not hires and webformat:
            image = self.image
        elif hires and webformat:
            transformer = Transformer(WebFormat(self.web_format))
            image_data = transformer.transform(self.hires_image,
                                               self.web_format,
                                               changed_on_format=True)
            if image_data:
                return image_data.getvalue()
            else:
                image = self.hires_image
        elif not hires and not webformat:
            raise ValueError(_(u"Low resolution image in original format is "
                               u"not supported"))
        return image.get_file()

    security.declareProtected(SilvaPermissions.View, 'get_canonical_web_scale')
    def get_canonical_web_scale(self, scale=None):
        """returns (width, height) of web image"""
        if scale is None:
            scale = self.web_scale
        m = self.re_WidthXHeight.match(scale)
        if m is None:
            m = self.re_percentage.match(scale)
            if m is None:
                msg = _("'${scale}' is not a valid scale identifier. "
                        "Probably a percent symbol is missing.",
                        mapping={'scale': scale})
                raise ValueError(msg)
            cropbox = Rect.parse(self.web_crop)
            if cropbox:
                width, height = cropbox.size
            else:
                width, height = self.get_dimensions()
            percentage = float(m.group(1))/100.0
            width = int(width * percentage)
            height = int(height * percentage)
        else:
            img_w, img_h = self.get_dimensions()
            width = m.group(1)
            height = m.group(2)
            if width == height == '*':
                msg = _("'${scale} is not a valid scale identifier. "
                        "At least one number is required.",
                        mapping={'scale': scale})
                raise ValueError(msg)
            if width == '*':
                height = int(height)
                width = img_w * height / img_h
            elif height == '*':
                width = int(width)
                height = img_h * width / img_w
            else:
                width = int(width)
        return width, height

    security.declareProtected(SilvaPermissions.View, 'get_crop_box')
    def get_crop_box(self, crop=None):
        """return crop box"""
        crop = crop or self.web_crop
        if crop is None or crop.strip() == '':
            return None
        rect = Rect.parse(crop)
        if rect is None:
            msg = _("'${crop} is not a valid crop identifier",
                    mapping={'crop': crop})
            raise ValueError(msg)
        image = PILImageFactory(self.hires_image)
        Crop(rect).validate(image)
        return (rect.lower_edge.x, rect.lower_edge.y,
                rect.higher_edge.x, rect.higher_edge.y)

    security.declareProtected(SilvaPermissions.View, 'get_dimensions')
    def get_dimensions(self, thumbnail=False, hires=False):
        """Returns width, heigt of (hi res) image.

        Raises ValueError if there is no way of determining the dimenstions,
        Return 0, 0 if there is no image,
        Returns width, height otherwise.
        """
        img = None
        if thumbnail:
            img = self.thumbnail_image
        elif hires:
            img = self.hires_image
        else:
            img = self.image

        if img is None:
            return (0, 0)
        try:
            return Size(*PILImageFactory(img).size)
        except (ValueError, TypeError):
            return Size(0, 0)

    security.declareProtected(SilvaPermissions.View, 'get_format')
    def get_format(self):
        """Returns image format.
        """
        return PILImageFactory(self.hires_image).format

    security.declareProtected(SilvaPermissions.View, 'tag')
    def tag(self, hires=False, thumbnail=False,
            request=None, preview=False, **extra_attributes):
        """ return xhtml tag

        Since 'class' is a Python reserved word, it cannot be passed in
        directly in keyword arguments which is a problem if you are
        trying to use 'tag()' to include a CSS class. The tag() method
        will accept a 'css_class' argument that will be converted to
        'class' in the output tag to work around this.
        """
        url = self.url(request=request,
                       preview=preview,
                       hires=hires,
                       thumbnail=thumbnail)

        title = self.get_title_or_id()
        width, height = self.get_dimensions(thumbnail=thumbnail, hires=hires)
        if extra_attributes.has_key('css_class'):
            extra_attributes['class'] = extra_attributes['css_class']
            del extra_attributes['css_class']

        extra_html_attributes = [
            '{name}="{value}"'.format(name=escape(name, 1),
                                      value=escape(value, 1))
            for name, value in extra_attributes.iteritems()]

        return '<img src="{src}" width="{width}" height="{height}" ' \
               'alt="{alt}" {extra_attributes} />'.format(
                    src=url,
                    width=str(width),
                    height=str(height),
                    alt=escape(title, 1),
                    extra_attributes=" ".join(extra_html_attributes))

    security.declareProtected(SilvaPermissions.View, 'url')
    def url(self, hires=False, thumbnail=False, request=None, preview=False):
        "return url of image"
        request = request or self.REQUEST
        url = getMultiAdapter(
            (self, request), IContentURL).url(preview=preview)
        if hires:
            url += '?hires'
        elif thumbnail:
            url += '?thumbnail'
        return url

    security.declareProtected(SilvaPermissions.View, 'get_web_format')
    def get_web_format(self):
        """Return file format of web presentation image
        """
        try:
            return PILImageFactory(self.image).format
        except (ValueError, TypeError):
            # XXX i18n - should we translate this?
            return 'unknown'

    security.declareProtected(SilvaPermissions.View, 'get_web_scale')
    def get_web_scale(self):
        """Return scale percentage / WxH of web presentation image
        """
        return str(self.web_scale)

    security.declareProtected(SilvaPermissions.View, 'get_web_crop')
    def get_web_crop(self):
        """Return crop identifier
        """
        return str(self.web_crop)

    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
        'get_file_system_path')
    def get_file_system_path(self):
        """return path on filesystem for containing image"""
        return self.hires_image.get_file_system_path()

    security.declareProtected(SilvaPermissions.View, 'get_orientation')
    def get_orientation(self):
        """Returns translated Image orientation (string).
        """
        width, height = self.get_dimensions()
        if width == height:
            return _("square")
        elif width > height:
            return _("landscape")
        return _("portrait")

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'get_filename')
    def get_filename(self):
        if self.image is None:
            return self.getId()
        return self.image.get_filename()

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'get_mime_type')
    def get_mime_type(self):
        if self.image is None:
            return 'application/octet-stream'
        return self.image.get_mime_type()

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'get_content_type')
    def get_content_type(self):
        if self.image is None:
            return 'application/octet-stream'
        return self.image.get_content_type()

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'get_file_size')
    def get_file_size(self):
        if self.image is None:
            return 0
        return self.image.get_file_size()

    ##########
    ## private

    def _create_derived_images(self):
        self._create_web_presentation()
        self._create_thumbnail()

    def _create_web_presentation(self):
        try:
            transformer = Transformer()
            cropbox = self.get_crop_box()
            if cropbox is not None:
                crop_rect = Rect.from_points(Point(cropbox[0], cropbox[1]),
                                             Point(cropbox[2], cropbox[3]))
                transformer.append(Crop(crop_rect))

            if self.web_scale != '100%':
                spec = WHResizeSpec.parse(self.web_scale)
                if spec is None:
                    spec = PercentResizeSpec.parse(self.web_scale)
                if spec is not None:
                    transformer.append(Resize(spec))

            transformer.append(WebFormat(self.web_format))
            image_io = transformer.transform(self.hires_image,
                                             self.web_format)
            if image_io:
                ct = self._web2ct[self.web_format]
                self._image_factory('image', image_io, ct)
            else:
                self.image = self.hires_image
        except ValueError, e:
            logger.info("Web presentation creation failed for %s with %s" %
                        ('/'.join(self.getPhysicalPath()), str(e)))
            self.image = self.hires_image
            return
        except IOError, e:
            logger.info("Web presentation creation failed for %s with %s" %
                        ('/'.join(self.getPhysicalPath()), str(e)))
            if str(e.args[0]) == "cannot read interlaced PNG files":
                self.image = self.hires_image
                return
            else:
                raise ValueError(str(e))

    def _create_thumbnail(self):
        try:
            transformer = Transformer(ThumbnailResize(self.thumbnail_size),
                                      WebFormat(self.web_format))
            thumb = transformer.transform(self.image or self.hires_image,
                                          self.web_format)
            if thumb:
                ct = self._web2ct[self.web_format]
                self._image_factory('thumbnail_image', thumb, ct)
        except IOError, e:
            logger.info("Thumbnail creation failed for %s with %s" %
                        ('/'.join(self.getPhysicalPath()), str(e)))
            if str(e.args[0]) == "cannot read interlaced PNG files":
                self.thumbnail_image = None
                return
            else:
                raise ValueError(str(e))
        except ValueError, e:
            logger.info("Thumbnail creation failed for %s with %s" %
                        ('/'.join(self.getPhysicalPath()), str(e)))
            # no thumbnail
            self.thumbnail_image = None
            return

    def _image_factory(self, image_id, image_file, content_type=None):
        service_files = getUtility(IFilesService)
        new_image = service_files.new_file(image_id)
        setattr(self, image_id, new_image)
        new_image = getattr(self, image_id)
        new_image.set_file(image_file)
        if content_type is not None:
            new_image.set_content_type(content_type)
        getUtility(IMimeTypeClassifier).guess_filename(new_image, self.getId())
        return new_image

    def _image_is_hires(self):
        return (self.image is not None and
                self.image.aq_base is self.hires_image.aq_base)


InitializeClass(Image)


# Management helpers

class ImageStorageConverter(object):
    """Convert image storage.
    """
    grok.implements(interfaces.IUpgrader)

    def __init__(self, service):
        self.service = service

    def validate(self, image):
        if not interfaces.IImage.providedBy(image):
            return False
        if image.hires_image is None:
            logger.error(
                "No orginal data for %s, storage not changed." %
                '/'.join(image.getPhysicalPath()))
            return False
        if self.service.is_file_using_correct_storage(image.hires_image):
            # don't convert that are already correct
            return False
        return True

    def upgrade(self, image):
        image_file = image.hires_image
        content_type = image_file.get_mime_type()
        data = image_file.get_file_fd()
        image._image_factory('hires_image', data, content_type)
        image._create_derived_images()
        logger.info(
            "Storage for image %s converted" %
            '/'.join(image.getPhysicalPath()))
        return image


for mimetype in mimetypes.types_map.values():
    if mimetype.startswith('image'):
        mimetypeRegistry.register(mimetype, manage_addImage, 'Silva')


def image_factory(self, id, content_type, file):
    """Create an Image.
    """
    filename = None
    if hasattr(file, 'name'):
        filename = os.path.basename(file.name)
    id = mangle.Id(self, id or filename,
        file=file, interface=interfaces.IAsset)
    id.cook()
    if not id.isValid():
        return None
    img = Image(str(id)).__of__(self)
    return img


@grok.subscribe(interfaces.IImage, IObjectMovedEvent)
def image_added(image, event):
    if image is not event.object or event.newName is None:
        return
    guess_filename = getUtility(IMimeTypeClassifier).guess_filename
    for file_id in ('hires_image', 'image', 'thumbnail_image'):
        image_file = getattr(image, file_id, None)
        if image_file is None:
            continue
        guess_filename(image_file, event.newName)

