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
from zope import interface
from zope.component import queryUtility
from zope.traversing.api import getPath
from zope.app.component.hooks import getSite

from zojax.cache.view import cache
from zojax.batching.batch import Batch

from zojax.calendar.cache import EventsTag
from zojax.calendar.interfaces import ICalendar

def EventsKey(oid, instance, *args, **kw):
    return {'context': getPath(instance.context),
            'bstart': instance.request.get('bstart', 0)}


class Events(object):

    events = ()

    @cache('pagelet: calendar.events', EventsKey, EventsTag)
    def render(self):
        calendar = queryUtility(ICalendar)
        if calendar is None:
            return super(Events, self).render()

        request = self.request

        year = request.get('year', None)
        month = request.get('month', None)
        day = request.get('day', None)

        try:
            year = int(year)
            month = int(month)
        except:
            return

        if not (year and month):
            return

        try:
            day = int(day)
        except:
            day = None

        events = calendar.getEvents(year, month, day)
        if events:
            self.events = Batch(events, size=15, request=self.request)

        return super(Events, self).render()
