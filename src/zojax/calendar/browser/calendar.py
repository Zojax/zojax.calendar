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

from zojax.catalog.interfaces import ICatalog
from zojax.resourcepackage.library import include
from zope.security.management import checkPermission


class ClendarView(object):

    hasEvents = True

    def update(self):
        include('jquery-wdcalendar')

        context = self.context
        request = self.request

        catalog = getUtility(ICatalog)

        results = catalog.searchResults(
            traversablePath = {'any_of': (context,)})

        if not results:
            self.hasEvents = False
            return

        self.events = results

    def checkEditing(self):
        return checkPermission('zojax.contenttype.AddCalendarEvent', self.context)
