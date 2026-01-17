# Social Content Workflow (for Amp to Execute)

## When I ask you to run this workflow:

### 1. Find Content Ideas
- Check `prompts/` folder for my content ideas
- Or look in `agents-campaigns` repo for recent work
- Or ask me for specific topics

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
- Use Publer API to schedule posts (credentials in config/.env)
- API: POST to `https://app.publer.com/api/v1/posts/schedule`
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
