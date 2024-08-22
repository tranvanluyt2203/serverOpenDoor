import requests


accessToken = ""

def CreateUser():
    data = {
        "username": "user01",
        "password": "1234abcd"
    }
    try:
        response = requests.post(BASE_API + API_CREATE, json=data)
        print("Response: ", response.json())
        print("Status code",response.status_code)
    except requests.RequestException as e:
        print("Request failed:", e)
        
def LoginUser():
    data = {
        "username": "user01",
        "password": "1234abcd"
    }
    try:
        response = requests.post(BASE_API + API_LOGIN,json=data)
        print("Response: ",response.json())
        print("Status code",response.status_code)
        global accessToken
        accessToken = response.json().get("body").get("data_user").get("access_token")
    except requests.RequestException as e:
        print("Request failed:",e)

if __name__ == "__main__":
    select = int(input("Nhập lựa chọn: "))
    if (select==1):
        CreateUser()
    elif (select==2):
        LoginUser()
        print(accessToken)
    
    
