from __future__ import unicode_literals, absolute_import, print_function, division

from django.test import TestCase


class TestProcessorMixin(TestCase):

    def test_hooks(self):
        self.skipTest("not tested")
        self.skipTest("test that async will return a Celery task")
        self.skipTest("test that sync will return a normal method")
        self.skipTest("test that proper args_type gets returned")
        #process, method = self.new.prepare_process(self.new.process)
        #self.assertIsInstance(process, HttpResourceProcessor)
        #self.assertTrue(callable(method))


class GeneratorAssertsMixin(object):

    def assert_generator_yields(self, generator, expected):
        for gen, exp in zip(generator, expected):
            if isinstance(exp, list):
                self.assert_generator_yields(gen, exp)
            else:
                self.assertEqual(gen, exp)
