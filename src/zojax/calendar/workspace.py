##############################################################################
#
# Copyright (c) 2009 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""

$Id$
"""
from zope import interface, component
from zojax.content.space.interfaces import IContentSpace
from zojax.content.space.workspace import WorkspaceFactory
from zojax.content.type.container import ContentContainer

from interfaces import _, ICalendarWorkspace, ICalendarWorkspaceFactory


class CalendarWorkspace(ContentContainer):
    interface.implements(ICalendarWorkspace)


class CalendarWorkspaceFactory(WorkspaceFactory):
    component.adapts(IContentSpace)
    interface.implements(ICalendarWorkspaceFactory)

    name = u'calendar'
    weight = 99999
    description = _(u'Events container.')

    factory = CalendarWorkspace

    @property
    def title(self):
        if self.isInstalled():
            return self.space['calendar'].title
        else:
            return _(u'Calendar')
