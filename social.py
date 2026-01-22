#!/usr/bin/env python3
"""Social Engine CLI - Unified command interface for social media content workflow."""

import argparse
import sys
from datetime import datetime
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
load_dotenv(Path(__file__).parent / "config" / ".env")


def cmd_ingest(args):
    """Ingest ideas from various sources."""
    from src.ingest import ingest_prompts, ingest_transcripts, ingest_agents_campaigns
    
    source = args.source
    results = []
    
    if source == "prompts":
        prompts_dir = Path("prompts")
        created = ingest_prompts(prompts_dir)
        results.extend(created)
        print(f"✓ Ingested {len(created)} ideas from prompts/")
        
    elif source == "transcripts":
        transcripts_dir = Path(args.path) if args.path else Path("inputs/transcripts")
        created = ingest_transcripts(transcripts_dir)
        results.extend(created)
        print(f"✓ Ingested {len(created)} ideas from {transcripts_dir}")
        
    elif source == "agents":
        repo_path = Path(args.repo) if args.repo else Path.home() / "Servando/controlthrive/agents-campaigns"
        since_days = int(args.since.rstrip('d')) if args.since else 7
        created = ingest_agents_campaigns(repo_path, since_days)
        results.extend(created)
        print(f"✓ Ingested {len(created)} ideas from agents-campaigns (last {since_days} days)")
        
    elif source == "all":
        from src.ingest import ingest_all
        results = ingest_all()
        print(f"✓ Ingested {len(results)} ideas from all sources")
    
    if results:
        print("\nCreated ideas:")
        for idea_id in results[:10]:
            print(f"  - {idea_id}")
        if len(results) > 10:
            print(f"  ... and {len(results) - 10} more")


def cmd_draft(args):
    """Generate drafts from ideas."""
    from src.drafts import list_ideas, create_drafts_from_idea
    
    if args.idea:
        platforms = args.platform.split(",") if args.platform else ["linkedin", "twitter"]
        created = create_drafts_from_idea(args.idea, platforms)
        print(f"✓ Created {len(created)} drafts for idea {args.idea}")
        for draft in created:
            print(f"  - {draft}")
    
    elif args.batch:
        ideas = list_ideas(status="ready")
        limit = args.limit or len(ideas)
        ideas = ideas[:limit]
        
        if not ideas:
            print("No ideas with status 'ready' found.")
            return
        
        platforms = args.platform.split(",") if args.platform else ["linkedin", "twitter"]
        total_created = []
        
        for idea in ideas:
            created = create_drafts_from_idea(idea["id"], platforms)
            total_created.extend(created)
            print(f"✓ {idea['id']} → {len(created)} drafts")
        
        print(f"\n✓ Created {len(total_created)} total drafts from {len(ideas)} ideas")
    
    else:
        ideas = list_ideas(status="ready")
        print(f"Found {len(ideas)} ideas ready for drafting:")
        for idea in ideas[:10]:
            print(f"  - {idea['id']}: {idea.get('content', '')[:50]}...")
        if len(ideas) > 10:
            print(f"  ... and {len(ideas) - 10} more")
        print("\nUse --idea <id> or --batch to generate drafts")


def cmd_review(args):
    """List drafts for review."""
    from src.drafts import list_drafts, approve_draft
    
    if args.approve:
        approve_draft(args.approve)
        print(f"✓ Approved: {args.approve}")
        return
    
    status = args.status
    platform = args.platform
    
    drafts = list_drafts(status=status, platform=platform)
    
    if not drafts:
        print("No drafts found matching criteria.")
        return
    
    print(f"Drafts ({len(drafts)}):\n")
    for draft in drafts:
        status_icon = "✓" if draft.get("status") == "approved" else "○"
        platform_tag = f"[{draft.get('platform', '?')}]"
        print(f"  {status_icon} {platform_tag:12} {draft['path']}")
        if args.verbose:
            content = draft.get("content", "")[:100]
            print(f"              {content}...")
    
    print(f"\nTo approve: python social.py review --approve <path>")


def cmd_plan(args):
    """Create a schedule plan."""
    from src.planner import create_plan_from_approved, save_plan, load_plan
    from src.drafts import list_drafts
    
    if args.show:
        plan_path = Path(args.show) if args.show != "default" else Path("queue/plan.json")
        if plan_path.exists():
            plan = load_plan(plan_path)
            print(f"Plan: {plan_path}")
            print(f"Created: {plan.get('created_at', 'unknown')}")
            print(f"Items: {len(plan.get('items', []))}\n")
            for item in plan.get("items", []):
                print(f"  [{item.get('platform', '?'):8}] {item.get('scheduled_at', '?')} → {item.get('draft', '?')}")
        else:
            print(f"No plan found at {plan_path}")
        return
    
    platform = args.platform
    count = args.count
    start_date = args.start or datetime.now().strftime("%Y-%m-%d")
    start_time = args.time or "09:00"
    interval = args.every or 1
    
    if isinstance(interval, str):
        interval = int(interval.rstrip('d'))
    
    plan = create_plan_from_approved(
        platform=platform,
        count=count,
        start_date=start_date,
        start_time=start_time,
        interval_days=interval
    )
    
    if not plan.get("items"):
        print("No approved drafts found to plan.")
        print("Use 'python social.py review --approve <path>' to approve drafts first.")
        return
    
    plan_path = save_plan(plan)
    
    print(f"✓ Created plan with {len(plan['items'])} posts → {plan_path}")
    print("\nSchedule:")
    for item in plan["items"]:
        print(f"  [{item.get('platform', '?'):8}] {item.get('scheduled_at', '?')} → {Path(item.get('draft', '')).name}")
    
    print(f"\nReview and edit {plan_path}, then run:")
    print(f"  python social.py apply {plan_path}")


def cmd_apply(args):
    """Apply a schedule plan to Publer."""
    from src.planner import load_plan, apply_plan
    
    plan_path = Path(args.plan) if args.plan else Path("queue/plan.json")
    
    if not plan_path.exists():
        print(f"Plan not found: {plan_path}")
        print("Create one with: python social.py plan --from-approved")
        return
    
    plan = load_plan(plan_path)
    dry_run = args.dry_run
    
    if dry_run:
        print("=== DRY RUN ===\n")
    
    results = apply_plan(plan, dry_run=dry_run)
    
    successes = results.get("successes", [])
    failures = results.get("failures", [])
    
    if dry_run:
        print(f"\nWould schedule {len(plan.get('items', []))} posts.")
        print("Remove --dry-run to apply for real.")
    else:
        print(f"\n✓ Scheduled: {len(successes)}")
        if failures:
            print(f"✗ Failed: {len(failures)}")
            for f in failures:
                print(f"  - {f}")


def cmd_queue(args):
    """Manage the Publer queue."""
    from src.queue_manager import QueueManager
    
    qm = QueueManager()
    action = args.action
    
    if action == "ls":
        platform = args.platform
        posts = qm.list_scheduled(platform=platform)
        
        if not posts:
            print(f"No scheduled posts{' for ' + platform if platform else ''}.")
            return
        
        print(f"Scheduled posts ({len(posts)}):\n")
        for post in posts:
            plat = post.get("network", post.get("platform", "?"))
            scheduled = post.get("scheduled_at", "?")
            text = post.get("text", "")[:60]
            post_id = post.get("id", "?")
            print(f"  [{plat:8}] {scheduled}")
            print(f"            {text}...")
            print(f"            ID: {post_id}\n")
    
    elif action == "sync":
        result = qm.sync()
        print(f"✓ Synced queue from Publer")
        print(f"  LinkedIn: {result.get('linkedin', 0)} posts")
        print(f"  X/Twitter: {result.get('twitter', 0)} posts")
        print(f"  Saved to: state/publer_snapshot.json")
    
    elif action == "cancel":
        if not args.post_id:
            print("Usage: python social.py queue cancel <post_id>")
            return
        result = qm.cancel(args.post_id)
        if result.get("success"):
            print(f"✓ Cancelled post {args.post_id}")
        else:
            print(f"✗ Failed to cancel: {result.get('error', 'unknown')}")
    
    elif action == "move":
        if not args.post_id or not args.to:
            print("Usage: python social.py queue move <post_id> --to <datetime>")
            return
        result = qm.reschedule(args.post_id, args.to)
        if result.get("success"):
            print(f"✓ Rescheduled post {args.post_id} to {args.to}")
        else:
            print(f"✗ Failed to reschedule: {result.get('error', 'unknown')}")


def cmd_status(args):
    """Show overall status of the content pipeline."""
    from src.drafts import list_drafts, list_ideas
    from src.queue_manager import QueueManager
    
    ideas_ready = len(list_ideas(status="ready"))
    ideas_drafted = len(list_ideas(status="drafted"))
    
    drafts_pending = len(list_drafts(status="draft"))
    drafts_approved = len(list_drafts(status="approved"))
    
    drafts_linkedin = len(list_drafts(platform="linkedin"))
    drafts_twitter = len(list_drafts(platform="twitter"))
    
    print("=== Social Engine Status ===\n")
    print("Ideas:")
    print(f"  Ready to draft:  {ideas_ready}")
    print(f"  Already drafted: {ideas_drafted}")
    
    print("\nDrafts:")
    print(f"  Pending review:  {drafts_pending}")
    print(f"  Approved:        {drafts_approved}")
    print(f"  LinkedIn:        {drafts_linkedin}")
    print(f"  Twitter/X:       {drafts_twitter}")
    
    plan_path = Path("queue/plan.json")
    if plan_path.exists():
        import json
        plan = json.loads(plan_path.read_text())
        print(f"\nPlan:")
        print(f"  Items:           {len(plan.get('items', []))}")
    
    print("\nQueue (Publer):")
    try:
        qm = QueueManager()
        linkedin_posts = qm.list_scheduled(platform="linkedin")
        twitter_posts = qm.list_scheduled(platform="twitter")
        print(f"  LinkedIn:        {len(linkedin_posts)}")
        print(f"  Twitter/X:       {len(twitter_posts)}")
    except Exception as e:
        print(f"  (Could not fetch: {e})")
    
    print("\n---")
    print("Commands: ingest, draft, review, plan, apply, queue, status")


def main():
    parser = argparse.ArgumentParser(
        description="Social Engine - Ideas to Posts workflow",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python social.py ingest prompts              # Ingest from prompts/
  python social.py ingest transcripts          # Ingest from inputs/transcripts/
  python social.py ingest agents --since 7d   # Ingest from agents-campaigns
  
  python social.py draft --batch --limit 5     # Generate drafts for 5 ideas
  python social.py review                      # List drafts for review
  python social.py review --approve drafts/x.md
  
  python social.py plan --from-approved --platform linkedin --start tomorrow
  python social.py apply queue/plan.json --dry-run
  python social.py apply queue/plan.json
  
  python social.py queue ls --platform x       # View X queue
  python social.py queue ls --platform linkedin
  python social.py queue sync                  # Sync from Publer
  python social.py queue cancel <post_id>
  
  python social.py status                      # Overall pipeline status
"""
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # ingest
    ingest_parser = subparsers.add_parser("ingest", help="Ingest ideas from sources")
    ingest_parser.add_argument("source", choices=["prompts", "transcripts", "agents", "all"], 
                               help="Source to ingest from")
    ingest_parser.add_argument("--path", help="Path for transcripts")
    ingest_parser.add_argument("--repo", help="Path to agents-campaigns repo")
    ingest_parser.add_argument("--since", default="7d", help="How far back to look (e.g., 7d)")
    
    # draft
    draft_parser = subparsers.add_parser("draft", help="Generate drafts from ideas")
    draft_parser.add_argument("--idea", help="Specific idea ID to draft")
    draft_parser.add_argument("--batch", action="store_true", help="Draft all ready ideas")
    draft_parser.add_argument("--limit", type=int, help="Limit number of ideas to draft")
    draft_parser.add_argument("--platform", help="Platform(s) to draft for (comma-separated)")
    
    # review
    review_parser = subparsers.add_parser("review", help="Review and approve drafts")
    review_parser.add_argument("--status", help="Filter by status (draft, approved)")
    review_parser.add_argument("--platform", help="Filter by platform")
    review_parser.add_argument("--approve", help="Approve a specific draft")
    review_parser.add_argument("--verbose", "-v", action="store_true", help="Show content preview")
    
    # plan
    plan_parser = subparsers.add_parser("plan", help="Create a schedule plan")
    plan_parser.add_argument("--from-approved", action="store_true", help="Plan from approved drafts")
    plan_parser.add_argument("--platform", help="Filter by platform")
    plan_parser.add_argument("--count", type=int, help="Limit number of posts")
    plan_parser.add_argument("--start", help="Start date (YYYY-MM-DD or 'tomorrow')")
    plan_parser.add_argument("--time", help="Start time (HH:MM)")
    plan_parser.add_argument("--every", help="Interval between posts (e.g., 2d)")
    plan_parser.add_argument("--show", nargs="?", const="default", help="Show existing plan")
    
    # apply
    apply_parser = subparsers.add_parser("apply", help="Apply plan to Publer")
    apply_parser.add_argument("plan", nargs="?", help="Path to plan file")
    apply_parser.add_argument("--dry-run", action="store_true", help="Show what would be scheduled")
    
    # queue
    queue_parser = subparsers.add_parser("queue", help="Manage Publer queue")
    queue_parser.add_argument("action", choices=["ls", "sync", "cancel", "move"], 
                              help="Queue action")
    queue_parser.add_argument("post_id", nargs="?", help="Post ID for cancel/move")
    queue_parser.add_argument("--platform", help="Filter by platform")
    queue_parser.add_argument("--to", help="New datetime for move")
    
    # status
    subparsers.add_parser("status", help="Show pipeline status")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    commands = {
        "ingest": cmd_ingest,
        "draft": cmd_draft,
        "review": cmd_review,
        "plan": cmd_plan,
        "apply": cmd_apply,
        "queue": cmd_queue,
        "status": cmd_status,
    }
    
    cmd_func = commands.get(args.command)
    if cmd_func:
        try:
            cmd_func(args)
        except Exception as e:
            print(f"Error: {e}")
            if "--debug" in sys.argv:
                raise
            return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
