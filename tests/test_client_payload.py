import json
from unittest.mock import Mock, patch

from django.test import SimpleTestCase, override_settings

from indexnow.client import _DEDUPE_CACHE, submit_url


class ClientPayloadTests(SimpleTestCase):
    def setUp(self) -> None:
        _DEDUPE_CACHE.clear()

    @override_settings(
        INDEXNOW_API_KEY="testkey",
        INDEXNOW_TIMEOUT=7,
        INDEXNOW_ENDPOINT="https://api.indexnow.org/indexnow",
        INDEXNOW_USER_AGENT="django-indexnow/test",
        INDEXNOW_DEDUPE_SECONDS=60,
    )
    @patch("indexnow.client.urlopen")
    @patch("indexnow.client.Site")
    def test_client_builds_expected_payload_and_headers(self, site_mock: Mock, urlopen_mock: Mock) -> None:
        site_mock.objects.get_current.return_value = Mock(domain="example.com")
        urlopen_mock.return_value.__enter__.return_value = Mock()

        submit_url("/path/")

        self.assertEqual(urlopen_mock.call_count, 1)
        request = urlopen_mock.call_args.args[0]
        timeout = urlopen_mock.call_args.kwargs["timeout"]

        self.assertEqual(request.get_method(), "POST")
        self.assertEqual(request.headers["Content-type"], "application/json; charset=utf-8")
        self.assertEqual(request.headers["User-agent"], "django-indexnow/test")
        self.assertEqual(timeout, 7)

        payload = json.loads(request.data.decode("utf-8"))
        self.assertEqual(
            payload,
            {
                "host": "example.com",
                "key": "testkey",
                "keyLocation": "https://example.com/testkey.txt",
                "urlList": ["https://example.com/path/"],
            },
        )

    @override_settings(
        INDEXNOW_API_KEY="testkey",
        INDEXNOW_DEDUPE_SECONDS=60,
    )
    @patch("indexnow.client.urlopen")
    @patch("indexnow.client.Site")
    def test_deduplication_skips_rapid_duplicate_submissions(
        self, site_mock: Mock, urlopen_mock: Mock
    ) -> None:
        site_mock.objects.get_current.return_value = Mock(domain="example.com")
        urlopen_mock.return_value.__enter__.return_value = Mock()

        submit_url("/same/")
        submit_url("/same/")

        self.assertEqual(urlopen_mock.call_count, 1)
