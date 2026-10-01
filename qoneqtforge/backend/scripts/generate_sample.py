"""CLI script: generate a sample video from a topic.

Usage:
    cd backend
    python -m scripts.generate_sample "AI is changing education"
"""

from __future__ import annotations

import asyncio
import json
import sys
import uuid

# Ensure backend is on path
sys.path.insert(0, ".")

from app.schemas import BriefSpec


async def main(topic: str) -> None:
    print(f"\n{'='*60}")
    print(f"  QoneqtForge — Sample Generation")
    print(f"  Topic: {topic}")
    print(f"{'='*60}\n")

    job_id = str(uuid.uuid4())[:8]
    brief = BriefSpec(topic=topic)

    # Stage 1: Ingest
    print("▶ Stage 1: Ingest...")
    from app.stages import s01_ingest
    brief = await s01_ingest.run(job_id, brief)
    print(f"  ✓ Brief validated\n")

    # Stage 2: Research
    print("▶ Stage 2: Research...")
    from app.stages import s02_research
    research = await s02_research.run(job_id, brief)
    print(f"  ✓ {len(research.facts)} facts gathered")
    for fact in research.facts:
        print(f"    • {fact[:80]}")
    print()

    # Stage 3: Script
    print("▶ Stage 3: Script...")
    from app.stages import s03_script
    script = await s03_script.run(job_id, brief, research)
    print(f"  ✓ Hook: '{script.hook}'")
    print(f"  ✓ {len(script.beats)} beats")
    print(f"  ✓ Caption: {script.caption[:80]}")
    print()

    # Stage 4: Scenes
    print("▶ Stage 4: Scene Plan...")
    from app.stages import s04_scenes
    scene_plan = await s04_scenes.run(job_id, brief, script)
    print(f"  ✓ {len(scene_plan.scenes)} scenes planned")
    print(f"  ✓ Style: {scene_plan.style_prefix[:60]}")
    print()

    # Stage 5: Critic
    print("▶ Stage 5: Critic / Quality Gate...")
    from app.stages import s05_critic
    critic_report = await s05_critic.run(job_id, brief, script, scene_plan, research)
    print(f"  ✓ Overall: {critic_report.overall:.1f}/10")
    print(f"  ✓ Pass: {critic_report.pass_}")
    print(f"  ✓ Scores: {critic_report.scores}")
    if critic_report.issues:
        print(f"  ⚠ Issues: {critic_report.issues}")
    print()

    # Save all outputs
    from app.utils.paths import get_job_dir
    job_dir = get_job_dir(job_id)
    output = {
        "job_id": job_id,
        "brief": brief.model_dump(),
        "research": research.model_dump(),
        "script": script.model_dump(),
        "scene_plan": scene_plan.model_dump(),
        "critic_report": critic_report.model_dump(),
    }
    output_path = job_dir / "sample_output.json"
    with open(output_path, "w") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"{'='*60}")
    print(f"  ✓ Sample output saved to: {output_path}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    topic = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "AI is transforming education in India"
    asyncio.run(main(topic))
