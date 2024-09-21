import requests

def test_proxy(proxy):
    url = "https://cats-backend-cxblew-prod.up.railway.app/user"
    proxies = {"http": proxy, "https": proxy}
    try:
        response = requests.get(url, proxies=proxies, timeout=10)
        print(f"Response Code: {response.status_code}")
        print(f"Response Body: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    proxy = "https://3d83fa804e1b8f10bd08__cr.de:7d3d77516f04ae40@gw.dataimpulse.com:823"  # Replace with your proxy details
    test_proxy(proxy)
