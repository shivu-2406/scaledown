import os
import unittest
from unittest.mock import patch, MagicMock
from scaledown.compressor.scaledown_compressor import ScaleDownCompressor
from scaledown.types.compressed_prompt import CompressedPrompt
from scaledown.exceptions import AuthenticationError

#this is an optional integration test that actually hits the network and uses api key
#for running with this:  SCALEDOWN_RUN_INTEGRATION=1 SCALEDOWN_API_KEY=... uv run python -m unittest discover tests
#else : uv run python -m unittest discover tests
class TestScaleDownIntegration(unittest.TestCase):
    """
    Real API tests. Skipped unless SCALEDOWN_RUN_INTEGRATION=1 is set.
    """
    @unittest.skipUnless(os.environ.get("SCALEDOWN_RUN_INTEGRATION"), "Skipping integration test")
    def test_live_api_call(self):
        # Ensure we have a key
        api_key = os.environ.get("SCALEDOWN_API_KEY")
        if not api_key:
            self.skipTest("No API key found in environment")

        compressor = ScaleDownCompressor(api_key=api_key, target_model="gpt-4o")
        context = "ScaleDown integration test context."
        prompt = "Shorten this."
        
        # This actually hits the network!
        result = compressor.compress(context, prompt)
        
        self.assertIsInstance(result, CompressedPrompt)
        self.assertTrue(len(result.content) > 0)
        self.assertGreater(result.metrics.latency_ms, 0)


class TestScaleDownCompressor(unittest.TestCase):
    def setUp(self):
        self.compressor = ScaleDownCompressor(api_key="test_key", target_model="gpt-4o")

    @patch('requests.post')
    def test_compress_single_success(self, mock_post):
        # 1. Setup Mock Response
        mock_response_data = {
            "results": {
                "compressed_prompt": "Compressed content",
                "original_prompt_tokens": 100,
                "compressed_prompt_tokens": 50,
                "request_metadata": {"timestamp": "2023-01-01T00:00:00Z"}
            },
            "latency_ms": 123,
            "model_used": "gpt-4o"
        }
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = mock_response_data

        # 2. Execute
        result = self.compressor.compress("context", "prompt")

        # 3. Assert Payload Structure
        args, kwargs = mock_post.call_args
        self.assertEqual(kwargs['headers']['x-api-key'], 'test_key')
        self.assertEqual(kwargs['json']['model'], 'gpt-4o')
        self.assertEqual(kwargs['json']['scaledown']['rate'], 'auto')

        # 4. Assert Result
        self.assertEqual(result.content, "Compressed content")
        self.assertEqual(result.metrics.original_prompt_tokens, 100)
        self.assertEqual(result.metrics.latency_ms, 123)

    @patch('requests.post')
    def test_compress_batch(self, mock_post):
        # Mocking for batch is tricky with ThreadPool, so we mock the response
        # to be returned for EACH call
        mock_response_data = {
            "results": {"compressed_prompt": "Batch content"}
        }
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = mock_response_data

        contexts = ["ctx1", "ctx2"]
        prompts = ["p1", "p2"]
        
        results = self.compressor.compress(contexts, prompts)
        
        self.assertEqual(len(results), 2)
        self.assertEqual(mock_post.call_count, 2)

    def test_missing_api_key_raises_error(self):
        # Ensure both env var and global getter return None
        with patch.dict(os.environ, {}, clear=True):
            with patch("scaledown.get_api_key", return_value=None):
                comp = ScaleDownCompressor(api_key=None)
                with self.assertRaises(AuthenticationError):
                    comp.compress("ctx", "prompt")

if __name__ == '__main__':
    unittest.main()
