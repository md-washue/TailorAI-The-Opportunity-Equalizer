# TailorAI Unit Tests
from app import (
    tex_escape,
    render_latex,
    render_plaintext,
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
)

def test_tex_escape():
    # Test characters per AGENT.md Section 6.4 specification
    text = "C++ & Python_100% $500 #1"
    expected = r"C++ \& Python\_100\% \$500 \#1"
    assert tex_escape(text) == expected
    print("✓ test_tex_escape passed")

def test_extract_tokens_and_coverage():
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
    print("✓ test_render_latex_sanity passed")

def test_render_plaintext():
    txt = render_plaintext(SAMPLE_RESUME)
    assert "ELENA ROSTOVA" in txt
    assert "CloudScale Systems" in txt
    assert "TECHNICAL SKILLS" in txt
    print("✓ test_render_plaintext passed")

def test_telemetry():
    log_event("test-session-xyz", "parse", True)
    log_event("test-session-xyz", "optimize", True)
    log_event("test-session-xyz", "export_tex", True)
    counts = get_telemetry_counts()
    assert counts["parse"] >= 1
    assert counts["optimize"] >= 1
    assert counts["export_tex"] >= 1
    print("✓ test_telemetry passed")

if __name__ == "__main__":
    test_tex_escape()
    test_extract_tokens_and_coverage()
    test_render_latex_sanity()
    test_render_plaintext()
    test_telemetry()
    print("\n🎉 ALL TESTS PASSED!")
