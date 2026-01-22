"""Ingest ideas from various sources into ideas/ folder."""

import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path


def slugify(text: str) -> str:
    """Convert text to URL-friendly slug."""
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_]+', '-', text)
    text = re.sub(r'-+', '-', text)
    return text.strip('-')[:50]


def generate_idea_id(slug: str = "") -> str:
    """Generate timestamp-based idea ID."""
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%SZ")
    if slug:
        return f"{ts}__{slug}"
    return ts


def write_idea(
    ideas_dir: Path,
    idea_id: str,
    source: str,
    content: str,
    tags: list[str] | None = None,
    status: str = "ready",
) -> Path:
    """Write an idea file with frontmatter."""
    tags = tags or []
    created_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    
    frontmatter = f"""---
id: {idea_id}
source: {source}
status: {status}
tags: {tags}
created_at: {created_at}
---
"""
    ideas_dir.mkdir(parents=True, exist_ok=True)
    filepath = ideas_dir / f"{idea_id}.md"
    filepath.write_text(frontmatter + content.strip() + "\n")
    return filepath


def ingest_prompts(prompts_dir: Path, ideas_dir: Path) -> list[str]:
    """
    Read all .md files from prompts/ (skip README.md).
    Create an idea in ideas/ for each file.
    Returns list of created idea IDs.
    """
    created_ids = []
    
    if not prompts_dir.exists():
        return created_ids
    
    for md_file in prompts_dir.glob("*.md"):
        if md_file.name.lower() == "readme.md":
            continue
        
        content = md_file.read_text()
        slug = slugify(md_file.stem)
        idea_id = generate_idea_id(slug)
        source = f"prompts:{md_file.name}"
        
        write_idea(ideas_dir, idea_id, source, content)
        created_ids.append(idea_id)
    
    return created_ids


def ingest_transcripts(transcripts_dir: Path, ideas_dir: Path) -> list[str]:
    """
    Read all .md or .txt files from inputs/transcripts/.
    Split by headings or "---" separators.
    Each segment becomes an idea.
    Returns list of created idea IDs.
    """
    created_ids = []
    
    if not transcripts_dir.exists():
        return created_ids
    
    for file in list(transcripts_dir.glob("*.md")) + list(transcripts_dir.glob("*.txt")):
        content = file.read_text()
        
        # Split by --- or ## headings
        sections = re.split(r'\n---\n|(?=\n## )', content)
        sections = [s.strip() for s in sections if s.strip()]
        
        for idx, section in enumerate(sections):
            # Extract section title if present
            title_match = re.match(r'^##\s*(.+)', section)
            if title_match:
                section_name = slugify(title_match.group(1))
            else:
                section_name = f"section-{idx + 1}"
            
            slug = slugify(f"{file.stem}-{section_name}")
            idea_id = generate_idea_id(slug)
            source = f"transcripts:{file.name}#{section_name}"
            
            write_idea(ideas_dir, idea_id, source, section)
            created_ids.append(idea_id)
    
    return created_ids


def ingest_agents_campaigns(
    repo_path: Path,
    ideas_dir: Path,
    since_days: int = 7,
) -> list[str]:
    """
    Use git log to find recently changed files in the repo.
    Filter to .md files and important docs.
    Create idea stubs for each.
    Returns list of created idea IDs.
    """
    created_ids = []
    
    if not repo_path.exists():
        return created_ids
    
    try:
        result = subprocess.run(
            [
                "git", "log",
                f"--since={since_days} days ago",
                "--name-only",
                "--pretty=format:",
                "--diff-filter=AM",
            ],
            cwd=repo_path,
            capture_output=True,
            text=True,
            check=True,
        )
    except subprocess.CalledProcessError:
        return created_ids
    
    # Get unique files
    files = set()
    for line in result.stdout.strip().split("\n"):
        line = line.strip()
        if line and (line.endswith(".md") or line in ["README", "CHANGELOG"]):
            files.add(line)
    
    for rel_path in files:
        file_path = repo_path / rel_path
        if not file_path.exists():
            continue
        
        content = file_path.read_text()
        
        # Truncate if too long (keep first 2000 chars)
        if len(content) > 2000:
            content = content[:2000] + "\n\n[...truncated...]"
        
        slug = slugify(Path(rel_path).stem)
        idea_id = generate_idea_id(slug)
        source = f"agents:{rel_path}"
        
        write_idea(ideas_dir, idea_id, source, content, status="review")
        created_ids.append(idea_id)
    
    return created_ids


def ingest_all(
    workspace: Path,
    agents_repo: Path | None = None,
    since_days: int = 7,
) -> dict[str, list[str]]:
    """
    Run all ingestion sources and return summary.
    """
    ideas_dir = workspace / "ideas"
    
    results = {
        "prompts": ingest_prompts(workspace / "prompts", ideas_dir),
        "transcripts": ingest_transcripts(workspace / "inputs" / "transcripts", ideas_dir),
        "agents": [],
    }
    
    if agents_repo:
        results["agents"] = ingest_agents_campaigns(agents_repo, ideas_dir, since_days)
    
    return results
