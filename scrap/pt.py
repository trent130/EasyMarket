import requests

def fetch_data():
    url = "https://live.betika.com/v1/uo/sports"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
        "Accept": "application/json"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()  # Return JSON response
    else:
        raise Exception(f"Failed with status code: {response.status_code}")


print(fetch_data())
# https://cdn.betika.com/seo-content/ke/meta-data-ke.json for fetching the header files
# https://ip.betika.com/ for ip address
# https://live.betika.com/v1/uo/sports for fetching sports information