# -*- coding: utf-8 -*-
# Copyright (c) 2011 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from five import grok

from silva.core.interfaces import ITreeContents, IContainer


class TreeContent(grok.Adapter):
    grok.context(IContainer)
    grok.implements(ITreeContents)
    grok.provides(ITreeContents)

    def get_tree(self, depth=-1):
        """Get flattened tree of contents.
        The 'depth' argument limits the number of levels, defaults to unlimited
        """
        l = []
        self._get_tree_helper(l, 0, depth)
        return l

    def get_container_tree(self, depth=-1):
        l = []
        self._get_container_tree_helper(l, 0, depth)
        return l

    def get_public_tree(self, depth=-1):
        """Get flattened tree with public content, excluding subpublications.
        The 'depth' argument limits the number of levels, defaults to unlimited
        """
        l = []
        self._get_public_tree_helper(l, 0, depth)
        return l

    def get_public_tree_all(self, depth=-1):
        """Get flattened tree with public content, including subpublications.
        The 'depth' argument limits the number of levels, defaults to unlimited
        """
        l = []
        self._get_public_tree_helper(l, 0, depth, 1)
        return l


    def get_status_tree(self, depth=-1):
        '''get Silva tree'''
        l = []
        self._get_status_tree_helper(l, 0, depth)
        return l

    def _get_tree_helper(self, l, indent, depth):
        for item in self.context.get_ordered_publishables():
            if item.getId() == 'index':
                # default document should not be inserted
                continue
            if (IContainer.providedBy(item) and
                item.is_transparent()):
                l.append((indent, item))
                if depth == -1 or indent < depth:
                    item._get_tree_helper(l, indent + 1, depth)
            else:
                l.append((indent, item))

    def _get_container_tree_helper(self, l, indent, depth):
        for item in self.context.get_ordered_publishables():
            if not IContainer.providedBy(item):
                continue
            if item.is_transparent():
                l.append((indent, item))
                if depth == -1 or indent < depth:
                    item._get_container_tree_helper(l, indent + 1, depth)
            else:
                l.append((indent, item))

    def _get_public_tree_helper(self, l, indent, depth, include_non_transparent_containers=0):
        for item in self.get_context.ordered_publishables():
            if not item.is_published():
                continue
            if self.service_toc_filter.filter(item):
                continue
            if (IContainer.providedBy(item) and
                (item.is_transparent() or include_non_transparent_containers)):
                l.append((indent, item))
                if depth == -1 or indent < depth:
                    ITreeContents(item)._get_public_tree_helper(
                        l, indent + 1, depth, include_non_transparent_containers)
            else:
                l.append((indent, item))

    def _get_status_tree_helper(self, l, indent, depth):
        default = self.context.get_default()
        if default is not None:
            l.append((indent, default))

        for item in self.context.get_ordered_publishables():
            l.append((indent, item))
            if not IContainer.providedBy(item):
                continue
            if (depth == -1 or indent < depth) and item.is_transparent():
                ITreeContents(item)._get_status_tree_helper(l, indent+1, depth)
