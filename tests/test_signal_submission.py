from unittest.mock import patch

from django.test import SimpleTestCase, override_settings

from indexnow.signals import indexnow


class SignalSubmissionTests(SimpleTestCase):
    @override_settings(INDEXNOW_API_KEY="testkey")
    @patch("indexnow.signals.submit_url")
    @patch("indexnow.signals.get_site_base_url", return_value="https://example.com")
    def test_signal_dispatch_triggers_submission(self, _site_mock, submit_mock) -> None:
        indexnow.send(sender=self.__class__, url="/blog/post/")
        submit_mock.assert_called_once_with("https://example.com/blog/post/")

    @override_settings(INDEXNOW_API_KEY="")
    @patch("indexnow.signals.submit_url")
    def test_signal_noop_when_disabled(self, submit_mock) -> None:
        indexnow.send(sender=self.__class__, url="/blog/post/")
        submit_mock.assert_not_called()
