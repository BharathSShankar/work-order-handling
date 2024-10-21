import requests
import json

BASE_URL = "http://127.0.0.1:5000"  # Adjust if your Quart server is running on a different URL/port

def test_work_order_system():
    # 1. Create a work order
    create_work_order_url = f"{BASE_URL}/workorders/"
    work_order_data = {
        "viewers": ["user1"],
        "changers": ["user2"],
        "details": json.dumps({"description": "Fix the AC"})  # Ensure details are serialized correctly
    }
    
    create_response = requests.post(create_work_order_url, json=work_order_data)
    
    if create_response.status_code == 200:
        work_order_id = create_response.json()["id"]
        print(f"Work order created successfully with ID: {work_order_id}")
    else:
        print(f"Failed to create work order. Status code: {create_response.status_code}")
        return

    # 2. Shift work order state
    shift_work_order_url = f"{BASE_URL}/workorders/{work_order_id}/state"
    shift_data = {
        "action": "approve",
        "performed_by": "user2"
    }

    shift_response = requests.post(shift_work_order_url, json=shift_data)
    
    if shift_response.status_code == 200:
        print("Work order state shifted successfully.")
        print(f"Time taken for state transition: {shift_response.json()['time_taken']} seconds")
    else:
        print(f"Failed to shift work order state. Status code: {shift_response.status_code}")
        return

    # 3. Get visible work orders for user1
    get_visible_work_orders_url = f"{BASE_URL}/workorders/visible/user1"
    visible_response = requests.get(get_visible_work_orders_url)

    if visible_response.status_code == 200:
        visible_work_orders = visible_response.json()
        print(f"Visible work orders for user1: {visible_work_orders}")
    else:
        print(f"Failed to fetch visible work orders. Status code: {visible_response.status_code}")
        return

    # 4. Get changeable work orders for user2
    get_changeable_work_orders_url = f"{BASE_URL}/workorders/changeable/user2"
    changeable_response = requests.get(get_changeable_work_orders_url)

    if changeable_response.status_code == 200:
        changeable_work_orders = changeable_response.json()
        print(f"Changeable work orders for user2: {changeable_work_orders}")
    else:
        print(f"Failed to fetch changeable work orders. Status code: {changeable_response.status_code}")
        return

    # 5. Test average time stats
    average_time_stats_url = f"{BASE_URL}/stats/average_time"
    average_time_stats_response = requests.get(average_time_stats_url)

    if average_time_stats_response.status_code == 200:
        average_time_stats = average_time_stats_response.json()
        print("Average time stats:", average_time_stats)
    else:
        print(f"Failed to fetch average time stats. Status code: {average_time_stats_response.status_code}")

    # 6. Test user-specific stats
    user_stats_url = f"{BASE_URL}/stats/user_stats/user2"
    user_stats_response = requests.get(user_stats_url)

    if user_stats_response.status_code == 200:
        user_stats = user_stats_response.json()
        print("User-specific stats for user2:", user_stats)
    else:
        print(f"Failed to fetch user-specific stats. Status code: {user_stats_response.status_code}")

    # 7. Test attribute-based stats
    attribute_stats_url = f"{BASE_URL}/stats/attribute_stats?attribute_key=description&attribute_value=Fix the AC"
    attribute_stats_response = requests.get(attribute_stats_url)

    if attribute_stats_response.status_code == 200:
        attribute_stats = attribute_stats_response.json()
        print("Attribute-based stats:", attribute_stats)
    else:
        print(f"Failed to fetch attribute-based stats. Status code: {attribute_stats_response.status_code}")

if __name__ == "__main__":
    test_work_order_system()
