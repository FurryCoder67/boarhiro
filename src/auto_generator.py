import requests, time, os

def hunt():
    url = "https://api.github.com/search/repositories?q=language:python&sort=stars"
    try:
        items = requests.get(url).json()['items'][:3]
        if not os.path.exists('data'): os.makedirs('data')
        with open("data/input.txt", "a", encoding="utf-8") as f:
            for item in items:
                f.write(f"\n# New Logic: {item['full_name']}\n")
        print("🐗 Intel Secured.")
    except: print("Hunt failed.")

if __name__ == "__main__":
    while True:
        hunt()
        time.sleep(86400)