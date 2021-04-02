from pathlib import Path
from unittest import TestCase

from ziggurat.template import Template, register_transform

FIXTURES_DIR = Path(__file__).parent / "fixtures"


class TemplateTestCases(TestCase):
    def tearDown(self):
        Template.transforms.pop("custom_transform", None)

    def test_render(self):
        template_path = str(FIXTURES_DIR / "greeting.txt")
        template = Template(template_path)
        self.assertEqual(template.render({"name": "World"}), "Hello World!")

    def test_render_with_escapes(self):
        # a slightly more complex template
        template_path = str(FIXTURES_DIR / "nginx.conf")
        template = Template(template_path)
        ctx = {
            "ssl": True,
            "host": "FOO.com",
            "locations": [
                {"path": "/", "sock": "http://unix:/run/foo.sock"},
                {"path": "/bar/", "sock": "http://unix:/run/bar.sock"},
            ],
        }

        self.assertEqual(
            template.render(ctx),
            """\
server {
    listen 443 ssl;

    server_name foo.com;

    location / {
        include proxy_params;
        proxy_pass http://unix:/run/foo.sock;
    }

    location /bar/ {
        include proxy_params;
        proxy_pass http://unix:/run/bar.sock;
    }

}
""",
        )

    def test_render_with_include(self):
        # @include basically invokes sub template rendering
        template_path = str(FIXTURES_DIR / "uses_include.txt")
        template = Template(template_path)
        ctx = {"foo": "bar", "bar": "foo"}
        self.assertEqual(
            template.render(ctx), "Some base with foo=bar\n\nand bar=foo\n"
        )

    def test_includes_registered_transforms(self):
        def custom_transform(value):
            return value[0]

        register_transform(custom_transform)

        template_path = str(FIXTURES_DIR / "transformed_greeting.txt")
        template = Template(template_path)
        self.assertEqual(template.render({"name": "World"}), "Hello W!")

    def test_bad_path(self):
        template_path = str(FIXTURES_DIR / "doesnt_exist.txt")
        with self.assertRaises(FileNotFoundError):
            Template(template_path)
