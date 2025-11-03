from fastapi.testclient import TestClient


def test_create_template(client: TestClient) -> None:
    payload = {
        "name": "Aid Request",
        "description": "Request assistance",
        "fields": [
            {"name": "full_name", "label": "Full Name", "type": "text", "required": True},
            {"name": "amount", "label": "Requested Amount", "type": "number", "required": True},
        ],
    }

    response = client.post("/api/v1/templates", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == payload["name"]
    assert len(data["fields"]) == 2


def test_create_submission(client: TestClient) -> None:
    template_payload = {
        "name": "Scholarship",
        "description": "Scholarship aid form",
        "fields": [
            {"name": "email", "label": "Email", "type": "email", "required": True},
            {"name": "needs", "label": "Needs", "type": "textarea"},
        ],
    }
    template_response = client.post("/api/v1/templates", json=template_payload)
    template_id = template_response.json()["id"]

    submission_payload = {"data": {"email": "student@example.com", "needs": "Books"}}
    submission_response = client.post(f"/api/v1/templates/{template_id}/submissions", json=submission_payload)
    assert submission_response.status_code == 201
    submission_data = submission_response.json()
    assert submission_data["template_id"] == template_id
    assert submission_data["data"] == submission_payload["data"]


def test_submission_validation(client: TestClient) -> None:
    template_payload = {
        "name": "Emergency Fund",
        "fields": [
            {"name": "contact", "label": "Contact", "type": "text", "required": True},
        ],
    }
    template_response = client.post("/api/v1/templates", json=template_payload)
    template_id = template_response.json()["id"]

    submission_payload = {"data": {}}
    response = client.post(f"/api/v1/templates/{template_id}/submissions", json=submission_payload)
    assert response.status_code == 422
    assert "Missing required field" in response.json()["detail"][0]


def test_render_template(client: TestClient) -> None:
    template_payload = {
        "name": "Job Aid",
        "fields": [
            {"name": "skills", "label": "Skills", "type": "textarea"},
        ],
    }
    template_response = client.post("/api/v1/templates", json=template_payload)
    template_id = template_response.json()["id"]

    response = client.get(f"/api/v1/templates/{template_id}/render")
    assert response.status_code == 200
    render = response.json()
    assert render["name"] == template_payload["name"]
    assert render["fields"][0]["type"] == "textarea"
