# Social Content Workflow (for Amp to Execute)

## When I ask you to run this workflow:

### 1. Find Content Ideas
- Look in `agents-campaigns` repo for recent interesting work
- Check this thread for any insights worth sharing
- Ask me if I have specific topics in mind

### 2. Generate Posts
For each idea:
- Create LinkedIn version (professional, detailed, 2-3 paragraphs)
- Create X/Twitter version (concise, punchy, 1-2 tweets)
- Save in `drafts/[topic-name]-linkedin.md` and `drafts/[topic-name]-twitter.md`

### 3. Wait for My Review
- Tell me to review `drafts/` folder
- I'll edit or delete

### 4. Publish to Publer
- Read approved drafts from `drafts/`
- Use `src/publer/scheduler.py` to schedule posts
- Confirm what was scheduled

## Post Format Template

**LinkedIn:**
- Professional tone
- Include key insight + why it matters + lesson learned
- 2-4 relevant hashtags

**Twitter/X:**
- Technical but concise
- Lead with the insight
- Thread if needed (numbered)
- 1-2 hashtags max
