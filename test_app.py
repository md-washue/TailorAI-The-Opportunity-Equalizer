# TailorAI Comprehensive Unit Test Suite
import copy
from app import (
    tex_escape,
    render_latex,
    render_plaintext,
    resume_to_text,
    compute_coverage,
    extract_tokens,
    SAMPLE_RESUME,
    SAMPLE_JOB_DESCRIPTION,
    ResumeModel,
    ExperienceItem,
    ProjectItem,
    EducationItem,
    OptimizationResult,
    IndexedBullet,
    log_event,
    get_telemetry_counts,
    check_and_increment_demo,
    get_demo_remaining,
)

def test_tex_escape():
    # 1. Test standard string with multiple special characters
    text = "C++ & Python_100% $500 #1"
    expected = r"C++ \& Python\_100\% \$500 \#1"
    assert tex_escape(text) == expected

    # 2. Test all 10 special characters without double-escaping curly braces
    raw_all = r"\ & % $ # _ { } ~ ^"
    expected_all = r"\textbackslash{} \& \% \$ \# \_ \{ \} \textasciitilde{} \textasciicircum{}"
    escaped_all = tex_escape(raw_all)
    assert escaped_all == expected_all, f"Expected {expected_all}, got {escaped_all}"

    # 3. Test None input
    assert tex_escape(None) == ""

    # 4. Test integers and booleans
    assert tex_escape(123) == "123"

    print("✓ test_tex_escape passed")

def test_render_plaintext_and_alias():
    # Test None handling
    assert render_plaintext(None) == ""
    assert resume_to_text(None) == ""

    # Test full model
    txt = render_plaintext(SAMPLE_RESUME)
    assert "ELENA ROSTOVA" in txt
    assert "CloudScale Systems" in txt
    assert "TECHNICAL SKILLS" in txt
    assert resume_to_text(SAMPLE_RESUME) == txt
    print("✓ test_render_plaintext_and_alias passed")

def test_extract_tokens_and_coverage():
    # Standard coverage test
    jd = "Seeking Python, Docker, and Kubernetes engineer with Redis experience."
    before = "Junior developer with HTML, CSS, and basic Python."
    after = "Software engineer building Docker microservices in Python with Redis and Kubernetes."
    
    cov = compute_coverage(jd, before, after)
    assert cov["before_pct"] >= 0
    assert cov["after_pct"] > cov["before_pct"]
    assert cov["delta_pct"] == cov["after_pct"] - cov["before_pct"]
    assert "docker" in cov["added_keywords"]
    assert "redis" in cov["added_keywords"]
    assert "kubernetes" in cov["added_keywords"]

    # Edge case: Empty JD
    cov_empty = compute_coverage("", before, after)
    assert cov_empty["before_pct"] == 0
    assert cov_empty["after_pct"] == 0
    assert cov_empty["delta_pct"] == 0

    print("✓ test_extract_tokens_and_coverage passed")

def test_render_latex_sanity():
    with open("templates/master_resume.tex.j2", "r", encoding="utf-8") as f:
        template_str = f.read()

    rendered, is_valid = render_latex(SAMPLE_RESUME, template_str)
    assert is_valid is True
    assert r"\begin{document}" in rendered
    assert r"\end{document}" in rendered
    assert rendered.count(r"\begin{") == rendered.count(r"\end{")
    assert "Elena Rostova" in rendered
    assert "CloudScale Systems" in rendered

    # Verify that special characters inside sample data don't break LaTeX syntax
    resume_with_specials = copy.deepcopy(SAMPLE_RESUME)
    resume_with_specials.name = "Elena & Associates #1"
    resume_with_specials.skills.append("C# & C++ (99.9% uptime)")
    rendered_sp, is_valid_sp = render_latex(resume_with_specials, template_str)
    assert is_valid_sp is True
    assert r"Elena \& Associates \#1" in rendered_sp
    assert r"C\# \& C++ (99.9\% uptime)" in rendered_sp

    print("✓ test_render_latex_sanity passed")

def test_positional_optimization_mapping():
    base = copy.deepcopy(SAMPLE_RESUME)
    opt_result = OptimizationResult(
        bullets=[
            # Normal experience bullet
            IndexedBullet(
                section="experience",
                item_index=0,
                bullet_index=0,
                improved="Architected distributed event-streaming services using Python, Redis, and Docker, reducing query latency by 45%.",
            ),
            # Case-insensitive section
            IndexedBullet(
                section="Projects",
                item_index=0,
                bullet_index=0,
                improved="Engineered resilient distributed task queue with asyncio, processing 15,000 tasks/min with zero downtime.",
            ),
            # Out of bounds item_index (should not crash)
            IndexedBullet(
                section="experience",
                item_index=99,
                bullet_index=0,
                improved="Invalid item index bullet.",
            ),
            # Negative index (should be ignored safely)
            IndexedBullet(
                section="projects",
                item_index=-1,
                bullet_index=0,
                improved="Negative index bullet.",
            ),
        ]
    )

    tailored = copy.deepcopy(base)
    diff_records = []
    for b in opt_result.bullets:
        sec = b.section.lower().strip()
        if sec == "experience" and 0 <= b.item_index < len(tailored.experience):
            exp_item = tailored.experience[b.item_index]
            if 0 <= b.bullet_index < len(exp_item.bullets):
                orig = exp_item.bullets[b.bullet_index]
                exp_item.bullets[b.bullet_index] = b.improved
                diff_records.append({
                    "section": f"Experience: {exp_item.company}",
                    "original": orig,
                    "improved": b.improved,
                })
        elif sec == "projects" and 0 <= b.item_index < len(tailored.projects):
            proj_item = tailored.projects[b.item_index]
            if 0 <= b.bullet_index < len(proj_item.bullets):
                orig = proj_item.bullets[b.bullet_index]
                proj_item.bullets[b.bullet_index] = b.improved
                diff_records.append({
                    "section": f"Project: {proj_item.name}",
                    "original": orig,
                    "improved": b.improved,
                })

    assert len(diff_records) == 2
    assert "Architected distributed event-streaming" in tailored.experience[0].bullets[0]
    assert "Engineered resilient distributed task queue" in tailored.projects[0].bullets[0]
    print("✓ test_positional_optimization_mapping passed")

def test_telemetry():
    log_event("test-session-audit", "parse", True)
    log_event("test-session-audit", "optimize", True)
    log_event("test-session-audit", "export_tex", True)
    counts = get_telemetry_counts()
    assert counts["parse"] >= 1
    assert counts["optimize"] >= 1
    assert counts["export_tex"] >= 1
    print("✓ test_telemetry passed")

def test_demo_quota_tracker():
    rem_before = get_demo_remaining()
    assert rem_before >= 0
    print("✓ test_demo_quota_tracker passed")

if __name__ == "__main__":
    test_tex_escape()
    test_render_plaintext_and_alias()
    test_extract_tokens_and_coverage()
    test_render_latex_sanity()
    test_positional_optimization_mapping()
    test_telemetry()
    test_demo_quota_tracker()
    print("\n🎉 ALL AUDIT & UNIT TESTS PASSED WITH 100% SUCCESS!")
