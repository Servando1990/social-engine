# How to Use Social Engine

## Daily Routine (5 minutes)

### 1. Generate Content Ideas
```bash
python scripts/03_generate_drafts.py
```
- Scans your repos and blog for interesting content
- Creates drafts in `drafts/` folder

### 2. Edit Drafts
- Open `drafts/` folder
- Edit/approve posts you like
- Delete ones you don't want

### 3. Schedule Posts
```bash
python scripts/04_schedule_posts.py
```
- Sends approved drafts to Publer
- Posts go live at scheduled times (LinkedIn 10am, X 2pm)

### 4. Check Performance (weekly)
```bash
python scripts/05_check_analytics.py
```
- See what's working
- Adjust your content strategy

## What Gets Posted

**From agents-campaigns:**
- Coding breakthroughs
- Architecture decisions  
- Problem-solving insights

**From website-blog:**
- Article summaries
- Key takeaways

**From Amp threads (future):**
- Interesting AI conversations
- Technical discoveries

## Content Flow

1. **Monday morning**: Run generate_drafts → get 5-10 ideas
2. **Review drafts**: Keep 3-5 best ones
3. **Schedule**: Queue for the week
4. **Friday**: Check analytics, adjust

## Tips

- LinkedIn gets longer, professional posts
- X gets concise, technical insights
- Edit drafts before scheduling (automation isn't perfect)
- Weekly analytics help you improve over time
