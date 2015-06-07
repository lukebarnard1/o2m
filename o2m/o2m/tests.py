
import unittest

class TestTautologies(unittest.TestCase):

	def test_true(self):
		'''Make sure that True really is True'''
		self.assertTrue(True)

	def test_false(self):
		'''Make sure that False really is False'''
		self.assertFalse(False)