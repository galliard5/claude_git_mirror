# claude_git_mirror

This repository contains campaign notes, worldbuilding documents, markdown-based content, and supporting AI-generated Python scripts for a solo RPG project.

## Primary workflow

- Keep the main narrative and reference material in `*.md` files.
- Use VS Code Markdown preview for writing and reviewing content.
- Mermaid diagrams are stored in Markdown code blocks and can be rendered with Mermaid preview extensions.
- Python scripts are available for support tasks but are not the core focus of the repo.

## Editing Markdown and Mermaid

- Open Markdown files in VS Code and use the built-in or extension-based preview pane.
- To preview Mermaid diagrams, install a Mermaid preview extension and use it in files with Mermaid code fences:

```md
```mermaid
flowchart TD
  A --> B
```
```

- Recommended VS Code extensions for this repo:
  - `Markdown All in One`
  - `Markdown Preview Enhanced`
  - `Mermaid Markdown Syntax Highlighting`
  - `GitHub Pull Requests and Issues`
  - `Git Graph`
  - `Better Comments`

## Collaboration and GitHub workflow

This repo is intended for solo work with optional collaboration from friends.

- Do most of your own editing directly on `main`.
- Ask collaborators to use feature branches or forks and submit pull requests.
- Review collaborator PRs before merging to keep `main` stable.
- Use the GitHub PR template in `.github/pull_request_template.md` for consistent submissions.

### Branch strategy

- `main` should contain reviewed and merged content.
- For larger additions or friend contributions, create a branch like `feature/<topic>`.
- Keep changes focused to one area per PR when possible.

## Branch protection recommendations

GitHub branch protection is managed through repository settings. Recommended rules for `main`:

- Require pull request reviews before merging.
- Require branch to be up to date before merging (optional but useful).
- Prevent force pushes.
- If you add automated checks later, require status checks to pass before merge.

These rules help prevent accidental direct commits to `main`, ensure review of collaborator changes, and keep the repo stable.

## Notes

- The `.vscode` folder contains editor settings and extension recommendations to make the repo easier to use.
- Your `.obsidian` workspace is excluded from Git, so only the repo content is tracked.
