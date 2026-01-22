"""Generate social media drafts from ideas."""

from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path


WORKSPACE_ROOT = Path(__file__).parent.parent
IDEAS_DIR = WORKSPACE_ROOT / "ideas"
DRAFTS_DIR = WORKSPACE_ROOT / "drafts"


def parse_frontmatter(content: str) -> tuple[dict, str]:
    """Parse frontmatter from markdown content.
    
    Returns (frontmatter_dict, body_content).
    """
    pattern = r"^---\s*\n(.*?)\n---\s*\n(.*)$"
    match = re.match(pattern, content, re.DOTALL)
    
    if not match:
        return {}, content
    
    frontmatter_raw = match.group(1)
    body = match.group(2)
    
    frontmatter = {}
    for line in frontmatter_raw.strip().split("\n"):
        if ":" in line:
            key, value = line.split(":", 1)
            frontmatter[key.strip()] = value.strip()
    
    return frontmatter, body


def write_frontmatter(frontmatter: dict, body: str) -> str:
    """Write frontmatter and body back to markdown format."""
    lines = ["---"]
    for key, value in frontmatter.items():
        lines.append(f"{key}: {value}")
    lines.append("---")
    lines.append(body)
    return "\n".join(lines)


def list_ideas(status: str = "ready") -> list[dict]:
    """Read all ideas from ideas/ folder, filter by status.
    
    Returns list of idea dicts with id, source, content, status.
    """
    ideas = []
    
    if not IDEAS_DIR.exists():
        return ideas
    
    for file_path in IDEAS_DIR.glob("*.md"):
        content = file_path.read_text()
        frontmatter, body = parse_frontmatter(content)
        
        idea_status = frontmatter.get("status", "ready")
        if status and idea_status != status:
            continue
        
        ideas.append({
            "id": file_path.stem,
            "source": frontmatter.get("source", ""),
            "content": body.strip(),
            "status": idea_status,
            "path": str(file_path),
        })
    
    return ideas


def generate_draft_linkedin(idea: dict) -> str:
    """Generate LinkedIn post content from an idea.
    
    This is a TEMPLATE/PLACEHOLDER - in real use, Amp or LLM would fill this.
    Returns the idea content with LinkedIn formatting hints.
    """
    content = idea.get("content", "")
    
    linkedin_post = f"""# LinkedIn Post

{content}

---
**LinkedIn Formatting Notes:**
- Professional tone, 2-3 paragraphs
- Add a hook in the first line
- Include a call-to-action
- Use 3-4 relevant hashtags

#Tech #Innovation #Development #Automation"""
    
    return linkedin_post


def generate_draft_twitter(idea: dict) -> str:
    """Generate Twitter/X post content from an idea.
    
    This is a TEMPLATE/PLACEHOLDER - in real use, Amp or LLM would fill this.
    Returns the idea content with Twitter formatting hints.
    """
    content = idea.get("content", "")
    
    if len(content) > 200:
        content = content[:200] + "..."
    
    twitter_post = f"""# Twitter/X Post

{content}

---
**Twitter Formatting Notes:**
- Concise and punchy
- Max 280 chars or use thread format
- 1-2 hashtags max

#Tech #Dev"""
    
    return twitter_post


def create_drafts_from_idea(
    idea_id: str, platforms: list[str] | None = None
) -> list[str]:
    """Create drafts for an idea across specified platforms.
    
    Args:
        idea_id: The idea filename stem (without .md)
        platforms: List of platforms to generate for. Defaults to ["linkedin", "twitter"]
    
    Returns list of created draft filenames.
    """
    if platforms is None:
        platforms = ["linkedin", "twitter"]
    
    idea_path = IDEAS_DIR / f"{idea_id}.md"
    if not idea_path.exists():
        raise FileNotFoundError(f"Idea not found: {idea_id}")
    
    content = idea_path.read_text()
    frontmatter, body = parse_frontmatter(content)
    
    idea = {
        "id": idea_id,
        "source": frontmatter.get("source", ""),
        "content": body.strip(),
        "status": frontmatter.get("status", "ready"),
    }
    
    DRAFTS_DIR.mkdir(parents=True, exist_ok=True)
    
    created_drafts = []
    now = datetime.now(timezone.utc)
    timestamp = now.strftime("%Y-%m-%dT%H:%M:%SZ")
    
    generators = {
        "linkedin": generate_draft_linkedin,
        "twitter": generate_draft_twitter,
    }
    
    for platform in platforms:
        if platform not in generators:
            continue
        
        draft_content = generators[platform](idea)
        
        draft_frontmatter = {
            "idea_id": idea_id,
            "platform": platform,
            "status": "draft",
            "created_at": timestamp,
        }
        
        draft_md = write_frontmatter(draft_frontmatter, draft_content)
        
        draft_filename = f"{idea_id}-{platform}.md"
        draft_path = DRAFTS_DIR / draft_filename
        draft_path.write_text(draft_md)
        
        created_drafts.append(draft_filename)
    
    frontmatter["status"] = "drafted"
    updated_idea = write_frontmatter(frontmatter, body)
    idea_path.write_text(updated_idea)
    
    return created_drafts


def list_drafts(status: str | None = None, platform: str | None = None) -> list[dict]:
    """Read all drafts from drafts/ folder with optional filters.
    
    Args:
        status: Filter by status (e.g., "draft", "approved")
        platform: Filter by platform (e.g., "linkedin", "twitter")
    
    Returns list of draft dicts with frontmatter fields and content.
    """
    drafts = []
    
    if not DRAFTS_DIR.exists():
        return drafts
    
    for file_path in DRAFTS_DIR.glob("*.md"):
        content = file_path.read_text()
        frontmatter, body = parse_frontmatter(content)
        
        draft_status = frontmatter.get("status", "draft")
        draft_platform = frontmatter.get("platform", "")
        
        if status and draft_status != status:
            continue
        if platform and draft_platform != platform:
            continue
        
        drafts.append({
            "filename": file_path.name,
            "path": str(file_path),
            "idea_id": frontmatter.get("idea_id", ""),
            "platform": draft_platform,
            "status": draft_status,
            "created_at": frontmatter.get("created_at", ""),
            "content": body.strip(),
        })
    
    return drafts


def approve_draft(draft_path: str) -> None:
    """Update draft frontmatter status to 'approved'.
    
    Args:
        draft_path: Path to the draft file (absolute or relative to DRAFTS_DIR)
    """
    path = Path(draft_path)
    if not path.is_absolute():
        path = DRAFTS_DIR / draft_path
    
    if not path.exists():
        raise FileNotFoundError(f"Draft not found: {draft_path}")
    
    content = path.read_text()
    frontmatter, body = parse_frontmatter(content)
    
    frontmatter["status"] = "approved"
    
    updated_content = write_frontmatter(frontmatter, body)
    path.write_text(updated_content)
