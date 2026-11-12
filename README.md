# LAUDEN organisation profile

This repository holds the page shown at
[github.com/lauden-io](https://github.com/lauden-io):

- `profile/README.md`: the page itself, with the LAUDEN logo in a light and
  a dark version;
- `scripts/update_repos.py`: rebuilds the "Public repositories" table from
  the GitHub API (standard library only);
- `.github/workflows/update-repos.yml`: runs it every day and commits the
  table when it changed. The only permission it has is to write this
  repository's contents, and its one action is pinned to a commit.

To change the page, edit `profile/README.md` outside the
`repos:start` / `repos:end` markers; the table between them is rewritten.
