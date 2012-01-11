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
from pytz import utc
from datetime import datetime, timedelta

from zope import interface
from zope.component import getUtility
from zope.traversing.api import getPath
from zope.app.component.hooks import getSite

from zojax.cache.view import cache
from zojax.cache.timekey import TimeKey, each15minutes
from zojax.portlet.cache import PortletId, PortletModificationTag
from zojax.catalog.interfaces import ICatalog

from cache import EventsTag
from interfaces import IEventsPortlet


def CalendarKey(object, instance, *args, **kw):
    if not instance.visibility:
        return (('principal', request.principal.id),)

    return ()


class EventsPortlet(object):
    interface.implements(IEventsPortlet)

    events = None

    @cache(PortletId(), EventsTag, PortletModificationTag, CalendarKey, TimeKey(each15minutes))
    def updateAndRender(self):
        return super(EventsPortlet, self).updateAndRender()

    def update(self):
        super(EventsPortlet, self).update()

        now = datetime.now(utc)

        query = dict(searchContext=(getSite(),),
                     sort_on='calendarEventStart',
                     typeType = {'any_of': ('Event type',)},
                     )

        if self.onlyToday:
            endDay = datetime(now.year, now.month, now.day, 23, 23, 59, 0, utc)
            query['calendarEventDuration']={'between': (now, endDay, True, True)}
        else:
            query['calendarEventDuration']={'between': (now, now+timedelta(3650), True, True)}

        results = getUtility(ICatalog).searchResults(**query)

        if results:
            self.events = results[:self.count]

    def isAvailable(self):
        if not self.events:
            return False

        return super(EventsPortlet, self).isAvailable()
