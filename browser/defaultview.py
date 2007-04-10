from zope import component
from zope import interface
from zope.app.pagetemplate import ViewPageTemplateFile

from Products.Five import BrowserView

def get_view(context, request, name='index.html'):
    return component.queryMultiAdapter((context, request), name=name)

class Default(BrowserView):
    def __call__(self):
        # Try to look up a default view on the version first, if any
        viewable = self.context.get_viewable()
        if viewable is None:
            return BlankView(self.context, self.request).__of__(self.context)()
        
        if viewable.aq_base is not self.context.aq_base:
            view = get_view(viewable, self.request)
            if view is not None:
                return view()
        return getattr(self.context, 'index_html')()

class BlankView(BrowserView):
    template = ViewPageTemplateFile('blank.pt')

class ContainerView(BrowserView):
    name = 'index.html'
    def __call__(self):
        default = self.context.get_default() or None
        if default:
            view = get_view(default, self.request, name=self.name)
        else:
            view = BlankView(self.context, self.request).__of__(self.context)
        return view()

class PreviewView(BrowserView):
    preview_buttons = ViewPageTemplateFile('../www/preview_buttons.zpt')

    def __init__(self, context, request):
        super(PreviewView, self).__init__(context, request)

        # make sure the back button points to the last edit screen visited
        back_url = request.SESSION.get('public_preview_back_url', None)
        # [sic]
        referer = request.get('HTTP_REFERER', None)
        if (referer and 'edit' in referer.split('/') and 
                not referer.endswith('/public_html')):
            # set the referer as the target for the back button...
            request.SESSION['public_preview_back_url'] = referer
            back_url = referer

        show_publish_now = (
            self.context.get_unapproved_version() is not None)

        # prepare arguments for preview_buttons page template
        self.args = {
            'message': request.get('message', ''),
            'message_type': request.get('message_type', ''),
            'show_publish_now': show_publish_now,
            'back_url': back_url,
            }
    
    def __call__(self):
        previewable = self.context.get_previewable()
        if not previewable:
            return BlankView(context, request).__of__(previewable)()
        view = get_view(previewable, self.request, name='index.html')
        html = view.__of__(previewable)()
        index = html.find('</body>')
        return html[:index] + self.preview_buttons(**self.args) + html[index:]

class ContainerPreviewView(ContainerView):
    name = 'preview_html'
