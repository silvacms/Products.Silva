# Copyright (c) 2002 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id: Image.py,v 1.26 2003/03/21 14:13:19 zagy Exp $

# Python
import re
from cStringIO import StringIO
from types import StringType, IntType
# Zope
import OFS
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from DateTime import DateTime
# Silva interfaces
from IAsset import IAsset
# Silva
import SilvaPermissions
from Asset import Asset
from File import cookPath
# misc
from helpers import add_and_edit

try:
    import PIL.Image
    havePIL = 1
except ImportError:
    havePIL = 0

try:
    from Products.ExtFile.ExtImage import ExtImage
except ImportError:  
    pass

icon = "www/silvaimage.gif"

class Image(Asset):
    """Web graphics (gif, jpg, png) can be uploaded and inserted in Silva
       documents.
    """    
    security = ClassSecurityInfo()

    meta_type = "Silva Image"

    __implements__ = IAsset
    
    re_WidthXHeight = re.compile(r'^([0-9]+)[Xx]([0-9]+)$')
    re_percentage = re.compile(r'^([0-9\.]+)\%$')

    hires_image = None
    web_scale = '100%'
    web_format = 'JPEG'
    web_formats = ('JPEG', 'GIF', 'PNG')
    
    def __init__(self, id, title):
        Image.inheritedAttribute('__init__')(self, id, title)
        self.image = None # should create default image

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'image')
    
    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'set_title')
    def set_title(self, title):
        """Set the title of the silva object.
        Overrides SilvaObject set_title() to accomodate the OFS.Image.Image 
        title attribute - which in turn is used in the tag() method.
        """
        self._title = title
        if self.image:
            # have to encode as otherwise unicode will blow up image rendering
            # code
            self.image.title = self.get_title_html()

    def set_web_presentation_properties(self, web_format, web_scale):
        """sets format and scaling for web presentation

            web_format (str): either JPEG or PNG (or whatever other format 
                makes sense, must be recognised by PIL)
            web_scale (str): WidthXHeight or nn.n%

            raises ValueError if web_scale cannot be parsed.

            automaticaly updates cached web presentation image
            
        """
        update_cache = 0
        if self.hires_image is None:
            update_cache = 1
            self.hires_image = self.image
            self.image = None
        if self.web_format != web_format:
            self.web_format = web_format
            update_cache = 1
        # check if web_scale can be parsed:
        canonical_scale = self.getCanonicalWebScale(web_scale)
        if self.web_scale != web_scale:
            update_cache = 1
            self.web_scale = web_scale
        if self.hires_image is not None and update_cache:
            self._createWebPresentation()
        
    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'set_image')
    def set_image(self, file):
        """Set the image object.
        """
        if self.hires_image is not None:
            self.hires_image.manage_beforeDelete(self.hires_image, self)
        self.hires_image = self._image_factory('hires_image', 
            self.get_title_html(), file)
        format = self.getFormat()
        if format in self.web_formats:
            self.web_format = format
        self._createWebPresentation()            

    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'set_zope_image')
    def set_zope_image(self, zope_img):
        """Set the image object with zope image.
        """
        self.hires_image = zope_img
        self._createWebPresentation()

    security.declareProtected(SilvaPermissions.View, 'getCanonicalWebScale')
    def getCanonicalWebScale(self, scale=None):
        """returns (width, height) of web image"""
        if scale is None:
            scale = self.web_scale
        m = self.re_WidthXHeight.match(scale)
        if m is None:
            m = self.re_percentage.match(scale)
            if m is None:
                raise ValueError, "'%s' is not a valid scale identifier" % (
                    scale, )
            percentage = float(m.group(1))/100.0
            width, height = self.getDimensions()
            width = int(width * percentage)
            height = int(height * percentage)
        else:
            width = int(m.group(1))
            height = int(m.group(2))
        return width, height            
   
    security.declareProtected(SilvaPermissions.View, 'getDimensions')
    def getDimensions(self):
        """returns width, heigt of (hi res) image
        
            raises ValueError if there is no way of determining the dimenstions
            return 0, 0 if there is no image
            returns width, height otherwise
        
        """
        img = self.hires_image
        if self.hires_image is None:
            img = self.image
        width, height = img.width, img.height
        if callable(width):
            width = width()
        if callable(height):
            height = height()
        if not (isinstance(width, IntType) and isinstance(height, IntType)):
            image = self._getPILImage()
            width, height = image.size
        return width, height            

    security.declareProtected(SilvaPermissions.View, 'getFormat')
    def getFormat(self):
        """returns image format (PIL identifier) or unknown if there is no PIL
        """
        try:
            return self._getPILImage().format
        except ValueError:
            return 'unknown'

    security.declareProtected(SilvaPermissions.View, 'getImage')
    def getImage(self, hires=1, webformat=0, REQUEST=None):
        """return image"""
        if hires and not webformat:
            image = self.hires_image
        elif not hires and webformat:
            image = self.image
        elif hires and webformat:
            pil_image = self._getPILImage()
            pil_image = self._prepareWebFormat(pil_image)
            image_data = StringIO()
            pil_image.save(image_data, self.web_format)
            del(pil_image)
            image = OFS.Image.Image('custom_image', self.get_title_html(), 
                image_data)
        elif not hires and not webformat:
            raise ValueError, "Low resolution image in original format is " \
                "not supported"
        if REQUEST is not None:                
            return image.index_html(REQUEST, REQUEST.RESPONSE)                
        else:
            return str(image.data)
        
    security.declareProtected(SilvaPermissions.View, 'canScale')
    def canScale(self):
        """returns if scaling/converting is possible"""
        return havePIL

    def _getPILImage(self):
        """return PIL of hi res image

            raise ValueError if no PIL is available
        """
        if not havePIL:
            raise ValueError, "No PIL installed."""
        img = self.hires_image
        if img is None:
            img = self.image
        if isinstance(img, OFS.Image.Image):
            image_reference = StringIO(str(img.data))
        else:            
            image_reference = img._get_filename(img.filename)
        try:
            image = PIL.Image.open(image_reference)
        except IOError:
            get_transaction().abort()
            raise
        return image

    def _createWebPresentation(self):
        width, height = self.getCanonicalWebScale()
        try:
            image = self._getPILImage()
        except ValueError:
            # XXX: warn the user, no scaling or converting has happend
            self.image = self.hires_image
            return    
        if self.web_scale == '100%' and image.format == self.web_format:
            self.image = self.hires_image
            return
        web_image_data = StringIO()
        web_image = image.resize((width, height), PIL.Image.BICUBIC)
        web_image = self._prepareWebFormat(web_image)
        web_image.save(web_image_data, self.web_format)
        self.image = OFS.Image.Image('image', self.get_title_html(), 
            web_image_data)

    def _prepareWebFormat(self, pil_image):
        """converts image's mode if necessary"""

        if pil_image.mode != 'RGB' and self.web_format == 'JPEG':
            pil_image = pil_image.convert("RGB")
        return pil_image                    

    def _image_factory(self, id, title, file):
        repository = self._useFSStorage()
        if repository is None:
            image = OFS.Image.Image(id, title, file)
        else:
            image = ExtImage(id, title)
            image._repository = repository
            image = image.__of__(self)
            image.manage_file_upload(file)
            image = image.aq_base
        return image        
    
    def _useFSStorage(self):
        """return true if we should store images on the filesystem"""
        service_files = getattr(self.get_root(), 'service_files', None)
        assert service_files is not None, "There is no service_files. " \
            "Refresh your silva root."
        if service_files.useFSStorage():
            return cookPath(service_files.filesystem_path())
        return None



InitializeClass(Image)
    
manage_addImageForm = PageTemplateFile("www/imageAdd", globals(),
                                       __name__='manage_addImageForm')

def manage_addImage(self, id, title, file=None, REQUEST=None):
    """Add an Image."""
    if not self.is_id_valid(id):
        return
    object = Image(id, title)
    self._setObject(id, object)
    object = getattr(self, id)

    if file:
        object.set_image(file)

    add_and_edit(self, id, REQUEST)
    return ''
