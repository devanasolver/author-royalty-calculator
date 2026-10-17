"""kdp new - start a book project folder."""

import json
import os

MANUSCRIPT = """# Chapter One

Write your first paragraph here. A blank line starts a new paragraph.
Use *italic* and **bold** where you need them.

***

A line of three stars makes a scene break.

# Chapter Two

Chapters always start on a right-hand page, like a real book.
"""

METADATA = {
    "title": "My Book",
    "subtitle": "",
    "author": "Your Name",
    "description": "Two or three short paragraphs that make a reader click Buy.",
    "keywords": ["", "", "", "", "", "", ""],
    "categories": [],
    "language": "en",
    "ai_generated": False,
}

README = """# {title}

Made with kdp-toolkit. The loop:

```bash
kdp interior manuscript.md --title "{title}" --author "{author}"
kdp validate interior.pdf
kdp cover --title "{title}" --author "{author}" --pages <pages from step 1>
kdp validate cover.pdf --cover --pages <pages>
kdp metadata metadata.json
```

Then upload interior.pdf and cover.pdf at kdp.amazon.com and paste the
metadata from metadata.json. Full walkthrough:
https://github.com/devanasolver/kdp-toolkit
"""


def new_project(folder, title, author):
    os.makedirs(folder, exist_ok=True)
    paths = {
        "manuscript.md": MANUSCRIPT,
        "metadata.json": json.dumps({**METADATA, "title": title,
                                     "author": author}, indent=2),
        "README.md": README.format(title=title, author=author),
    }
    for name, content in paths.items():
        p = os.path.join(folder, name)
        if not os.path.exists(p):
            with open(p, "w", encoding="utf-8") as f:
                f.write(content)
    return sorted(paths)
