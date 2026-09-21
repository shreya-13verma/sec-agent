def test_health_check(client):
    """TC-015: Health check verification."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["database"] == "connected"

def test_list_hosts(client, admin_headers):
    """List all synchronized hosts."""
    response = client.get("/api/v1/hosts", headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "items" in data
    assert data["total"] >= 1
    # Verify fields of first host
    host = data["items"][0]
    assert "hostname" in host
    assert "ip_address" in host
    assert "os_family" in host

def test_list_hosts_search_and_filter(client, admin_headers):
    """Search and filter host list."""
    # Filter by OS SLES
    response = client.get("/api/v1/hosts?os_family=SLES", headers=admin_headers)
    assert response.status_code == 200
    items = response.json()["items"]
    assert all(item["os_family"] == "SLES" for item in items)

    # Search by hostname pattern
    response_search = client.get("/api/v1/hosts?search=hana", headers=admin_headers)
    assert response_search.status_code == 200
    search_items = response_search.json()["items"]
    assert len(search_items) >= 1
    assert "hana" in search_items[0]["hostname"].lower()

def test_get_host_detail(client, admin_headers):
    """Get complete host detail with packages, errata, channels."""
    # First get host id
    list_res = client.get("/api/v1/hosts", headers=admin_headers)
    host_id = list_res.json()["items"][0]["id"]

    detail_res = client.get(f"/api/v1/hosts/{host_id}", headers=admin_headers)
    assert detail_res.status_code == 200
    data = detail_res.json()
    assert data["id"] == host_id
    assert "packages" in data
    assert "channels" in data
    assert "missing_errata" in data
    assert len(data["packages"]) > 0

def test_sync_hosts_from_mlm(client, sec_officer_headers):
    """TC-005: Trigger MLM inventory sync."""
    response = client.post("/api/v1/hosts/sync", json={"force_full_sync": True}, headers=sec_officer_headers)
    assert response.status_code == 202
    data = response.json()
    assert data["status"] == "SUCCESS"
    assert data["synced_hosts_count"] >= 1

def test_host_cascade_delete(client, admin_headers, db_session):
    """TC-013: Deleting a host cascade deletes packages and channels."""
    from backend.app.models.host import Host, HostPackage, HostChannel
    
    # Create temporary host with packages
    test_host = Host(
        mlm_system_id=999999,
        hostname="cascade-test.corp.internal",
        ip_address="10.0.99.99",
        os_family="SLES",
        os_version="15 SP5",
        kernel_release="5.14.0",
        architecture="x86_64",
        compliance_status="UNKNOWN",
        compliance_score=0.0
    )
    db_session.add(test_host)
    db_session.commit()
    db_session.refresh(test_host)

    pkg = HostPackage(
        host_id=test_host.id,
        package_name="test-pkg",
        package_version="1.0",
        package_release="1",
        package_arch="x86_64"
    )
    ch = HostChannel(
        host_id=test_host.id,
        channel_label="test-channel",
        channel_name="Test Channel"
    )
    db_session.add_all([pkg, ch])
    db_session.commit()

    # Delete via API
    del_res = client.delete(f"/api/v1/hosts/{test_host.id}", headers=admin_headers)
    assert del_res.status_code == 204

    # Verify cascade delete
    assert db_session.query(Host).filter(Host.id == test_host.id).first() is None
    assert db_session.query(HostPackage).filter(HostPackage.host_id == test_host.id).first() is None
    assert db_session.query(HostChannel).filter(HostChannel.host_id == test_host.id).first() is None
