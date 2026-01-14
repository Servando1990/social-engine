# Social Engine (Minimal)

This is a small tool to capture ideas, generate drafts from your repos, and schedule posts to Publer.

## Quick Start

1. Copy environment file
2. Add your API key and account IDs
3. Run the scripts

"""bash
cp config/env.example .env
python scripts/01_validate_auth.py
python scripts/02_list_accounts.py
python scripts/03_generate_drafts.py
python scripts/04_schedule_posts.py --dry-run
"""

## Configuration

- `config/sources.yml` controls where content is pulled from
- `config/accounts.yml` stores account IDs for LinkedIn and X
- `config/schedule.yml` stores posting cadence and defaults

## Notes

- This project is intentionally small
- It favors control over full automation
- You can expand sources and formatting later
