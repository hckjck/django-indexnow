from django.test import SimpleTestCase, override_settings


class KeyEndpointTests(SimpleTestCase):
    @override_settings(INDEXNOW_API_KEY="abc123")
    def test_key_endpoint_returns_plain_text_key(self) -> None:
        response = self.client.get("/indexnow/key.txt")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "text/plain; charset=utf-8")
        self.assertEqual(response.content, b"abc123\n")

    @override_settings(INDEXNOW_API_KEY="")
    def test_key_endpoint_disabled_without_key(self) -> None:
        response = self.client.get("/indexnow/key.txt")
        self.assertEqual(response.status_code, 404)
