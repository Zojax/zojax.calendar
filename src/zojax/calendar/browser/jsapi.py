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
#import calendar as calendarModule
from zojax.calendar.product import calendar as calendarModule

from pytz import utc
from datetime import datetime, timedelta
from simplejson import JSONEncoder

from zope import interface
from zope.component import getUtility, queryMultiAdapter
from zope.publisher.browser import BrowserView
from zojax.catalog.interfaces import ICatalog
from zope.publisher.interfaces import NotFound


class Encoder(JSONEncoder):

    def encode(self, *kv, **kw):
        return unicode(super(Encoder, self).encode(*kv, **kw))

encoder = JSONEncoder()


def jsonable(func):

    def cal(self):
        self.request.response.setHeader('Content-Type', ' application/json;charset=UTF-8')
        return unicode(func(self)).encode('utf-8')
    return cal


class ICalendarAPI(interface.Interface):
    pass


class CalendarAPI(BrowserView):
    interface.implements(ICalendarAPI)

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.__parent__ = context

    def publishTraverse(self, request, name):
        view = queryMultiAdapter((self, request), name=name)
        if view is not None:
            return view

        raise NotFound(self, name, request)


class listCalendar(object):

    @jsonable
    def __call__(self):
        request = self.request
        context = self.context

        showdate = request.form.get('showdate', datetime.now().strftime('%m/%d/%Y %H:%M'))
        viewtype = request.form.get('viewtype', 'month')

        # convert str date to datetime:
        try:
            showdate = datetime.strptime(showdate, '%m/%d/%Y %H:%M')
        except ValueError:
            try:
                showdate = datetime.strptime(showdate, '%m/%d/%Y')
            except ValueError:
                # TODO: need return error
                return """{"showdate": %s}"""%showdate

        if viewtype == 'month':
            lastDay = calendarModule.monthrange(showdate.year, showdate.month)[1]
            first_date = datetime(showdate.year, showdate.month, 1, 0, 0, 0, 0, utc)
            last_date = datetime(showdate.year, showdate.month, lastDay, 23, 23, 59, 0, utc)

        if viewtype == 'week':
            firstWeekDay = showdate.day - calendarModule.weekday(showdate.year, showdate.month, showdate.day)
            first_date = datetime(showdate.year, showdate.month, firstWeekDay, 0, 0, 0, 0, utc)
            last_date = datetime(showdate.year, showdate.month, firstWeekDay, 23, 23, 59, 0, utc) + timedelta(days=6)

        if viewtype == 'day':
            first_date = datetime(showdate.year, showdate.month, showdate.day, 0, 0, 0, 0, utc)
            last_date = datetime(showdate.year, showdate.month, showdate.day, 23, 23, 59, 0, utc)

        return self.listCalendarByRange(first_date, last_date)

    def listCalendarByRange(self, first_date, last_date):
        """ """
        catalog = getUtility(ICatalog)

        ret = {}
        ret['events'] = ""
        ret["issort"] = 'true'
        ret["start"] = first_date
        ret["end"] = last_date
        ret['error'] = 'null'

        # select events from calendar within range:
        results = catalog.searchResults(
            traversablePath = {'any_of': (self.context,)},
            typeType = {'any_of': ('Event type',)},
            calendarEventDuration = {
                'between': (first_date, last_date, True, True)})

        events = ""
        for i in results:
            events = events + """["%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s"],"""%(
                i.__name__,
                i.title,
                i.startDate.strftime('%m/%d/%Y %H:%M'),
                i.endDate.strftime('%m/%d/%Y %H:%M'),
                0, #IsAllDayEvent,
                0, #more than one day event
                   #$row->InstanceType,
                0, #Recurring event,
                '6', #$row->Color,
                1, #editable
                i.location or 'null',
                '' #$attends
                )
        ret['events'] = "[%s]"%events[:-1]

        return """{"start":"%s", "issort":true, "end":"%s", "events":%s, "error":null}"""%(
            ret["start"].strftime('%m/%d/%Y %H:%M'),
            ret["end"].strftime('%m/%d/%Y %H:%M'),
            ret['events'])
