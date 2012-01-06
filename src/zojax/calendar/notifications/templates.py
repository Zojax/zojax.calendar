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
from zojax.mail.interfaces import IMailer
"""

$Id$
"""
import types
from datetime import date
from email.Utils import formataddr

from zope import interface, component
from zope.proxy import removeAllProxies
from zope.component import getUtility, queryMultiAdapter
from zope.traversing.browser import absoluteURL
from zope.app.component.hooks import getSite
from zope.size.interfaces import ISized
from zope.app.intid.interfaces import IIntIds
from zope.dublincore.interfaces import IDCTimes
from zope.schema.interfaces import IVocabularyFactory

from zojax.ownership.interfaces import IOwnership
from zojax.assignment.interfaces import IAssignments
from zojax.workflow.interfaces import IWorkflowState
from zojax.principal.profile.interfaces import IPersonalProfile
from zojax.authentication.utils import getPrincipal
from zojax.personal.space.interfaces import IPersonalSpace

from zojax.calendar.interfaces import ICalendarEvent


class EventNotification(object):

    def update(self):
        super(EventNotification, self).update()

        context = removeAllProxies(self.context)
        request = self.request
        principal = self.request.principal
        ids = getUtility(IIntIds)

        self.name = context.__name__

        mailer = getUtility(IMailer)

        profile = IPersonalProfile(principal, None)
        if profile is not None and profile.email:
            author = profile.title
            self.author = author
            self.addHeader(u'To', formataddr((author, profile.email),))
        else:
            self.author = principal.title or principal.id

        self.addHeader(u'From', formataddr((self.author, mailer.email_from_address),))

        self.addHeader(u'In-Reply-To', u'<%s@zojax.com>'%ids.getId(context))

        self.url = u'%s/'%absoluteURL(context, request)
        self.title = u'%s'%context.title
        self.calendar = context.__parent__

        # calendar
        self.calendarUrl = u'%s/'%absoluteURL(self.calendar, request)

        # owner
        self.owner = IOwnership(context).owner

        members = []
        for memeber in context.attendees:
            principal = getPrincipal(memeber)
            oneMember = {}

            homeFolder = IPersonalSpace(principal, None)
            profileUrl = homeFolder is not None \
                and '%s/profile/'%absoluteURL(homeFolder, request) or ''

            oneMember["url"] = profileUrl
            oneMember["title"] = principal.title
            members.append(oneMember)

        info = {
            'event': context,
            'sdDate': context.startDate.strftime('%m/%d/%Y'),
            'sdTime': context.startDate.strftime('%H:%M'),
            'edDate': context.endDate.strftime('%m/%d/%Y'),
            'edTime': context.endDate.strftime('%H:%M'),
            'members': members}

        self.info = info


    def text(self):
        text = getattr(self.context.text,'cooked', '')

        if u'src="@@content.attachment/' in text:
            s = u'src="%s/@@content.attachment/'%absoluteURL(
                getSite(), self.request)
            text = text.replace(u'src="@@content.attachment/', s)

        return text


class EventAddedNotification(EventNotification):

    @property
    def subject(self):
        return u'Event created "%s"'%self.context.title


class EventModifiedNotification(EventNotification):

    @property
    def subject(self):
        return u'Event modified "%s"'%self.context.title


class EventDeletedNotification(object):

    def update(self):
        super(EventDeletedNotification, self).update()

        context = removeAllProxies(self.context)
        request = self.request
        principal = self.request.principal

        self.name = context.__name__

        mailer = getUtility(IMailer)

        profile = IPersonalProfile(principal, None)
        if profile is not None and profile.email:
            author = profile.title
            self.author = author
            self.addHeader(u'To', formataddr((author, profile.email),))
        else:
            self.author = principal.title or principal.id

        self.addHeader(u'From', formataddr((self.author, mailer.email_from_address),))

        self.url = '%s/'%absoluteURL(context, request)
        self.calendar = context.__parent__

        # calendar
        self.calendarUrl = u'%s/'%absoluteURL(self.calendar, request)

    @property
    def subject(self):
        return u'Event deleted "%s"'%(self.context.title)
