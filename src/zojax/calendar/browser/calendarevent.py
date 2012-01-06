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
from zope.component import getUtility

from zojax.personal.space.interfaces import IPersonalSpace
from zojax.authentication.utils import getPrincipal
from zope.traversing.browser import absoluteURL


class ClendarEventView(object):

    def update(self):

        context = self.context
        request = self.request

    def getMemberInfo(self, attendees):
        if attendees is None:
            return

        members = []
        for member in attendees:
            principal = getPrincipal(member)
            oneMember = {}

            homeFolder = IPersonalSpace(principal, None)
            profileUrl = homeFolder is not None \
                and '%s/profile/'%absoluteURL(homeFolder, self.request) or ''

            oneMember["url"] = profileUrl
            oneMember["title"] = principal.title
            members.append(oneMember)

        return members
