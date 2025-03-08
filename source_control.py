import requests
import json
import time

# Object details
NEW_DESCRIPTION_TEMPLATE = "Updated description via API - Run {}"
# Function to get authentication token
def get_auth_token():
    auth_url = f"{IICS_BASE_URL}/public/core/v3/login"
    headers = {"Content-Type": "application/json"}
    payload = {
        "username": USERNAME,
        "password": PASSWORD,
    }
    response = requests.post(auth_url, headers=headers, json=payload)
    data = response.json()
    if response.status_code == 200:
        session_id = data['userInfo'].get('sessionId')
        return session_id
    else:
        print("Failed to authenticate:", response.text)
        exit()
#Fething Object details
def object_fetch_API(sessionId,task_name):
    Object_fetch_URL=f"{IICS_POD_URL}/api/v2/mttask/name/{task_name}"
    headers = {
        "Content-Type": "application/json",
        "icSessionId": sessionId
    }
    
    response = requests.get(Object_fetch_URL, headers=headers)
    if response.status_code == 200:
        print("Object fetched successfully!")
        return response.json()
    else:
        print("Fetching failed:", response.text)
        exit()
        
    
# Function to check out an object
def checkout_object(sessionId,task_name):
    checkout_url = f"{IICS_POD_URL}/public/core/v3/checkout"
    headers = {
        "Content-Type": "application/json",
        "INFA-SESSION-ID": sessionId
    }
    payload = {
  "objects": [
    {
      "path": [
        "Amit",
        task_name
      ],
      "type": "MTT"
    }
  ]
}
    response = requests.post(checkout_url, headers=headers, json=payload)
    if response.status_code == 200:
        print("Object checked out successfully!")
    else:
        print("Checkout failed:", response.text)
        exit()
        
# Function to modify the object's description
def update_object_description(sessionId,fetch_api_response):
    OBJECT_ID =fetch_api_response.get("frsGuid","")
    update_url = f"{IICS_POD_URL}/api/v2/mttask/frs/{OBJECT_ID}"
    headers = {
        "Content-Type": "application/json",
        "INFA-SESSION-ID": sessionId
    }
    
    response = requests.patch(update_url, headers=headers, json=fetch_api_response)
    if response.status_code == 200:
        print(f"Object description updated successfully! (Run {fetch_api_response.get("description")})")
    else:
        print(f"Update failed on run {fetch_api_response.get("description")}:", response.text)
        exit()
# Function to check in an object
def checkin_object(sessionId, run_count,task_name,object_id):
    checkin_url = f"{IICS_POD_URL}/public/core/v3/checkin"
    headers = {
        "Content-Type": "application/json",
        "INFA-SESSION-ID": sessionId
    }
    payload = {
  "objects": [
    {
      "id": object_id
    }
  ],
  "summary": "Revised Revised m_custArch"
}
    response = requests.post(checkin_url, headers=headers, json=payload)
    print(response)
    if response.status_code == 200:
        print(f"Object checked in successfully! (Run {run_count})")
    else:
        print("checkin failed")
if __name__ == "__main__":
    # Load configuration from JSON file
    with open("config.json", "r") as config_file:
        config = json.load(config_file)
    # Access config values
    USERNAME = config["username"]
    PASSWORD = config["password"]
    IICS_BASE_URL = config["iics_base_url"]
    IICS_POD_URL = config["iics_pod_url"]
    task_name=config["mappingtask_name"]
    Iteration=config["number_of_iteration"]
    
    session_token = get_auth_token()
    for i in range(1,Iteration):  # Run N times
        print(f"\n=== Iteration {i} ===")
        fetch_api_response=object_fetch_API(session_token,task_name)
        checkout_object(session_token,task_name)
        fetch_api_response["description"]=NEW_DESCRIPTION_TEMPLATE.format(i)
        update_object_description(session_token,fetch_api_response)
        checkin_object(session_token, i,task_name,fetch_api_response.get("frsGuid"))
        #time.sleep(2)  # Small delay to prevent API throttlig