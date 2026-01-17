# Agent Instructions

## Main Workflow
When user says "Read WORKFLOW_FOR_AMP.md and run it":
1. Read prompts from `prompts/` folder (user's content ideas)
2. Generate LinkedIn + Twitter posts, save to `drafts/`
3. Pause for user review
4. Publish approved drafts via Publer API

## Key Files
- **prompts/** - User writes content ideas here
- **drafts/** - You generate posts here (markdown files)
- **config/.env** - Publer API credentials (PUBLER_API_KEY, PUBLER_LINKEDIN_ACCOUNT_ID, PUBLER_X_ACCOUNT_ID)
- **WORKFLOW_FOR_AMP.md** - Full workflow instructions
- **src/publer/** - Reference code for Publer API (optional, you can use requests directly)

## Publer API
- Base URL: `https://app.publer.com/api/v1`
- Auth: `Authorization: Bearer-API {api_key}` header
- Schedule endpoint: `POST /posts/schedule` or `/posts/schedule/publish`
- See PUBLER_API_CAPABILITIES.md for full API details

## Post Format
- LinkedIn: Professional, 2-3 paragraphs, relevant hashtags
- Twitter/X: Concise, punchy, threads if needed, max 2 hashtags
