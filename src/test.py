import requests

url = "http://127.0.0.1:5000/requirements"

payload = {
    "requirement_name": "REQ-TEST",
    "requirement_description": "TEST POST",
}

r = requests.post(url, json=payload)

print("code : ", r.status_code)
print("Reponse : ", r.json())