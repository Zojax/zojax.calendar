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
from zope.component import getUtility, queryUtility
from zope.app.component.hooks import getSite
from zope.app.intid.interfaces import IIntIds

from zojax.cache.view import cache
from zojax.cache.timekey import TimeKey, each15minutes
from zojax.portlet.cache import PortletId, PortletModificationTag
from zojax.catalog.interfaces import ICatalog
from zojax.content.space.utils import getSpace
from zojax.principal.profile.timezone import getPrincipalTimezone

from cache import EventsTag
from interfaces import IEventsPortlet


def CalendarKey(object, instance, *args, **kw):
    if not instance.visibility:
        return (('principal', request.principal.id),)

    return ()


class EventsPortlet(object):
    interface.implements(IEventsPortlet)

    events = None

    @cache(PortletId(), EventsTag, PortletModificationTag, CalendarKey, TimeKey(minutes=each15minutes))
    def updateAndRender(self):
        return super(EventsPortlet, self).updateAndRender()

    def update(self):
        super(EventsPortlet, self).update()

        context, request = self.context, self.request

        ids = queryUtility(IIntIds)
        principal = request.principal

        now = datetime.now(utc)
        endDay = now+timedelta(3650)

        # set timezone from user profile
        user_tz = getPrincipalTimezone(principal)
        if user_tz:
            now = now.astimezone(user_tz)
            endDay = endDay.astimezone(user_tz)

        query = dict(searchContext=(getSite(),),
                     sort_on='calendarEventStart',
                     typeType = {'any_of': ('Event type',)},
                     )

        if self.spaceMode == 2:
            query['contentSpace'] = {'any_of': [ids.queryId(getSpace(context))]}
        elif self.spaceMode == 3:
            query['traversablePath'] = {'any_of':(getSpace(context),)}

        if self.onlyToday:
            tz = user_tz and user_tz or utc
            endDay = datetime(now.year, now.month, now.day, 23, 59, 59, 0)
            endDay = tz.localize(endDay)

        query['calendarEventDuration']={'between': (now, endDay, True, True)}
        results = getUtility(ICatalog).searchResults(**query)

        if results:
            self.events = results[:self.count]

    def isAvailable(self):
        if not self.events:
            return False

        return super(EventsPortlet, self).isAvailable()
