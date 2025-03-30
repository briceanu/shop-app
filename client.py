import requests





url  = 'http://localhost:8000/user/secret'

# ✅ Use headers instead of auth
headers = {
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJnaWdpIiwiZXhwIjoxNzQzMzcyNTpyfQ.KeCl2zniNWoYpS8sKBq0Uk08_e8Nf1LEwbRsbSw1s3Q"
}


response = requests.get(url=url,headers=headers)


print(response.status_code)
print(response.text)