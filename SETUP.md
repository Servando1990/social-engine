# Quick Setup

## Current Content Sources

✅ **agents-campaigns repo** - Markdown files (active)
🔜 **Amp threads** - Your AI interactions (needs implementation)

## Test It Now

```bash
# 1. Generate drafts from your agents-campaigns repo
python scripts/03_generate_drafts.py

# 2. Check drafts folder
ls -la drafts/

# 3. Edit drafts you like, delete others

# 4. Publish (with dry-run first)
python scripts/04_schedule_posts.py --dry-run
```

## Next: Add Amp Threads

To pull from your Amp conversations, we need to implement `src/sources/amp_threads.py`.

This would extract insights from threads like this one to create social posts.
