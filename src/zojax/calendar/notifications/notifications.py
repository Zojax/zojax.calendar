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

from zope.lifecycleevent.interfaces import IObjectModifiedEvent
from zope.app.container.interfaces import IObjectAddedEvent, IObjectRemovedEvent

from zojax.ownership.interfaces import IOwnership
from zojax.content.type.interfaces import IDraftedContent
from zojax.subscription.interfaces import ISubscriptionDescription,\
    SubscriptionException
from zojax.content.notifications.utils import sendNotification
from zojax.content.notifications.notification import Notification

from zojax.calendar.interfaces import _, ICalendarEvent, ICalendarWorkspace
from interfaces import IEventNotification


class EventNotification(Notification):
    component.adapts(ICalendarWorkspace)
    interface.implementsOnly(IEventNotification)

    type = u'event'
    title = _(u'Calendar Events')
    description = _(u'Notification for Calendar Events')


class EventNotificationDescription(object):
    interface.implements(ISubscriptionDescription)

    title = _(u'Calendar Events')
    description = _(u'Notification for Calendar Events')


@component.adapter(ICalendarEvent, IObjectAddedEvent)
def CalendarEventAdded(object, ev):
    """ sends emails when the event is created """
    if IDraftedContent.providedBy(object):
        return

    principals = ()
    owner = IOwnership(object).owner.id
    attendees = object.attendees or None
    notification = component.getAdapter(object.__parent__, IEventNotification, 'event')

    if attendees:
        if owner not in attendees:
            principals += (owner, )
        principals += attendees

    if not attendees:
        principals += (owner, )

    #check subscribe
    for principal in principals:
        try:
            if not notification.isSubscribed(principal):
                notification.subscribe(principal)
        except SubscriptionException:
            pass

    # send notifications
    sendNotification('event', object, ev, principal={'any_of': principals})


@component.adapter(ICalendarEvent, IObjectModifiedEvent)
def CalendarEventModified(object, ev):
    """ sends emails when the event is modified """
    if IDraftedContent.providedBy(object):
        return

    principals = ()
    owner = IOwnership(object).owner.id
    attendees = object.attendees or None
    notification = component.getAdapter(object.__parent__, IEventNotification, 'event')

    if attendees:
        if owner not in attendees:
            principals += (owner, )
        principals += attendees

    if not attendees:
        principals += (owner, )

    #check subscribe
    for principal in principals:
        try:
            if not notification.isSubscribed(principal):
                notification.subscribe(principal)
        except SubscriptionException:
            pass

    # send notifications
    sendNotification('event', object, ev, principal={'any_of': principals})


@component.adapter(ICalendarEvent, IObjectRemovedEvent)
def CalendarEventRemoved(object, ev):
    """ sends emails when the event is removed """
    if IDraftedContent.providedBy(object):
        return

    principals = ()
    owner = IOwnership(object).owner.id
    attendees = object.attendees or None
    notification = component.getAdapter(object.__parent__, IEventNotification, 'event')

    if attendees:
        if owner not in attendees:
            principals += (owner, )
        principals += attendees

    if not attendees:
        principals += (owner, )

    # send notifications
    sendNotification('event', object, ev, principal={'any_of': principals})
