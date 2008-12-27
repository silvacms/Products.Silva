import AccessControl
#zope
import Globals

#silva
from Products.Silva.adapters import adapter
from Products.Silva import interfaces

#python
from types import StringType

module_security = AccessControl.ModuleSecurityInfo('Products.Silva.adapters.tocrendering')

def escape(thestring):
    thestring = thestring.replace('&','&amp;')
    thestring = thestring.replace('<','&lt;')
    thestring = thestring.replace('>','&gt;')
    return thestring

class TOCRenderingAdapter(adapter.Adapter):
    """ Adapter for TOCs (autotoc, document toc) to render"""

    __allow_access_to_unprotected_subobjects__ = 1

    #Special "fastie quickie" autotoc rendering code...
    #NOTE: get_tree_iterator and get_public_tree_iterator are just
    #      modified forms of Folder._get_tree_helper and
    #      Folder._get_public_tree_helper

    def _get_container_items(self, container, sort_order, show_types):
        items = container.objectItems(show_types)
        if sort_order in ('alpha','reversealpha'):
            #get_title could be blank, then use id
            items = [ (o[1].get_title() or o[1].id,o) for o in items ]
            if sort_order == "reversealpha":
                items.sort(reverse=True)
            else:
                items.sort()
            items = [ o[1] for o in items ]
        elif sort_order=='silva': #determine silva sorting
            nonordered_items = []
            ordered_items = []
            for i in items:
                if i[0] not in container._ordered_ids:
                    nonordered_items.append(i)
                else:
                    ordered_items.append(i)
            items = ordered_items + nonordered_items
        else: # chronologically by modification date
            items = [ (o[1].get_modification_datetime(),o) for o in items ]
            if sort_order.startswith('r'):
                items.sort(reverse=True)
            else:
                items.sort()
            items = [ o[1] for o in items ]
        return items

    def _get_tree_iterator(self, container, indent=0, toc_depth=-1,sort_order='silva',show_types=['Silva Document','Silva Folder', 'Silva Publication']):
        """yield for every element in this toc
        The 'depth' argument limits the number of levels, defaults to unlimited
        """
        items = self._get_container_items(container,sort_order,show_types)

        for (name,item) in items:
            if name == 'index': #include the containers index
                # default document should not be inserted
                continue
            #preview doesn't obey toc_filters?
            yield (indent, item)
            if interfaces.IContainer.providedBy(item) and \
                   item.is_transparent() and \
                   (toc_depth == -1 or indent < toc_depth):
                for (dep,o) in self._get_tree_iterator(item, indent + 1, toc_depth=toc_depth,sort_order=sort_order,show_types=show_types):
                    yield (dep,o)

    def _get_public_tree_iterator(self, container, indent=0, include_non_transparent_containers=0, toc_depth=-1,sort_order='silva',show_types=['Silva Document','Silva Folder', 'Silva Publication']):
        toc_filter = self.context.service_toc_filter
        items = self._get_container_items(container,sort_order,show_types)
        for (name,item) in items:
            if not (item.is_published() or interfaces.IAsset.providedBy(item)) or \
                   (name=='index'):
                continue
            if toc_filter.filter(item):
                    continue
            yield (indent, item)
            if (interfaces.IContainer.providedBy(item) and \
                (item.is_transparent() or \
                 include_non_transparent_containers))  and \
                (toc_depth == -1 or indent < toc_depth):
                for (dep,o) in self._get_public_tree_iterator(item, indent+1,
                                                   include_non_transparent_containers,toc_depth=toc_depth,sort_order=sort_order,show_types=show_types):
                    yield (dep,o)

    def render_tree(self, public=1, append_to_url=None, toc_depth=-1,
                    display_desc_flag=False, sort_order="silva",
                    show_types=['Silva Document', 'Silva Publication', 'Silva Folder'],
                    show_icon=False):
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
        depth = 0
        item = None
        for (depth,item) in func(container=self.context,toc_depth=toc_depth,sort_order=sort_order,show_types=show_types):
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
            if show_icon:
                html.append(self.context.render_icon(item))
            title = (public and item.get_title() or item.get_title_editable()) or item.id
            html.append(a_templ%(
                item.absolute_url(),
                append_to_url,
                escape(title)))
            if display_desc_flag:
                v = public and item.get_viewable() or item.get_previewable()
                desc = v and gmv(v,'silva-extra','content_description',acquire=0)
                if desc:
                    html.append('<p>%s</p>'%desc)
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
