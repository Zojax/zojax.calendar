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
from time import localtime
from datetime import date, datetime

from zope import interface
from zope.component import getUtility
from zope.session.interfaces import ISession
from zope.app.component.hooks import getSite

from zojax.cache.view import cache
from zojax.portlet.cache import PortletId, PortletModificationTag

from zojax.calendar.cache import EventsTag
from zojax.calendar.interfaces import ICalendar

sessionId = 'zojax.calendar.currentdate'


def CalendarKey(object, instance, *args, **kw):
    key = {'today': date.today(),
           'currentDate': (instance.year, instance.month)}

    if not instance.visibility:
        key['principal'] = request.principal.id

    return key


class CalendarPortlet(object):

    def __init__(self, context, request, manager, view):
        super(CalendarPortlet, self).__init__(context, request, manager, view)

        self.now = localtime()
        self.year, self.month = self.getCurrentDate()

    @cache(PortletId(), EventsTag, PortletModificationTag, CalendarKey)
    def updateAndRender(self):
        return super(CalendarPortlet, self).updateAndRender()

    def update(self):
        self.site = getSite()
        self.calendar = self.request.locale.dates.calendars['gregorian']

        now = self.now
        year = self.year
        month = self.month
        yearmonth = year, month

        self.showPrevMonth = yearmonth > (now[0]-1, now[1])
        self.showNextMonth = yearmonth < (now[0]+1, now[1])

        # next/previous month/year
        if month == 1:
            self.prevMonthMonth, self.prevMonthYear = 12, year - 1
        else:
            self.prevMonthMonth, self.prevMonthYear = month - 1, year

        if month == 12:
            self.nextMonthMonth, self.nextMonthYear = 1, year + 1
        else:
            self.nextMonthYear, self.nextMonthMonth = year, month + 1

        # current month name
        self.monthName = self.calendar.getMonthNames()[month-1]

    def getEventsForCalendar(self):
        year, month = self.year, self.month
        last_day = filter(lambda x: bool(x),
                          calendar.monthcalendar(year, month)[-1])[-1]
        calendar.setfirstweekday(self.calendar.week['firstDay']-1)

        events = {}
        for event in getUtility(ICalendar).getEvents(year, month):
            end = event.endDate
            first = event.startDate.day
            if end.year > year or end.month > month:
                endDay = last_day
            else:
                endDay = end.day
            for day in range(first, endDay + 1):
                data = events.setdefault(day, [])
                data.append(event)

        todayDay = self.now[2]
        isToday = (self.now[1] == self.month) and (self.now[0] == self.year)

        data = []
        for week in calendar.monthcalendar(year, month):
            data.append([])
            weekdata = data[-1]

            for daynumber in week:
                if daynumber == 0:
                    weekdata.append(0)
                    continue

                day = {'day': daynumber}

                if isToday and (todayDay == daynumber):
                    day['today'] = True
                else:
                    day['today'] = False

                day['date'] = '%s-%s-%s' % (year, month, daynumber)

                if daynumber in events:
                    for event in events[daynumber]:
                        day['events'] = ' \n'.join(
                            [event.title for event in events[daynumber]])

                weekdata.append(day)

        return data

    def getCurrentDate(self):
        session = None
        request = self.request

        # First priority goes to the data in the REQUEST
        year = request.get('pyear', None)
        month = request.get('pmonth', None)

        # Next get the data from the SESSION
        if self.useSession:
            try:
                session = ISession(request)
            except:
                session = None

            if session is not None:
                data = session[sessionId]
                if not year:
                    year = data.get('year', None)
                if not month:
                    month = data.get('month', None)

        # Last resort to today
        if not year:
            year = self.now[0]
        if not month:
            month = self.now[1]

        year, month = int(year), int(month)

        # Store the results in the session for next time
        if session:
            data = session[sessionId]
            data['year'] = year
            data['month'] = month

        # Finally return the results
        return year, month

    def isToday(self, day):
        return (self.now[2]==day and
                self.now[1]==self.month and self.now[0]==self.year)

    def getWeekdays(self):
        firstDay = self.calendar.week['firstDay']-1
        days = self.calendar.getDayAbbreviations()
        return days[firstDay:] + days[:firstDay]
