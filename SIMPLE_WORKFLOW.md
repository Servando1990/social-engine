# Super Simple Workflow

## 3 Steps Total

### Step 1: Extract Ideas
```bash
python scripts/03_generate_drafts.py
```
- Pulls from your repos and blog
- Creates draft files in `drafts/`

### Step 2: Edit Drafts
- Open `drafts/` folder
- Edit the posts you like
- Delete the ones you don't

### Step 3: Publish
```bash
python scripts/04_schedule_posts.py
```
- Sends drafts to Publer
- Posts go live immediately or scheduled

---

## That's It

Run step 1 whenever you want ideas. Edit. Publish.
