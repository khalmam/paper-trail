def test_no_demo_token_unless_set_on_purpose(client, settings):
    settings.DEMO_TOKEN = None
    assert client.get("/api/demo-token").status_code == 404


def test_demo_token_is_handed_out_when_configured(client, settings):
    settings.DEMO_TOKEN = "demo-abc"
    assert client.get("/api/demo-token").json() == {"token": "demo-abc"}


def test_simulator_asks_for_the_demo_token(client):
    assert "/api/demo-token" in client.get("/simulator").content.decode()


def test_simulator_script_keeps_newlines_escaped(client):
    page = client.get("/simulator").content.decode()
    assert "l.subject+'\\n\\n'+l.body" in page


def test_simulator_script_parses(client, tmp_path):
    import re, shutil, subprocess, pytest
    if not shutil.which("node"):
        pytest.skip("node not installed")
    page = client.get("/simulator").content.decode()
    scripts = re.findall(r"<script>(.*?)</script>", page, re.S)
    assert scripts
    f = tmp_path / "s.js"
    f.write_text("\n".join(scripts))
    r = subprocess.run(["node", "--check", str(f)], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr


def test_simulator_skin_respects_reduced_motion_and_never_animates_all(client):
    page = client.get("/simulator").content.decode()
    assert "prefers-reduced-motion" in page and "pt-line" in page
    assert "transition:all" not in page.replace(" ", "")


def test_simulator_sends_recent_turns_with_each_message(client):
    page = client.get("/simulator").content.decode()
    assert "history:hist.slice(-8)" in page and "let hist=[];" in page
