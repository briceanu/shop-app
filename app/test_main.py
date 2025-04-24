from fastapi.testclient import TestClient
from main import app
 
client = TestClient(app)



headers = {
  "Authorization": "bearer",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZW9kb3IiLCJleHAiOjE3NDU1NjIxNjYsImp0aSI6IjhkYzg0MTY2LWFiYzctNDk1OS1iMDE3LTRhODhkODZjZjhjOSJ9.wtQyDv8FivvSwW9IDk3GQx5KvO_KQxN62NjzUdPZU4c",
 }

url = "/user/new_access_token"

def test_get_new_access_token():
    response = client.post(url=url,headers=headers)
    assert response.status_code == 401


def test_logout_user():
    response = client.post(url='/user/logout',headers=headers)
    assert response.status_code == 400
    assert response.json()['detail']=='Token already blacklisted'
