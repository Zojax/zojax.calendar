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

from zope.event import notify
from zope.lifecycleevent import ObjectCreatedEvent, ObjectModifiedEvent

class Encoder(JSONEncoder):

    def encode(self, *kv, **kw):
        return unicode(super(Encoder, self).encode(*kv, **kw))

encoder = JSONEncoder()


def jsonable(func):

    def cal(self):
        self.request.response.setHeader('Content-Type', ' application/json;charset=UTF-8')
        return unicode(func(self)).encode('utf-8')
    return cal


def js2PythonTime(day):
    """ convert str date to datetime """
    try:
        day = datetime.strptime(day, '%m/%d/%Y %H:%M')
    except ValueError:
        try:
            day = datetime.strptime(day, '%m/%d/%Y')
        except ValueError:
            # TODO: need return error
            return encoder.encode({'success': False, 'message': 'Error converting time', 'day': day})
    return day


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


class addCalendar(object):

    @jsonable
    def __call__(self):
        request = self.request
        context = self.context

        calendarStartTime = request.form.get('CalendarStartTime', None)
        calendarEndTime = request.form.get('CalendarEndTime', None)
        calendarTitle = request.form.get('CalendarTitle', None)
        isAllDayEvent = request.form.get('IsAllDayEvent', None)


class listCalendar(object):

    @jsonable
    def __call__(self):
        request = self.request
        context = self.context

        showdate = request.form.get('showdate', datetime.now().strftime('%m/%d/%Y %H:%M'))
        viewtype = request.form.get('viewtype', 'month')

        showdate = js2PythonTime(showdate)

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
        ret['events'] = []
        ret["issort"] = True
        ret["start"] = first_date.strftime('%m/%d/%Y %H:%M')
        ret["end"] = last_date.strftime('%m/%d/%Y %H:%M')
        ret['error'] = None

        # select events from calendar within range:
        results = catalog.searchResults(
            traversablePath = {'any_of': (self.context,)},
            typeType = {'any_of': ('Event type',)},
            calendarEventDuration = {
                'between': (first_date, last_date, True, True)})

        events = ""
        for i in results:
            ret['events'].append([
                i.__name__,
                i.title,
                i.startDate.strftime('%m/%d/%Y %H:%M'),
                i.endDate.strftime('%m/%d/%Y %H:%M'),
                i.isAllDayEvent or 'null',
                0, #more than one day event
                   #InstanceType,
                i.recurringRule,
                i.color,
                1, #editable
                i.location or 'null',
                '' #attends
                ])

        return encoder.encode(ret)


class updateCalendar(object):

    @jsonable
    def __call__(self):
        request = self.request
        context = self.context
        container = context.context

        calendarId = request.form.get('calendarId', None)
        calendarStartTime = request.form.get('CalendarStartTime', None)
        calendarEndTime = request.form.get('CalendarEndTime', None)

        calendarStartTime = js2PythonTime(calendarStartTime)
        calendarEndTime = js2PythonTime(calendarEndTime)

        event = container.get(calendarId)
        print event

        if not event:
            return encoder.encode({'IsSuccess': False, 'Msg': 'Event is not updated'})

        event.startDate = calendarStartTime
        event.endDate = calendarEndTime

        notify(ObjectModifiedEvent(event))

        return encoder.encode({'IsSuccess': True, 'Msg': 'Succefully'})


class removeCalendar(object):

    @jsonable
    def __call__(self):
        request = self.request
        context = self.context
        container = context.context

        calendarId = request.form.get('calendarId', None)

        if not calendarId:
            return encoder.encode({'success': False, 'message': ''})

        try:
            del container[calendarId]
            msg = {'IsSuccess': True, 'Msg': 'Succefully'}
        except KeyError:
            msg = {'IsSuccess': False, 'Msg': 'Event is not removed'}

        return encoder.encode(msg)


class detailedCalendar(object):

    @jsonable
    def __call__(self):
        request = self.request
        context = self.context

        stpartdate = request.form.get('stpartdate', None)
        stparttime = request.form.get('stparttime', None)

        etpartdate = request.form.get('etpartdate', None)
        etparttime = request.form.get('etparttime', None)

        id = request.form.get('id', None)
        subject = request.form.get('Subject', None)
        isAllDayEvent = request.form.get('IsAllDayEvent', None)
        description = request.form.get('Description', None)
        location = request.form.get('Location', None)
        colorvalue = request.form.get('colorvalue', None)
        timezone = request.form.get('timezone', None)
