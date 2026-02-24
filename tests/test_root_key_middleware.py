from django.test import SimpleTestCase, override_settings


class RootKeyMiddlewareTests(SimpleTestCase):
    @override_settings(INDEXNOW_API_KEY="deadbeef")
    def test_root_key_file_is_served_by_middleware(self) -> None:
        response = self.client.get("/deadbeef.txt")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "text/plain; charset=utf-8")
        self.assertEqual(response.content, b"deadbeef\n")

    @override_settings(INDEXNOW_API_KEY="")
    def test_root_key_file_is_disabled_without_key(self) -> None:
        response = self.client.get("/anything.txt")
        self.assertEqual(response.status_code, 404)
