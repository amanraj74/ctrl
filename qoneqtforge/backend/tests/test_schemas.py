"""Tests for Pydantic schemas — validates all data contracts."""

import pytest
from app.schemas import BriefSpec, Script, Beat, Scene, ScenePlan, CriticReport, QACheck, QAReport


class TestBriefSpec:
    def test_valid_brief(self):
        brief = BriefSpec(topic="AI in education")
        assert brief.topic == "AI in education"
        assert brief.language == "en"
        assert brief.duration_sec == 30

    def test_minimal_brief(self):
        brief = BriefSpec(topic="Test")
        assert brief.community == "general"
        assert brief.tone == "energetic"
        assert brief.visual_style == "cinematic"

    def test_all_options(self):
        brief = BriefSpec(
            topic="Startup funding trends",
            source_type="trend",
            community="startup",
            tone="inspiring",
            language="hi",
            duration_sec=45,
            voice="hi-IN-SwaraNeural",
            visual_style="photoreal",
        )
        assert brief.language == "hi"
        assert brief.duration_sec == 45


class TestScript:
    def test_valid_script(self):
        script = Script(
            title="Test Video",
            hook="This changes everything about AI",
            beats=[
                Beat(role="hook", text="This changes everything about AI."),
                Beat(role="context", text="The industry is shifting."),
                Beat(role="insight", text="New models are 10x faster."),
            ],
            cta="Join the discussion!",
            caption="AI is transforming everything. #AI #Tech",
            hashtags=["#AI", "#Tech", "#Innovation"],
            facts_used=["AI models improved 10x"],
        )
        assert len(script.beats) == 3
        assert len(script.hashtags) == 3


class TestScenePlan:
    def test_valid_scene_plan(self):
        plan = ScenePlan(
            style_prefix="cinematic, teal-orange grade",
            scenes=[
                Scene(idx=0, narration="Test narration 1", visual_prompt="A futuristic city",
                      motion="zoom_in", duration_sec=5.0),
                Scene(idx=1, narration="Test narration 2", visual_prompt="A tech lab",
                      motion="pan_left", duration_sec=4.0),
            ],
        )
        assert len(plan.scenes) == 2
        assert plan.scenes[0].motion == "zoom_in"


class TestCriticReport:
    def test_passing_report(self):
        report = CriticReport(
            scores={"hook": 9, "clarity": 8, "factuality": 9, "pacing": 8, "safety": 10, "community_fit": 8},
            overall=8.7,
            issues=[],
            must_fix=[],
            pass_=True,
        )
        assert report.pass_ is True

    def test_failing_report(self):
        report = CriticReport(
            scores={"hook": 5, "clarity": 6, "factuality": 7, "pacing": 6, "safety": 10, "community_fit": 6},
            overall=6.2,
            issues=["Weak hook"],
            must_fix=["Rewrite hook to be more specific"],
            pass_=False,
        )
        assert report.pass_ is False


class TestQAReport:
    def test_all_passed(self):
        report = QAReport(
            checks=[
                QACheck(name="Resolution", passed=True, expected="1080x1920", actual="1080x1920"),
                QACheck(name="Duration", passed=True, expected="30s", actual="29.5s"),
            ],
            all_passed=True,
        )
        assert report.all_passed is True
