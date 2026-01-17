#!/usr/bin/env python3
"""Ultra-simple workflow: extract → edit → publish."""

from pathlib import Path
import subprocess
import sys


def main() -> int:
    """Run the simple workflow with prompts."""
    print("\n🚀 Social Engine - Simple Workflow\n")
    
    # Step 1: Extract
    print("Step 1: Extract ideas from your repos and blog")
    response = input("Generate drafts? (y/n): ").lower()
    if response == 'y':
        print("\n📝 Generating drafts...")
        subprocess.run([sys.executable, "scripts/03_generate_drafts.py"])
        print("\n✅ Drafts created in drafts/\n")
    
    # Step 2: Edit
    print("Step 2: Edit your drafts")
    print(f"   → Open the drafts/ folder")
    print(f"   → Edit posts you like")
    print(f"   → Delete ones you don't want")
    input("\nPress Enter when done editing...")
    
    # Step 3: Publish
    print("\nStep 3: Publish to Publer")
    response = input("Schedule posts now? (y/n): ").lower()
    if response == 'y':
        print("\n📤 Scheduling posts...")
        subprocess.run([sys.executable, "scripts/04_schedule_posts.py"])
        print("\n✅ Done! Posts scheduled.\n")
    else:
        print("\n👋 Skipping publish. Run manually when ready.\n")
    
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
