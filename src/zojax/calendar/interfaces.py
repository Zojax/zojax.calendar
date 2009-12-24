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
from zope import schema, interface
from zope.i18nmessageid import MessageFactory

_ = MessageFactory('zojax.calendar')


class EventDatesError(schema.interfaces.ValidationError):
    __doc__ = _("""Event dates are wrong.""")


class IEvent(interface.Interface):

    title = schema.TextLine(
        title = _(u'Title'),
        description = _(u'Event title.'),
        required = True)

    description = schema.Text(
        title = _(u'Description'),
        description = _(u'A short summary of the event.'),
        required = False)

    startDate = schema.Datetime(
        title = _('Event Starts'),
        required = True)

    endDate = schema.Datetime(
        title = _('Event Ends'),
        required = True)

    @interface.invariant
    def startEndDates(event):
        end = getattr(event, 'endDate', None)
        start = getattr(event, 'startDate', None)
        if (start is None or end is None) or (start >= end):
            raise EventDatesError()


class IEventLocation(interface.Interface):

    location = schema.TextLine(
        title = _('Event Location'),
        required = False)


class IEventType(interface.Interface):
    """ event content type """


class IEventsPortlet(interface.Interface):
    """ Upcoming events portlet """

    label = schema.TextLine(
        title = _(u'Label'),
        description = _('Custom label for events portlet.'),
        required = False)

    count = schema.Int(
        title = _(u'Count'),
        description = _(u'Number of events in portlet.'),
        default = 7,
        required = True)

    visibility = schema.Bool(
        title = _('Visibility'),
        description = _('All events are visible to all users.'),
        default = True,
        required = False)


class ICalendarPortlet(interface.Interface):
    """ Calendar portlet """

    useSession = schema.Bool(
        title = _(u'Use session'),
        description = _('Use session to store current year and month for portlet.'),
        default = True,
        required = False)

    visibility = schema.Bool(
        title = _('Visibility'),
        description = _('All events are visible to all users.'),
        default = True,
        required = False)


class ICalendar(interface.Interface):
    """ A tool for encapsulating how calendars work and are displayed """

    def getEvents(month, year, day=None, tz=None):
        """ list of events """



class ICalendarProduct(ICalendar):
    """ Calendar product """
