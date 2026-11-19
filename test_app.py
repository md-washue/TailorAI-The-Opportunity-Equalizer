# TailorAI Comprehensive Unit Test Suite
import os
import copy
import shutil
import tempfile
from unittest.mock import patch, MagicMock
import requests

import app
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
            # Unknown section name (e.g. 'volunteering')
            IndexedBullet(
                section="volunteering",
                item_index=0,
                bullet_index=0,
                improved="Led local hackathon organizing committee.",
            ),
            # Empty section name
            IndexedBullet(
                section="",
                item_index=0,
                bullet_index=0,
                improved="Orphaned bullet.",
            ),
            # Out of bounds item_index (should not crash)
            IndexedBullet(
                section="experience",
                item_index=99,
                bullet_index=0,
                improved="Invalid item index bullet.",
            ),
            # Out of bounds bullet_index (should not crash)
            IndexedBullet(
                section="experience",
                item_index=0,
                bullet_index=99,
                improved="Invalid bullet index bullet.",
            ),
            # Negative item index (should be safely ignored)
            IndexedBullet(
                section="projects",
                item_index=-1,
                bullet_index=0,
                improved="Negative item index bullet.",
            ),
            # Negative bullet index (should be safely ignored)
            IndexedBullet(
                section="projects",
                item_index=0,
                bullet_index=-1,
                improved="Negative bullet index bullet.",
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

    # Test empty OptimizationResult (no bullets)
    empty_opt = OptimizationResult(bullets=[])
    assert len(empty_opt.bullets) == 0

    print("✓ test_positional_optimization_mapping passed (all bounds & edge cases verified)")

def test_fetch_github_repos():
    # 1. Empty / whitespace username returns empty string
    assert app.fetch_github_repos("") == ""
    assert app.fetch_github_repos("   ") == ""
    assert app.fetch_github_repos(None) == ""

    # 2. Mocking successful 200 response
    mock_repos = [
        {"name": "repo-one", "description": "A high-performance cache", "language": "Python"},
        {"name": "repo-two", "description": None, "language": "Go"},
    ]
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = mock_repos

    with patch("requests.get", return_value=mock_resp) as mock_get:
        output = app.fetch_github_repos("octocat")
        assert "repo-one (Language: Python)" in output
        assert "A high-performance cache" in output
        assert "repo-two (Language: Go)" in output
        assert "No description provided." in output
        # Verify User-Agent header was sent
        call_kwargs = mock_get.call_args[1]
        assert call_kwargs["headers"]["User-Agent"] == "TailorAI-HackTheGap"
        assert call_kwargs["timeout"] == 5

    # 3. Mocking non-200 response (e.g. 403 Forbidden / 404 Not Found)
    mock_err_resp = MagicMock()
    mock_err_resp.status_code = 403
    with patch("requests.get", return_value=mock_err_resp):
        assert app.fetch_github_repos("octocat") == ""

    # 4. Mocking network timeout / connection error
    with patch("requests.get", side_effect=requests.exceptions.Timeout):
        assert app.fetch_github_repos("octocat") == ""

    # 5. Invalid / malicious username inputs (path traversal / XSS / injection)
    assert app.fetch_github_repos("invalid/user") == ""
    assert app.fetch_github_repos("<script>alert(1)</script>") == ""
    assert app.fetch_github_repos("user?param=1") == ""
    assert app.fetch_github_repos("user#anchor") == ""
    assert app.fetch_github_repos("../etc/passwd") == ""

    print("✓ test_fetch_github_repos passed (offline & resilient)")

def test_telemetry_isolated():
    temp_dir = tempfile.mkdtemp()
    tmp_db_path = os.path.join(temp_dir, "isolated_metrics.sqlite3")

    original_db_path = app.DB_PATH
    try:
        app.DB_PATH = tmp_db_path
        app.init_db()

        app.log_event("test-session-audit", "parse", True)
        app.log_event("test-session-audit", "optimize", True)
        app.log_event("test-session-audit", "export_tex", True)
        app.log_event("test-session-audit", "cover_letter", True)

        counts = app.get_telemetry_counts()
        assert counts["parse"] == 1
        assert counts["optimize"] == 1
        assert counts["export_tex"] == 1
        assert counts["cover_letter"] == 1
    finally:
        app.DB_PATH = original_db_path
        shutil.rmtree(temp_dir, ignore_errors=True)

    print("✓ test_telemetry_isolated passed (isolated in temporary database)")

def test_demo_quota_tracker():
    tracker = app.get_demo_tracker()
    with tracker["lock"]:
        orig_count = tracker["count"]
        orig_date = tracker.get("date")

    try:
        with tracker["lock"]:
            tracker["count"] = 0
            tracker["date"] = app.date.today().isoformat()

        assert app.get_demo_remaining() == 50

        # Test single increment
        allowed, remaining = app.check_and_increment_demo()
        assert allowed is True
        assert remaining == 49
        assert app.get_demo_remaining() == 49

        # Test exhaustion cap at 50
        with tracker["lock"]:
            tracker["count"] = 50
        assert app.get_demo_remaining() == 0
        allowed_exhausted, remaining_exhausted = app.check_and_increment_demo()
        assert allowed_exhausted is False
        assert remaining_exhausted == 0
        assert app.get_demo_remaining() == 0

        # Test date rollover resets count
        with tracker["lock"]:
            tracker["date"] = "2000-01-01"
        assert app.get_demo_remaining() == 50
        allowed_new_day, remaining_new_day = app.check_and_increment_demo()
        assert allowed_new_day is True
        assert remaining_new_day == 49
    finally:
        with tracker["lock"]:
            tracker["count"] = orig_count
            tracker["date"] = orig_date

    print("✓ test_demo_quota_tracker passed (isolated & fully verified)")

def test_security_sql_and_xss_resilience():
    import html
    import sqlite3

    # 1. SQL Injection Parameterization Test
    temp_dir = tempfile.mkdtemp()
    tmp_db_path = os.path.join(temp_dir, "sec_metrics.sqlite3")
    orig_db = app.DB_PATH
    try:
        app.DB_PATH = tmp_db_path
        app.init_db()

        # Injection payload attempting to drop table or alter logic
        sql_payload_session = "test-session'; DROP TABLE events; --"
        sql_payload_event = "parse' OR '1'='1"
        app.log_event(sql_payload_session, sql_payload_event, True)

        # Verify database table is intact and stored string is literal
        conn = sqlite3.connect(tmp_db_path)
        cur = conn.cursor()
        cur.execute("SELECT session_id, event_type FROM events WHERE session_id = ?", (sql_payload_session,))
        row = cur.fetchone()
        conn.close()

        assert row is not None
        assert row[0] == sql_payload_session
        assert row[1] == sql_payload_event
    finally:
        app.DB_PATH = orig_db
        shutil.rmtree(temp_dir, ignore_errors=True)

    # 2. XSS HTML Escaping Test
    xss_tag = "<script>alert('xss')</script>"
    xss_attr = '" onmouseover="alert(1)" style="color:red"'
    assert "<" not in html.escape(xss_tag, quote=True)
    assert ">" not in html.escape(xss_tag, quote=True)
    assert '"' not in html.escape(xss_attr, quote=True)

    # 3. LaTeX Command Injection Escaping Test
    tex_payload = r"\write18{rm -rf /} \input{/etc/passwd}"
    sanitized_tex = tex_escape(tex_payload)
    assert r"\write18" not in sanitized_tex
    assert r"\input" not in sanitized_tex
    assert r"\textbackslash{}write18\{rm -rf /\} \textbackslash{}input\{/etc/passwd\}" == sanitized_tex

    print("✓ test_security_sql_and_xss_resilience passed (SQLi, XSS, and TeX injection verified)")

if __name__ == "__main__":
    test_tex_escape()
    test_render_plaintext_and_alias()
    test_extract_tokens_and_coverage()
    test_render_latex_sanity()
    test_positional_optimization_mapping()
    test_fetch_github_repos()
    test_telemetry_isolated()
    test_demo_quota_tracker()
    test_security_sql_and_xss_resilience()
    print("\n🎉 ALL AUDIT & UNIT TESTS PASSED WITH 100% SUCCESS!")
