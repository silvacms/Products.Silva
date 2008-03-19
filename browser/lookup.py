# from Products.Silva.i18n import translate as _

# from Products.Silva.adapters.interfaces import IViewerSecurity
# from Products.Silva.roleinfo import ASSIGNABLE_VIEWER_ROLES

from Products.Silva.interfaces import IContent, IContainer, IAsset, \
     IPublishable, IGhostFolder
from DateTime import DateTime
from AccessControl import getSecurityManager
from Products.Five import BrowserView
from Acquisition import aq_base
from Products.Silva import mangle, icon

class ObjectLookup(BrowserView):
    """
    View that allows browsing and searching for objects.
    """

    def renderIcon(self, obj=None, meta_type='Unknown'):
        """Gets the icon for the object and wraps that in an image tag
        """
        tag = ('<img src="%(icon_path)s" width="16" height="16" border="0" '
               'alt="%(alt)s" />')
        if obj is None:
            icon_path = ('%s/globals/silvageneric.gif' %
                         self.context.REQUEST['BASE2'])
            return tag % {'icon_path': icon_path, 'alt': meta_type}
        try:
            icon_path = '%s/%s' % (self.context.REQUEST['BASE1'],
                icon.registry.getIcon(obj))
        except icon.RegistryError:
            icon_path = getattr(aq_base(obj), 'icon', None)
            if icon_path is None:
                icon_path = ('%s/globals/silvageneric.gif' %
                             self.context.REQUEST['BASE2'])
            meta_type = getattr(obj, 'meta_type')
        return tag % {'icon_path': icon_path, 'alt': meta_type}
    
    def objectLookupGetObjects(self, filter=None, show_add=False):
        """Returns objects to be displayed for the lookup window
            
            filter: 'Asset', 'Content', a certain meta_type (string) or a 
                        list of meta_types

            show_add: whether or not to show the 'add' button (to add new 
                        objects)

            returns a tuple with 5 values:

              default - can be None or refers to the default object (index)

              publishables - an ordered list of publishable items

              assets - a list of assets (ordered by id)

              addables - a list of meta_types that are allowed to be added 
                        to the page

              show_containers - true if containers are in the list of publishables
                                but shouldn't be selectable
        """
        model = self.context

        default = None
        ordered_publishables = []
        assets = []
        all_addables = []

        show_containers = []

        filter = filter or []
        
        if show_add and not IGhostFolder.providedBy(model):
            all_addables = model.get_silva_addables()

        if isinstance(filter, str):
            filter = filter.split("|")
        
        if filter == ['Asset']:
            assets = model.get_assets()
            ordered_publishables = [
                o for o in model.get_ordered_publishables() 
                if o.implements_container()]
            show_containers = ordered_publishables
            if show_add:
                addables = [a['name'] for a in all_addables if 
                                IAsset.implementedBy(
                                    a['instance'])]
        elif filter == ['Content']:
            default = model.get_default()
            ordered_publishables = []
            if default:
                ordered_publishables.append(default)
            ordered_publishables.extend(
                [o for o in model.get_ordered_publishables() if 
                    o.implements_content() or o.implements_container() ]
            )
            show_containers = [ o for o in ordered_publishables if o.implements_container() ]
            if show_add:
                addables = [a['name'] for a in all_addables if
                                IContent.implementedBy(
                                    a['instance'])]
        elif filter == ['Container']:
            ordered_publishables = [
                o for o in model.get_ordered_publishables() 
                if o.implements_container()]
            if show_add:
                addables = [a['name'] for a in all_addables if 
                                IContainer.implementedBy(
                                    a['instance'])]
        elif filter == ['Publishable']:
            default = model.get_default()
            ordered_publishables = []
            if default:
                ordered_publishables.append(default)
            ordered_publishables.extend(model.get_ordered_publishables())
            if show_add:
                addables = [a['name'] for a in all_addables if
                                IPublishable.implementedBy(
                                    a['instance'])]
        else:
            # get all objects using filter, then divide them the way they 
            # should be returned
            if not filter or filter == ['']:
                # return everything
                default = model.get_default()
                ordered_publishables = model.get_ordered_publishables()
                assets = model.get_assets()
                if show_add:
                    addables = [a['name'] for a in all_addables]
            else:
                #assume filter containers a list of meta types
                objects = model.objectValues(filter)
                defaultobj = model.get_default()
                if defaultobj and defaultobj in objects:
                    default = defaultobj
                for o in model.get_ordered_publishables():
                    if o in objects:
                        ordered_publishables.append(o)
                    elif o.implements_container():
                        ordered_publishables.append(o)
                        show_containers.append(o)
                for o in model.get_assets():
                    if o in objects:
                        assets.append(o)

                if show_add:
                    addables = [
                        a['name'] for a in all_addables if a['name'] in filter]

        # sort the assets
        assets.sort(lambda a, b: cmp(a.id, b.id))

        return (default, ordered_publishables, assets, addables, show_containers)


class SidebarView(BrowserView):
    def render(self, tab_name, vein):
        # XXX once we move everything to five views, the object_lookup
        # template can become much much simpler.
        context = self.context.aq_inner
        sidebar = context.service_sidebar.render(context, tab_name, vein)
        sidebar = sidebar.replace('/edit/', '/')
        return sidebar
