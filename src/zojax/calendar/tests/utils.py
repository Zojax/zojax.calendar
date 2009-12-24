##############################################################################
#
# Copyright (c) 2009 Zope Foundation and Contributors.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Functional tests for zojax.filefield

"""
import os.path, shutil, tempfile

import transaction
from ZODB.DB import DB
from ZODB.DemoStorage import DemoStorage
from ZODB.blob import BlobStorage
from zope.testing import doctest
import zope.app.testing.functional
from zope.app.rotterdam import Rotterdam
from zope.app.component.hooks import setSite
from zope.app.intid import IntIds
from zope.app.intid.interfaces import IIntIds
from zope.app.testing.functional import getRootFolder
from zojax.layoutform.interfaces import ILayoutFormLayer


class IDefaultSkin(ILayoutFormLayer, Rotterdam):
    """ skin """


def setUp(test):
    root = getRootFolder()
    root['intids'] = IntIds()
    root['intids'].register(root)
    root.getSiteManager().registerUtility(root['intids'], IIntIds)


class FunctionalTestSetup(zope.app.testing.functional.FunctionalTestSetup):

    temp_dir_name = None

    def setUp(self):
        """Prepares for a functional test case."""
        # Tear down the old demo storage (if any) and create a fresh one
        transaction.abort()
        self.db.close()
        storage = DemoStorage("Demo Storage", self.base_storage)
        # make a dir
        temp_dir_name = self.temp_dir_name = tempfile.mkdtemp()
        # wrap storage with BlobStorage
        storage = BlobStorage(temp_dir_name, storage)
        self.db = self.app.db = DB(storage)
        self.connection = None

    def tearDown(self):
        """Cleans up after a functional test case."""
        transaction.abort()
        if self.connection:
            self.connection.close()
            self.connection = None
        self.db.close()
        # del dir named '__blob_test__%s' % self.name
        if self.temp_dir_name is not None:
            shutil.rmtree(self.temp_dir_name, True)
            self.temp_dir_name = None
        setSite(None)


class ZCMLLayer(zope.app.testing.functional.ZCMLLayer):

    def setUp(self):
        self.setup = FunctionalTestSetup(self.config_file)


def FunctionalDocFileSuite(*paths, **kw):
    if 'layer' in kw:
        layer = kw['layer']
        del kw['layer']
    else:
        layer = zope.app.testing.functional.Functional

    globs = kw.setdefault('globs', {})
    globs['http'] = zope.app.testing.functional.HTTPCaller()
    globs['getRootFolder'] = zope.app.testing.functional.getRootFolder
    globs['sync'] = zope.app.testing.functional.sync

    kw['package'] = doctest._normalize_module(kw.get('package'))

    kwsetUp = kw.get('setUp')
    def setUp(test):
        FunctionalTestSetup().setUp()

        if kwsetUp is not None:
            kwsetUp(test)
    kw['setUp'] = setUp

    kwtearDown = kw.get('tearDown')
    def tearDown(test):
        if kwtearDown is not None:
            kwtearDown(test)
        FunctionalTestSetup().tearDown()
    kw['tearDown'] = tearDown

    if 'optionflags' not in kw:
        old = doctest.set_unittest_reportflags(0)
        doctest.set_unittest_reportflags(old)
        kw['optionflags'] = (old
                             | doctest.ELLIPSIS
                             | doctest.NORMALIZE_WHITESPACE)

    suite = doctest.DocFileSuite(*paths, **kw)
    suite.layer = layer
    return suite
