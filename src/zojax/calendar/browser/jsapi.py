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
from zojax.calendar.product import calendar as calendarModule

import urllib
from pytz import utc, timezone
from datetime import datetime, timedelta
from simplejson import JSONEncoder

from zope import interface
from zope.event import notify
from zope.component import getUtility, queryMultiAdapter
from zope.traversing.browser import absoluteURL
from zope.publisher.browser import BrowserView
from zope.publisher.interfaces import NotFound
from zope.lifecycleevent import ObjectCreatedEvent, ObjectModifiedEvent

from zojax.catalog.interfaces import ICatalog
from zojax.content.type.interfaces import IContentType
from zojax.formatter.interfaces import IFormatterConfiglet
from zojax.personal.space.interfaces import IPersonalSpace
from zojax.principal.profile.interfaces import IPersonalProfile
from zojax.resourcepackage.library import include, includeInplaceSource
from zojax.authentication.utils import getPrincipal
from zojax.principal.profile.timezone import getPrincipalTimezone
from zojax.principal.field.utils import searchPrincipals


class Encoder(JSONEncoder):

    def encode(self, *kv, **kw):
        return unicode(super(Encoder, self).encode(*kv, **kw))

encoder = JSONEncoder()


def jsonable(func):

    def cal(self):
        self.request.response.setHeader('Content-Type', ' application/json;charset=UTF-8')
        return unicode(func(self)).encode('utf-8')
    return cal


def js2PythonTime(value, diffHours=None):
    """ converts str date to datetime """
    try:
        value = datetime.strptime(value, '%m/%d/%Y %H:%M')
    except ValueError:
        try:
            value = datetime.strptime(value, '%m/%d/%Y')
        except ValueError:
            return encoder.encode({'success': False, 'message': 'Error converting time', 'value': value})

    # set timezone from settings
    configlet = getUtility(IFormatterConfiglet)
    tz = timezone(configlet.timezone)
    if value.tzinfo is None:
        value = datetime(value.year, value.month, value.day, value.hour,
                         value.minute, value.second, value.microsecond, tz)

    value = value.astimezone(tz)

    if diffHours:
        value = value - timedelta(hours=int(diffHours))

    return value


def membersToTuple(members):
    """ converts members to tuple """
    if isinstance(members, list):
        # olny uniq members
        seen = set()
        uniqMembers = [x for x in members if x not in seen and not seen.add(x)]
        return tuple( uniqMembers )
    elif isinstance(members, basestring):
        return (members,)
    return ()


def timezoneToJs(tz):
    """ converts timezone to number for js """
    value = datetime.now(utc).astimezone(tz)

    offset = value.tzinfo.utcoffset(value)
    if offset < timedelta():
        ind = -1
    else:
        ind = 1
    offset = ind*(abs(offset).seconds/600)*10

    return offset/60


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
        context, request = self.context, self.request
        container = context.context

        calendarStartTime = request.form.get('CalendarStartTime', None)
        calendarEndTime = request.form.get('CalendarEndTime', None)
        eventTitle = request.form.get('CalendarTitle', None).strip()
        isAllDayEvent = request.form.get('IsAllDayEvent', None)
        diffHours = request.form.get('timezone', None)

        try:
            eventCt = getUtility(IContentType, name='calendar.event')
            event = eventCt.create(title=eventTitle)

            event.startDate = js2PythonTime(calendarStartTime, diffHours=diffHours)
            event.endDate = js2PythonTime(calendarEndTime, diffHours=diffHours)
            event.isAllDayEvent = bool(isAllDayEvent)

            eventCt.__bind__(container).add(event)

            msg = {'IsSuccess': True, 'Msg': 'Created Successfully'}
        except Exception, e:
            msg = {'IsSuccess': False, 'Msg': 'Event is not created: %s'%e}

        return encoder.encode(msg)


class listCalendar(object):

    diffHours = None

    @jsonable
    def __call__(self):
        context, request = self.context, self.request

        # set timezone from settings
        configlet = getUtility(IFormatterConfiglet)
        tz = timezone(configlet.timezone)

        showdate = request.form.get('showdate', datetime.now().strftime('%m/%d/%Y %H:%M'))
        viewtype = request.form.get('viewtype', 'month')
        self.diffHours = request.form.get('timezone', None)

        showdate = js2PythonTime(showdate)

        if viewtype == 'month':
            lastDay = calendarModule.monthrange(showdate.year, showdate.month)[1]
            first_date = datetime(showdate.year, showdate.month, 1, 0, 0, 0, 0, tzinfo=tz)
            last_date = datetime(showdate.year, showdate.month, lastDay, 23, 23, 59, 0, tzinfo=tz)

        if viewtype == 'week':
            currentWeekDay = calendarModule.weekday(showdate.year, showdate.month, showdate.day)
            firstWeekDay = showdate - timedelta(days=currentWeekDay)
            first_date = datetime(firstWeekDay.year, firstWeekDay.month, firstWeekDay.day, 0, 0, 0, 0, tzinfo=tz)
            last_date = datetime(firstWeekDay.year, firstWeekDay.month, firstWeekDay.day, 23, 23, 59, 0, tzinfo=tz) + timedelta(days=6)

        if viewtype == 'day':
            first_date = datetime(showdate.year, showdate.month, showdate.day, 0, 0, 0, 0, tzinfo=tz)
            last_date = datetime(showdate.year, showdate.month, showdate.day, 23, 23, 59, 0, tzinfo=tz)

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

        if self.diffHours:
            first_date = first_date - timedelta(hours=int(self.diffHours))
            last_date = last_date - timedelta(hours=int(self.diffHours))

        # select events from calendar within range:
        results = catalog.searchResults(
            traversablePath = {'any_of': (self.context,)},
            typeType = {'any_of': ('Event type',)},
            calendarEventDuration = {
                'between': (first_date, last_date, True, True)})

        events = ""
        for i in results:

            members = []
            if i.attendees:
                for member in i.attendees:
                    principal = getPrincipal(member)

                    homeFolder = IPersonalSpace(principal, None)
                    profileUrl = homeFolder is not None \
                        and '%s/profile/'%absoluteURL(homeFolder, self.request) or ''

                    members.append('<a href="%s">%s</a>'%(profileUrl, principal.title))

            text = getattr(i.text,'cooked', '')
            startDate = i.startDate
            endDate = i.endDate

            if self.diffHours:
                startDate = startDate + timedelta(hours=int(self.diffHours))
                endDate = endDate + timedelta(hours=int(self.diffHours))

            ret['events'].append([
                i.__name__,
                i.title,
                startDate.strftime('%m/%d/%Y %H:%M'),
                endDate.strftime('%m/%d/%Y %H:%M'),
                i.isAllDayEvent,
                0, #more than one day event
                   #InstanceType,
                i.recurringRule,
                i.color,
                1, #editable
                i.location,
                i.description,
                urllib.quote(', '.join(members)), #attends
                i.eventUrl,
                i.contactName,
                i.contactEmail,
                i.contactPhone,
                text #i.text
                ])

        return encoder.encode(ret)


class updateCalendar(object):

    @jsonable
    def __call__(self):
        context, request = self.context, self.request
        container = context.context

        calendarId = request.form.get('calendarId', None)
        calendarStartTime = request.form.get('CalendarStartTime', None)
        calendarEndTime = request.form.get('CalendarEndTime', None)
        diffHours = request.form.get('timezone', None)

        calendarStartTime = js2PythonTime(calendarStartTime, diffHours=diffHours)
        calendarEndTime = js2PythonTime(calendarEndTime, diffHours=diffHours)

        event = container.get(calendarId)

        if not event:
            return encoder.encode({'IsSuccess': False, 'Msg': 'Event is not updated'})

        event.startDate = calendarStartTime
        event.endDate = calendarEndTime

        notify(ObjectModifiedEvent(event))

        return encoder.encode({'IsSuccess': True, 'Msg': 'Updated Successfully'})


class removeCalendar(object):

    @jsonable
    def __call__(self):
        context, request = self.context, self.request
        container = context.context

        calendarId = request.form.get('calendarId', None)

        if not calendarId:
            return encoder.encode({'success': False, 'message': 'Event is not removed'})

        try:
            del container[calendarId]
            msg = {'IsSuccess': True, 'Msg': 'Removed Successfully'}
        except KeyError, e:
            msg = {'IsSuccess': False, 'Msg': 'Event is not removed: %s'%e}

        return encoder.encode(msg)


class detailedCalendar(object):

    @jsonable
    def __call__(self):
        context, request = self.context, self.request
        container = context.context

        diffHours = request.form.get('timezone', None)

        stpartdate = request.form.get('stpartdate', None)
        stparttime = request.form.get('stparttime', None)
        startDate = js2PythonTime(stpartdate + (stparttime and ' '+stparttime or ''), diffHours=diffHours)

        etpartdate = request.form.get('etpartdate', None)
        etparttime = request.form.get('etparttime', None)
        endDate = js2PythonTime(etpartdate + (etparttime and ' '+etparttime or ''), diffHours=diffHours)

        eventId = request.form.get('id', None)

        subject = request.form.get('Subject', None).strip()
        isAllDayEvent = request.form.get('IsAllDayEvent', None)
        description = request.form.get('Description', None).strip()
        location = request.form.get('Location', None).strip()
        colorvalue = request.form.get('colorvalue', None)
        timezone = request.form.get('timezone', None)

        attendees = request.form.get('attendees', None)
        eventUrl = request.form.get('eventUrl', None).strip()
        contactName = request.form.get('contactName', None).strip()
        contactEmail = request.form.get('contactEmail', None).strip()
        contactPhone = request.form.get('contactPhone', None).strip()
        text = request.form.get('text', None).strip()

        if eventId:
            ret = self.updateDetailedCalendar(eventId, startDate, endDate, \
                subject, isAllDayEvent, description, location, colorvalue, timezone, \
                eventUrl, contactName, contactEmail, contactPhone, text, attendees)
        else:
            ret = self.addDetailedCalendar(startDate, endDate, subject, \
                isAllDayEvent, description, location, colorvalue, timezone, \
                eventUrl, contactName, contactEmail, contactPhone, text, attendees)

        return ret

    def updateDetailedCalendar(self, eventId, startDate, endDate, \
        subject, isAllDayEvent, description, location, colorvalue, timezone, \
        eventUrl, contactName, contactEmail, contactPhone, text, attendees):
        context = self.context
        container = context.context

        if eventId and eventId in container:
            event = container[eventId]

            try:
                event.title = subject
                event.description = description
                event.startDate = startDate
                event.endDate = endDate
                event.location = location
                event.isAllDayEvent = bool(isAllDayEvent)
                event.color = colorvalue

                event.attendees = membersToTuple(attendees)
                event.eventUrl = bool(eventUrl) and eventUrl or None
                event.contactName = contactName
                event.contactEmail = bool(contactEmail) and contactEmail or None
                event.contactPhone = contactPhone
                event.text = text

                notify(ObjectModifiedEvent(event))

                msg = {'IsSuccess': True, 'Msg': 'Updated Successfully', 'Data': eventId}
            except Exception, e:
                msg = {'IsSuccess': False, 'Msg': 'Event is not update: %s'%e}
        else:
            msg = {'IsSuccess': False, 'Msg': 'Event is not update'}

        return encoder.encode(msg)


    def addDetailedCalendar(self, startDate, endDate, \
        subject, isAllDayEvent, description, location, colorvalue, timezone, \
        eventUrl, contactName, contactEmail, contactPhone, text, attendees):
        context = self.context
        container = context.context

        try:
            eventCt = getUtility(IContentType, name='calendar.event')
            event = eventCt.create(title=subject)

            event.description = description
            event.startDate = startDate
            event.endDate = endDate
            event.location = location
            event.isAllDayEvent = bool(isAllDayEvent)
            event.color = colorvalue

            event.attendees = membersToTuple(attendees)
            event.eventUrl = bool(eventUrl) and eventUrl or None
            event.contactName = contactName
            event.contactEmail = bool(contactEmail) and contactEmail or None
            event.contactPhone = contactPhone
            event.text = text

            eventCt.__bind__(container).add(event)

            msg = {'IsSuccess': True, 'Msg': 'Created Successfully', 'Data': ''}
        except Exception, e:
            msg = {'IsSuccess': False, 'Msg': 'Event is not created: %s'%e}

        return encoder.encode(msg)


class listMembers(object):

    @jsonable
    def __call__(self):
        context, request = self.context, self.request
        container = context.context

        tag = request.form.get('tag', None)

        query = dict(type=('user',),)
        if tag:
            query['searchableText'] = tag

        members = []
        for member in searchPrincipals(**query)[:10]:
            oneMember = {}
            oneMember["key"] = member.id
            oneMember["value"] = member.title
            members.append(oneMember)

        return encoder.encode(members)


class editCalendar(object):
    """ popup form of editing calendar event """

    def update(self):
        context, request = self.context, self.request

        configlet = getUtility(IFormatterConfiglet)
        tz = timezone(configlet.timezone)
        if tz:
            # difference between timezone in user's browser and formatter settings
            timeZone = '(new Date().getTimezoneOffset() / 60 * -1) - %s'%timezoneToJs(tz)
        else:
            timeZone = str('new Date().getTimezoneOffset() / 60 * -1')

        apiUrl = u'%s/CalendarAPI/'%absoluteURL(context, request)
        includeInplaceSource(jssource%{
                'apiUrl': apiUrl,
                'timezone': timeZone,
                }, ('jquery-wdcalendar', 'zojax-calendar-edit',))

    def getEvent(self, eventId, diffHours):
        context = self.context

        if eventId and eventId in context:
            event = context[eventId]
            startDate = event.startDate
            endDate = event.endDate

            members = []
            for memeber in event.attendees:
                principal = getPrincipal(memeber)
                oneMember = {}
                oneMember["key"] = memeber
                oneMember["value"] = principal.title
                members.append(oneMember)

            if diffHours:
                startDate = startDate + timedelta(hours=int(diffHours))
                endDate = endDate + timedelta(hours=int(diffHours))

            info = {
                'event': event,
                'sdDate': startDate.strftime('%m/%d/%Y'),
                'sdTime': startDate.strftime('%H:%M'),
                'edDate': endDate.strftime('%m/%d/%Y'),
                'edTime': endDate.strftime('%H:%M'),
                'members': members}
            return info

        return

    def splitDateTime(self, value):
        """ returns array with date and time """
        if not value or not " " in value:
            return

        value = value.split()
        return value

jssource = """<script type="text/javascript">
        var CalendarAPI_URL = '%(apiUrl)s';
        var userTimezone = %(timezone)s;
</script>"""
