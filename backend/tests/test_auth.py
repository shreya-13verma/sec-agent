def test_login_valid_credentials(client):
    """TC-001: Valid user authentication returns 200 and access token."""
    response = client.post("/api/v1/auth/login", json={"username": "admin", "password": "admin123"})
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["username"] == "admin"
    assert data["user"]["role"] == "Admin"

def test_login_invalid_password(client):
    """TC-002: Invalid password returns 401 Unauthorized."""
    response = client.post("/api/v1/auth/login", json={"username": "admin", "password": "wrongpassword"})
    assert response.status_code == 401
    assert "Invalid username or password" in response.json()["detail"]

def test_login_nonexistent_user(client):
    """TC-002: Non-existent user returns 401 Unauthorized."""
    response = client.post("/api/v1/auth/login", json={"username": "ghost_user", "password": "any"})
    assert response.status_code == 401

def test_protected_route_without_token(client):
    """TC-003: Accessing protected endpoints without a token returns 401."""
    response = client.get("/api/v1/hosts")
    assert response.status_code == 401

def test_current_user_profile(client, admin_headers):
    """Get authenticated user profile."""
    response = client.get("/api/v1/auth/me", headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "admin"
    assert data["role"] == "Admin"

def test_register_new_user_by_admin(client, admin_headers):
    """Admin registers a new operator account."""
    new_user_payload = {
        "username": "new_ops_eng",
        "email": "ops@compliance.corp",
        "password": "strongPassword123",
        "full_name": "Operations Lead",
        "role": "Operator"
    }
    response = client.post("/api/v1/auth/register", json=new_user_payload, headers=admin_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "new_ops_eng"
    assert data["role"] == "Operator"

def test_register_new_user_forbidden_for_operator(client, operator_headers):
    """Operator cannot register new users (RBAC)."""
    new_user_payload = {
        "username": "unauthorized_user",
        "email": "unauth@compliance.corp",
        "password": "pwd",
        "full_name": "Unauthorized User",
        "role": "Operator"
    }
    response = client.post("/api/v1/auth/register", json=new_user_payload, headers=operator_headers)
    assert response.status_code == 403
