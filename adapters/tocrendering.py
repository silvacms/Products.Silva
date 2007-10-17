import AccessControl
#zope
import Globals

#silva
from Products.Silva.adapters import adapter
from Products.Silva import interfaces

#python
from types import StringType

module_security = AccessControl.ModuleSecurityInfo('Products.Silva.adapters.tocrendering')

class TOCRenderingAdapter(adapter.Adapter):
    """ Adapter for TOCs (autotoc, document toc) to render"""

    __allow_access_to_unprotected_subobjects__ = 1

    #Special "fastie quickie" autotoc rendering code...
    #NOTE: get_tree_iterator and get_public_tree_iterator are just
    #      modified forms of Folder._get_tree_helper and
    #      Folder._get_public_tree_helper

    def _get_tree_iterator(self, container, indent=0, toc_depth=-1):
        """yield for every element in this toc
        The 'depth' argument limits the number of levels, defaults to unlimited
        """
        for item in container.get_ordered_publishables():
            if indent and item.id == 'index': #include the containers index
                # default document should not be inserted
                continue
            #preview doesn't obey toc_filters?
            yield (indent, item)
            if interfaces.IContainer.providedBy(item) and \
                   item.is_transparent() and \
                   (toc_depth == -1 or indent < toc_depth):
                for (dep,o) in self._get_tree_iterator(item, indent + 1, toc_depth=toc_depth):
                    yield (dep,o)

    def _get_public_tree_iterator(self, container, indent=0, include_non_transparent_containers=0, toc_depth=-1):
        toc_filter = self.context.service_toc_filter
        for item in container.get_ordered_publishables():
            if not (item.is_published() or interfaces.IAsset.providedBy(item)) or \
                   (indent and item.id=='index'):
                continue
            if toc_filter.filter(item):
                    continue
            yield (indent, item)
            if (interfaces.IContainer.providedBy(item) and \
                (item.is_transparent() or \
                 include_non_transparent_containers))  and \
                (toc_depth == -1 or indent < toc_depth):
                for (dep,o) in self._get_public_tree_iterator(item, indent+1,
                                                   include_non_transparent_containers,toc_depth=toc_depth):
                    yield (dep,o)

    def render_tree(self, public=1, append_to_url=None, toc_depth=-1):
        if isinstance(append_to_url,StringType):
            if append_to_url[0] != '/':
                append_to_url = '/' + append_to_url
        else:
            append_to_url = ''

        #func is either a generator function that returns the public items
        #or all items to render in this TOC.  The functions use yields
        #to generate the lists.  Rendering is sped up since the list
        #is only iterated through once.
        func = public and self._get_public_tree_iterator or self._get_tree_iterator
        html = []
        a_templ = '<a href="%s%s">%s</a>'

        prev_depth = [-1]
        gmv = self.context.service_metadata.getMetadataValue
        depth = item = None  #need to pre-initialize these
        #the func yeilds the depth and the item for each item, and
        #this loop will quietly end when there are no more items to render
        for (depth,item) in func(container=self.context,toc_depth=toc_depth):
            pd = prev_depth[-1]
            if pd < depth: #down one level
                html.append('<ul class="toc">')
                prev_depth.append(depth)
            elif pd > depth: #up one level
                for i in range(pd-depth):
                    prev_depth.pop()
                    html.append('</ul></li>')
            elif pd == depth: #same level
                html.append('</li>')
            html.append('<li>')
            title = (public and item.get_title() or item.get_title_editable()) or item.id
            html.append(a_templ%(item.absolute_url(),append_to_url,title))
        else:
            #do this when the loop is finished, to
            #ensure that the lists are ended properly
            #the last item in the list could part of a nested list (with depth 1,2,3+, etc)
            #so need to loop down the depth and close all open lists
            while depth >= 0:
                html.append('</li></ul>')
                depth -= 1
        return '\n'.join(html)
    
Globals.InitializeClass(TOCRenderingAdapter)

def __allow_access_to_unprotected_subobjects__(name,value=None):
    return name in ('getTOCRenderingAdapter')

#NOTE: can pass in any Silva object.  If object isn't a container
#      this will acquire the nearest container
def getTOCRenderingAdapter(container):
    if not interfaces.IContainer.providedBy(container):
        container = container.get_container()
    return TOCRenderingAdapter(container)
