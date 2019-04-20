from datetime import datetime
import unittest
from unittest.mock import call, Mock

from xplenty import xplenty_api


class XplentyClientTestCase(unittest.TestCase):

    def setUp(self):
        self.client = xplenty_api.XplentyClient("foo", "bar")

    def test_api_is_bytes(self):
        self.assertEqual(type(self.client.api_key), type(b''))

    def test_add_auth_header(self):
        mock_request = Mock()

        self.client.add_auth_header(mock_request)

        mock_request.add_header.assert_called_once_with("Authorization", "Basic YmFy")
