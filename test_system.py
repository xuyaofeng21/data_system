import requests

BASE_URL = "http://127.0.0.1:8000"

def test_flow():
    # 1. Register Admin
    print("Registering Admin...")
    try:
        res = requests.post(f"{BASE_URL}/register", json={
            "username": "admin",
            "password": "password123",
            "role": "admin"
        })
        if res.status_code == 200:
            print("Admin Registered.")
        else:
            print(f"Admin Register info: {res.json()}")
    except Exception as e:
        print(f"Error: {e}")

    # 2. Login
    print("Logging in...")
    res = requests.post(f"{BASE_URL}/token", data={
        "username": "admin",
        "password": "password123"
    })
    token = res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("Logged in.")

    # 3. Create Template
    print("Creating Template...")
    template_data = {
        "name": "Purchase Request",
        "graph_json": {
            "nodes": [
                {"id": "Start"},
                {"id": "ManagerApproval"},
                {"id": "FinanceApproval"},
                {"id": "End"}
            ]
        }
    }
    res = requests.post(f"{BASE_URL}/templates", json=template_data, headers=headers)
    template_id = res.json()["id"]
    print(f"Template Created ID: {template_id}")

    # 4. Start Instance
    print("Starting Instance...")
    res = requests.post(f"{BASE_URL}/instances", json={"template_id": template_id}, headers=headers)
    instance = res.json()
    instance_id = instance["id"]
    print(f"Instance Started ID: {instance_id}")

    # 5. Check Prediction
    print("Checking Execution...")
    res = requests.get(f"{BASE_URL}/instances", headers=headers)
    instances = res.json()
    for inst in instances:
        if inst["id"] == instance_id:
            # We need to fetch executions to see prediction. 
            # The schema might not nest executions deep enough in list view, 
            # but let's check what we got.
            pass
            
    # Complete Node
    print("Completing Node...")
    res = requests.post(f"{BASE_URL}/instances/{instance_id}/complete_node", headers=headers)
    print(f"Node Completed: {res.json()}")

    # Check Dashboard Stats
    print("Checking Stats...")
    res = requests.get(f"{BASE_URL}/dashboard/stats", headers=headers)
    print(f"Stats: {res.json()}")

if __name__ == "__main__":
    test_flow()
