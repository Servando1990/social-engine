# Social Engine

Unified CLI for social media content workflow: ideas → drafts → schedule → publish.

## Quick Start

```bash
# 1. Add your API key to config/.env
PUBLER_API_KEY=your_key_here

# 2. Check status
python social.py status
```

## Workflow

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  IDEAS IN   │───▶│   DRAFTS    │───▶│    PLAN     │───▶│   PUBLISH   │
│             │    │             │    │             │    │             │
│ prompts/    │    │ drafts/     │    │ queue/      │    │ Publer API  │
│ transcripts │    │ *-linkedin  │    │ plan.json   │    │ LinkedIn    │
│ agents repo │    │ *-twitter   │    │             │    │ X/Twitter   │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
     ingest            draft             plan              apply
```

## Commands

### 1. Ingest Ideas

```bash
python social.py ingest prompts              # From prompts/*.md
python social.py ingest transcripts          # From inputs/transcripts/
python social.py ingest agents --since 7d    # From agents-campaigns repo
python social.py ingest all                  # All sources
```

### 2. Generate Drafts

```bash
python social.py draft --batch               # All ready ideas → LinkedIn + X drafts
python social.py draft --batch --limit 5     # Limit to 5 ideas
python social.py draft --idea <id>           # Specific idea
```

### 3. Review & Approve

```bash
python social.py review                      # List all drafts
python social.py review -v                   # With content preview
python social.py review --approve drafts/my-post-linkedin.md
```

### 4. Plan Schedule

```bash
python social.py plan --from-approved                    # Default: tomorrow 9am, daily
python social.py plan --from-approved --platform linkedin
python social.py plan --from-approved --start 2026-01-25 --time "14:00" --every 2d
python social.py plan --show                             # View current plan
```

Edit `queue/plan.json` directly for full control over exact times.

### 5. Apply to Publer

```bash
python social.py apply queue/plan.json --dry-run   # Preview what will be scheduled
python social.py apply queue/plan.json             # Actually schedule posts
```

### 6. Manage Queue

```bash
python social.py queue ls --platform linkedin    # View LinkedIn queue
python social.py queue ls --platform x           # View X queue
python social.py queue sync                      # Refresh from Publer
python social.py queue cancel <post_id>          # Cancel a scheduled post
python social.py queue move <post_id> --to "2026-01-25T14:00:00Z"
```

### Status

```bash
python social.py status    # Overview of entire pipeline
```

## Folder Structure

```
social-engine/
├── prompts/           # Raw content ideas (you write these)
├── inputs/
│   └── transcripts/   # Meeting transcripts to extract ideas from
├── ideas/             # Normalized ideas (auto-generated)
├── drafts/            # LinkedIn + X post drafts (auto-generated)
├── queue/             # Schedule plans (plan.json)
├── state/             # Event logs, Publer snapshots
├── config/
│   └── .env           # PUBLER_API_KEY
└── social.py          # Main CLI
```

## Configuration

Only one env variable needed in `config/.env`:

```
PUBLER_API_KEY=your_api_key_here
```

The workspace ID and account IDs are fetched automatically from the API.

## Example Workflow

```bash
# 1. Drop a raw idea
echo "AI agents are changing how we build software" > prompts/ai-agents.md

# 2. Ingest it
python social.py ingest prompts

# 3. Generate drafts
python social.py draft --batch

# 4. Review and approve
python social.py review
python social.py review --approve drafts/ai-agents-linkedin.md
python social.py review --approve drafts/ai-agents-twitter.md

# 5. Plan the schedule
python social.py plan --from-approved --start tomorrow --time "09:00"

# 6. Publish
python social.py apply queue/plan.json --dry-run
python social.py apply queue/plan.json

# 7. Check what's queued
python social.py queue ls --platform linkedin
python social.py queue ls --platform x
```
