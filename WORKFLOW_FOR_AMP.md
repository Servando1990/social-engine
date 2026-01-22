# Social Content Workflow (for Amp)

## Quick Commands

```bash
python social.py status                    # See pipeline overview
python social.py ingest prompts            # Pull ideas from prompts/
python social.py draft --batch             # Generate drafts
python social.py review                    # List drafts
python social.py plan --from-approved      # Create schedule
python social.py apply queue/plan.json     # Publish to Publer
python social.py queue ls --platform x     # View queue
```

## Full Workflow

### 1. Ingest Ideas
Sources:
- `prompts/` - Raw ideas (markdown files)
- `inputs/transcripts/` - Meeting transcripts
- `agents-campaigns` repo - Recent work

```bash
python social.py ingest prompts
python social.py ingest transcripts
python social.py ingest agents --since 7d
```

### 2. Generate Drafts
```bash
python social.py draft --batch --limit 10
```
Creates `drafts/*-linkedin.md` and `drafts/*-twitter.md`

### 3. Review & Approve
User reviews drafts, then:
```bash
python social.py review --approve drafts/<filename>.md
```

### 4. Plan Schedule
```bash
python social.py plan --from-approved --start tomorrow --time "09:00" --every 2d
```
Creates `queue/plan.json` - user can edit for exact control.

### 5. Apply to Publer
```bash
python social.py apply queue/plan.json --dry-run   # Preview
python social.py apply queue/plan.json             # Publish
```

### 6. Manage Queue
```bash
python social.py queue ls --platform linkedin
python social.py queue ls --platform x
python social.py queue cancel <post_id>
```

## Post Format

**LinkedIn:**
- Professional tone
- 2-3 paragraphs
- Key insight + why it matters + lesson
- 3-4 hashtags

**Twitter/X:**
- Concise, punchy
- Lead with the insight
- Thread if needed
- 1-2 hashtags max

## Files

| Folder | Purpose |
|--------|---------|
| `prompts/` | Raw ideas you write |
| `ideas/` | Normalized ideas (auto) |
| `drafts/` | Generated posts (auto) |
| `queue/` | Schedule plans |
| `state/` | Event logs |
| `config/.env` | PUBLER_API_KEY |
