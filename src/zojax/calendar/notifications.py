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
from zope import interface, component

from zope.app.intid.interfaces import IIntIdAddedEvent
from zope.app.container.interfaces import IObjectAddedEvent
from zope.lifecycleevent.interfaces import IObjectModifiedEvent
from zope.app.container.interfaces import IObjectRemovedEvent
from zojax.content.draft.interfaces import IDraftPublishedEvent

from zojax.subscription.interfaces import ISubscriptionDescription
from zojax.content.notifications.utils import sendNotification
from zojax.content.notifications.notification import Notification

from interfaces import _, ICalendarEvent, ICalendarWorkspace, IEventNotification


class EventNotification(Notification):
    component.adapts(ICalendarWorkspace)
    interface.implementsOnly(IEventNotification)

    type = u'event'
    title = _(u'Calendar Event')
    description = _(u'Notification for Calendar Event')


class EventNotificationDescription(object):
    interface.implements(ISubscriptionDescription)

    title = _(u'Calendar Event')
    description = _(u'Notification for Calendar Event')


@component.adapter(ICalendarEvent, IObjectAddedEvent)
def CalendarEventAdded(object, ev):
    """ """
    attendees = object.attendees or None
    if attendees is not None:
        # ToDo: send notification for author?
        sendNotification('event', object, ev, principal={'any_of': attendees})


@component.adapter(ICalendarEvent, IObjectModifiedEvent)
def CalendarEventModified(object, ev):
    """ """


@component.adapter(ICalendarEvent, IObjectRemovedEvent)
def CalendarEventRemoved(object, ev):
    """ """
