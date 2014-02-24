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
import calendar
from pytz import utc
from datetime import datetime, timedelta

from zope import interface
from zope.component import getUtility
from zope.app.component.hooks import getSite
from zojax.catalog.index import DateTimeValueIndex, DateTimeSetIndex

from zojax.catalog.utils import Indexable
from zojax.catalog.interfaces import ICatalog

from interfaces import IEvent, IEventType, ICalendarProduct

dayTimedelta = timedelta(1)


class CalendarProduct(object):
    interface.implements(ICalendarProduct)

    def getEvents(self, year, month, day=None, tz=utc):
        year = int(year)
        month = int(month)

        if not day:
            last_day = calendar.monthrange(year, month)[1]
            first_date = datetime(year, month, 1, 0, 0, 0, 0, tz)
            last_date = datetime(year, month, last_day, 23, 23, 59, 0, tz)
        else:
            first_date = datetime(year, month, day, 0, 0, 0, 0, tz)
            last_date = datetime(year, month, day, 23, 23, 59, 0, tz)

        catalog = getUtility(ICatalog)

        results = catalog.searchResults(
            searchContext = (getSite(),),
            sort_on='calendarEventStart', sort_order='reverse',
            typeType = {'any_of': ('Event type',)},
            calendarEventDuration = {
                'between': (first_date, last_date, True, True)})

        return results


def indexEventStart():
    return DateTimeValueIndex(
        'startDate',
        Indexable('zojax.calendar.product.EventDuration'), resolution=4)


def indexEventDuration():
    return DateTimeSetIndex(
        'duration',
        Indexable('zojax.calendar.product.EventDuration'), resolution=4)


class EventDuration(object):

    def __init__(self, context, default=None):
        self.duration = default

        event = IEvent(context, None)
        if event is None:
            self.duration = default
            return

        value = event.startDate
        if value is None:
            self.duration = default
            return

        if value.tzinfo is None:
            startDate = datetime(
                value.year, value.month, value.day, value.hour,
                value.minute, value.second, value.microsecond, utc)
        else:
            startDate = value

        value = event.endDate
        if value.tzinfo is None:
            endDate = datetime(
                value.year, value.month, value.day, value.hour,
                value.minute, value.second, value.microsecond, utc)
        else:
            endDate = value

        self.endDate = endDate
        self.startDate = startDate

        duration = [startDate, endDate]

        date = datetime(
            startDate.year, startDate.month, startDate.day, 12, 0, 0, 0, utc)

        while date < endDate:
            if date > startDate:
                duration.append(date)
            date = date + dayTimedelta

        self.duration = duration
