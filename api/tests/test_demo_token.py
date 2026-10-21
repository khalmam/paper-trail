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
