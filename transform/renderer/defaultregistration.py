try:
    import libxslt
    import libxml2
    NO_XSLT = False
except ImportError:
    NO_XSLT = True
 
from Products.Silva.transform.rendererreg import getRendererRegistry

def registerDefaultRenderers():

    # don't register XSLT related renderers if no XSLT is installed
    if NO_XSLT:
        return
    
    from Products.Silva.transform.renderer.imagesonrightrenderer import\
         ImagesOnRightRenderer
    from Products.Silva.transform.renderer.basicxsltrenderer import\
         BasicXSLTRenderer
    from Products.Silva.transform.renderer.notitlerenderer import\
         NoTitleRenderer
    
    reg = getRendererRegistry()
    
    reg.registerRenderer(
        'Silva Document',
        'Basic XSLT Renderer',
        BasicXSLTRenderer())

    reg.registerRenderer(
        'Silva Document',
        'Without Title Renderer (Same as basic but without the document title)',
        NoTitleRenderer())
        
    reg.registerRenderer(
        'Silva Document', 
        'Images on Right',
        ImagesOnRightRenderer())
