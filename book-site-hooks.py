"""Post-build step for the book site (see `hooks:` in mkdocs.yml).

MkDocs can only turn `index.md` or a root `README.md` into `index.html`, and
this repository can carry neither: a lowercase `index.md` next to `INDEX.md`
collides on case-insensitive filesystems (macOS, Windows by default), so a
clone would silently lose one of the two files. The table of contents therefore
stays `INDEX.ru.md`, and this hook writes the site root as a redirect to it.
"""

import pathlib

TARGET = "INDEX.ru/"

_REDIRECT = f"""<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<title>Освоение разработки через спецификации</title>
<link rel="canonical" href="{TARGET}">
<meta http-equiv="refresh" content="0; url={TARGET}">
</head>
<body>
<p>Открываю <a href="{TARGET}">оглавление курса</a>.</p>
</body>
</html>
"""


def on_post_build(config):
    """Write the root page after MkDocs has finished the site."""
    pathlib.Path(config["site_dir"], "index.html").write_text(_REDIRECT, encoding="utf-8")
