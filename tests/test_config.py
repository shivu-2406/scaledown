import unittest
import os
from unittest.mock import patch
from scaledown.compressor.config import get_api_url, default_scaledown_api

class TestConfig(unittest.TestCase):
    def test_get_api_url_default(self):
        # Ensure environment variable is NOT set
        with patch.dict(os.environ, {}, clear=True):
            self.assertEqual(get_api_url(), default_scaledown_api)

    def test_get_api_url_env_var(self):
        # Mock environment variable
        test_url = "https://custom.api.com"
        with patch.dict(os.environ, {"SCALEDOWN_API_URL": test_url}):
            self.assertEqual(get_api_url(), test_url)

