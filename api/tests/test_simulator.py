def test_simulator_is_labeled_simulated_and_self_contained(client):
    response = client.get("/simulator")
    html = response.content.decode()
    assert response.status_code == 200 and "Simulated voice assistant" in html
    for forbidden in ("http://", "https://", "<link", "src=", "innerHTML"):
        assert forbidden not in html


def test_simulator_posts_to_the_chat_endpoint(client):
    assert "/api/chat" in client.get("/simulator").content.decode()


def test_simulator_offers_voice_input_and_spoken_replies(client):
    html = client.get("/simulator").content.decode()
    assert "SpeechRecognition" in html and "speechSynthesis" in html
