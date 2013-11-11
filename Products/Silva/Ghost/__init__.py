# -*- coding: utf-8 -*-
# Copyright (c) 2002-2013 Infrae. All rights reserved.
# See also LICENSE.txt


from zeam.component import getComponent
from silva.core.interfaces import IGhostManager

# For BBB
from .base import GhostBase, GhostBaseManager, GhostBaseManipulator
from .content import Ghost, GhostVersion
from .smi import TargetValidator


def get_ghost_factory(container, target):
    """add new ghost to container
    """
    if target is None:
        return None

    get_manager = getComponent((target,), IGhostManager, default=None)
    if get_manager is None:
        return None

    return lambda identifier: get_manager(
        container=container).modify(target, identifier).create(recursive=True)

