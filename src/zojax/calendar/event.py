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
from zojax.content.type.item import PersistentItem
from zojax.richtext.field import RichTextProperty
from zope.schema.fieldproperty import FieldProperty

from interfaces import ICalendarEvent

class CalendarEvent(PersistentItem):
    interface.implements(ICalendarEvent)

    endDate = FieldProperty(ICalendarEvent['endDate'])
    startDate = FieldProperty(ICalendarEvent['startDate'])
    location = FieldProperty(ICalendarEvent['location'])
    attendees = FieldProperty(ICalendarEvent['attendees'])
    eventUrl = FieldProperty(ICalendarEvent['eventUrl'])
    contactName = FieldProperty(ICalendarEvent['contactName'])
    contactEmail = FieldProperty(ICalendarEvent['contactEmail'])
    contactPhone = FieldProperty(ICalendarEvent['contactPhone'])
    text = RichTextProperty(ICalendarEvent['text'])
    isAllDayEvent = FieldProperty(ICalendarEvent['isAllDayEvent'])
    recurringRule = FieldProperty(ICalendarEvent['recurringRule'])
    color = FieldProperty(ICalendarEvent['color'])

