import secrets

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Generate a secure IndexNow API key."

    def add_arguments(self, parser) -> None:  # type: ignore[no-untyped-def]
        parser.add_argument(
            "--set",
            action="store_true",
            help="Also print a settings assignment line.",
        )

    def handle(self, *args, **options) -> None:  # type: ignore[no-untyped-def]
        key = secrets.token_hex(16)
        self.stdout.write(key)
        if options["set"]:
            self.stdout.write(f'INDEXNOW_API_KEY = "{key}"')
