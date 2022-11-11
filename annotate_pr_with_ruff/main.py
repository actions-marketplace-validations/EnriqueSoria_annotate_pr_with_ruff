#!/bin/python
import os

from .changeutils import get_changed_files
from .github_utils import get_diff
from .github_utils import submit_review
from .ruff import ruff


def main():
    owner = os.getenv("REPO_OWNER")
    repo = os.getenv("REPO_NAME")
    pr_number = int(os.getenv("PULL_REQUEST_NUMBER"))

    diff = get_diff(owner=owner, repo=repo, pr_number=pr_number)

    changed_files = get_changed_files(diff)

    ruff_errors = ruff()
    locations = {"/" + ruff_error.file.removeprefix("/") for ruff_error in ruff_errors}
    changed_files = {
        filename.removeprefix("/"): lines.intersection()
        for filename, lines in changed_files.items()
        if filename in locations
    }

    ruff_errors = [
        ruff_error
        for ruff_error in ruff_errors
        if ruff_error.line_number in changed_files.get(ruff_error.file, {})
    ]

    submit_review(owner=owner, repo=repo, pr_number=pr_number, errors=ruff_errors)


if __name__ == "__main__":
    main()
