# Social Engine (Amp-Powered)

Dead simple social media content workflow powered by Amp AI.

## How It Works

1. **Write prompts** → Create markdown files in `prompts/` with content ideas
2. **Run Amp** → Tell Amp: "Read WORKFLOW_FOR_AMP.md and run it"
3. **Review** → Check generated posts in `drafts/`
4. **Publish** → Amp schedules to Publer (LinkedIn + X/Twitter)

## Setup

```bash
cp config/env.example .env
# Add your Publer API credentials
```

## Usage

```bash
# Start Amp and say:
"Read WORKFLOW_FOR_AMP.md and run it"
```

That's it. No Python scripts to run.

## What's What

- `prompts/` - Your content ideas (you write these)
- `drafts/` - Generated posts (Amp creates these)
- `config/` - API credentials and account settings
- `WORKFLOW_FOR_AMP.md` - Instructions for Amp to execute
