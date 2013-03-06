# -*- coding: utf-8 -*-
# Copyright (c) 2013  Infrae. All rights reserved.
# See also LICENSE.txt

import unittest
import transaction
import operator
from Products.Silva.EmailMessageService import EmailQueueTransaction
from Products.Silva.testing import FunctionalLayer

def sorter(col):
    return sorted(col, key=operator.itemgetter(0))


class EmailQueueTransactionTestCase(unittest.TestCase):

    layer = FunctionalLayer

    def setUp(self):
        self.email_queue = EmailQueueTransaction(transaction.manager)

    def test_add_some_emails(self):
        self.email_queue.enqueue_email('me', 'him', 'mail 1', 'content')
        self.email_queue.enqueue_email('me', 'him', 'mail 2', 'content')
        self.email_queue.enqueue_email('him', 'me', 'mail 3', 'content')
        aggregated = sorter(
            [('me', {'him': [('mail 3', 'content')]}),
             ('him', {'me': [('mail 1', 'content'),
                             ('mail 2', 'content')]})])
        self.assertEqual(aggregated, sorter(self.email_queue))

    def test_add_some_emails_in_a_savepoint(self):
        self.email_queue.enqueue_email('me', 'him', 'mail 1', 'content')
        self.email_queue.enqueue_email('him', 'me', 'mail 2', 'content')
        savepoint = self.email_queue.savepoint()
        self.email_queue.enqueue_email('me', 'him', 'mail 3', 'content')
        self.email_queue.enqueue_email('me', 'him', 'mail 4', 'content')
        self.email_queue.enqueue_email('him', 'me', 'mail 5', 'content')
        self.assertEqual(2, len(self.email_queue._queues))
        aggregated = sorter(
            [('me',
                {'him': [('mail 2', 'content'),
                         ('mail 5', 'content')]}),
             ('him',
                {'me': [('mail 1', 'content'),
                        ('mail 3', 'content'),
                        ('mail 4', 'content')]})])
        self.assertEqual(aggregated, sorter(self.email_queue))
        savepoint.rollback()
        aggregated = sorter(
            [('me', {'him': [('mail 2', 'content')]}),
             ('him', {'me': [('mail 1', 'content')]})])
        self.assertEqual(aggregated, sorter(self.email_queue))

    def test_empty_queue(self):
        self.email_queue.savepoint().rollback()
        self.assertEqual([self.email_queue._current_queue],
                          self.email_queue._queues)

    def test_empty_savepoint(self):
        self.email_queue.enqueue_email('me', 'him', 'mail 1', 'content')
        self.email_queue.savepoint().rollback()
        aggregated = [('him', {'me': [('mail 1', 'content')]})]
        self.assertEqual(aggregated, list(self.email_queue))
        self.assertEqual(2, len(self.email_queue._queues))
        self.assertEqual({}, self.email_queue._current_queue)
        self.assertEqual(self.email_queue._current_queue, self.email_queue._queues[-1])

    def test_savepoint_from_empty(self):
        savepoint = self.email_queue.savepoint()
        self.email_queue.enqueue_email('me', 'him', 'mail 1', 'content')
        savepoint.rollback()
        self.assertEqual([], list(self.email_queue))
        self.assertEqual([self.email_queue._current_queue],
                          self.email_queue._queues)
        self.assertEqual({}, self.email_queue._current_queue)

    def test_activation(self):
        self.email_queue.enqueue_email('me', 'him', 'mail 1', 'content')
        self.email_queue.deactivate()
        self.email_queue.enqueue_email('me', 'him', 'mail 2', 'content')
        self.email_queue.activate()
        self.email_queue.enqueue_email('him', 'me', 'mail 3', 'content')
        aggregated = [('him', {'me': [('mail 1', 'content')]}),
                      ('me', {'him': [('mail 3', 'content')]})]
        self.assertEqual(aggregated, sorter(self.email_queue))


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(EmailQueueTransactionTestCase))
    return suite
