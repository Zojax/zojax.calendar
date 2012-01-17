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
from pytz import timezone

from zope.component import getUtility
from zope.security.management import checkPermission

from zojax.catalog.interfaces import ICatalog
from zope.traversing.browser import absoluteURL
from zojax.formatter.interfaces import IFormatterConfiglet
from zojax.resourcepackage.library import include, includeInplaceSource

from zojax.calendar.browser.jsapi import timezoneToJs


class ClendarView(object):

    hasEvents = True

    def update(self):
        context = self.context
        request = self.request

        configlet = getUtility(IFormatterConfiglet)
        tz = timezone(configlet.timezone)
        if tz:
            # difference between timezone in user's browser and formatter settings
            timeZone = '(new Date().getTimezoneOffset() / 60 * -1) - %s'%timezoneToJs(tz)
        else:
            timeZone = str('new Date().getTimezoneOffset() / 60 * -1')

        calendarUrl = u'%s'%absoluteURL(context, request)
        readonly = self.checkEditing() and 'false' or 'true'
        includeInplaceSource(jssource%{
                'calendarUrl': calendarUrl,
                'readonly': readonly,
                'timezone': timeZone,
                }, ('jquery-wdcalendar', 'zojax-calendar-js',))

        catalog = getUtility(ICatalog)

        results = catalog.searchResults(
            traversablePath = {'any_of': (context,)})

        if not results:
            self.hasEvents = False
            return

        self.events = results

    def checkEditing(self):
        return checkPermission('zojax.contenttype.AddCalendarEvent', self.context)

jssource = """<script type="text/javascript">
        var Calendar_URL = '%(calendarUrl)s/';
        var CalendarAPI_URL = '%(calendarUrl)s/CalendarAPI/';
        var CalendarAPI_readonly = %(readonly)s;
        var userTimezone = %(timezone)s;
</script>"""
