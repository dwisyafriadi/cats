import requests
from tabulate import tabulate
from colorama import Fore, Style
import urllib.parse
import time

# Function to read all authorization tokens from query.txt
def get_authorization_tokens():
    with open('query.txt', 'r') as file:
        return [line.strip() for line in file if line.strip()]

# Function to read the proxy from proxy.txt
def get_proxy():
    try:
        with open('proxy.txt', 'r') as file:
            proxy = file.readline().strip()
            return proxy if proxy else None
    except FileNotFoundError:
        return None

# Function to set headers with the provided token
def get_headers(token):
    return {
        "accept": "*/*",
        "accept-language": "en-US,en;q=0.9",
        "authorization": f"tma {token}",
        "content-type": "application/json",
        "priority": "u=1, i",
        "sec-ch-ua": "\"Not)A;Brand\";v=\"99\", \"Microsoft Edge\";v=\"127\", \"Chromium\";v=\"127\", \"Microsoft Edge WebView2\";v=\"127\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Windows\"",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "cross-site",
        "Referer": "https://cats-frontend.tgapps.store/",
        "Referrer-Policy": "strict-origin-when-cross-origin"
    }

# Helper functions for managing requests
def make_request_with_delay(url, headers, proxies=None, delay=2):
    response = requests.get(url, headers=headers, proxies=proxies, timeout=10)
    time.sleep(delay)  # Adjust the delay as needed
    return response

def make_request_with_retries(url, headers, proxies=None, max_retries=3):
    for attempt in range(max_retries):
        try:
            response = requests.get(url, headers=headers, proxies=proxies, timeout=10)
            response.raise_for_status()  # Raise an error for bad status codes
            return response
        except requests.exceptions.RequestException as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            time.sleep(2 ** attempt)  # Exponential backoff
    return None

def process_in_batches(tasks, batch_size=5, delay=5):
    for i in range(0, len(tasks), batch_size):
        batch = tasks[i:i + batch_size]
        for task in batch:
            # Call the function to process each task
            make_request_with_delay(task['url'], task['headers'])
        time.sleep(delay)  # Delay after each batch

def print_welcome_message():
    print(Fore.WHITE + f"\nCats Auto Clear Task")

def user_info(proxy=None):
    tokens = get_authorization_tokens()
    all_user_data = []
    total_rewards_sum = 0
    
    for token in tokens:
        headers = get_headers(token)
        url = "https://cats-backend-cxblew-prod.up.railway.app/user"
        
        proxies = {"http": proxy, "https": proxy} if proxy else None
        response = make_request_with_retries(url, headers, proxies)
        
        if response and response.status_code == 200:
            data = response.json()
            first_name = data.get('firstName', 'N/A')
            last_name = data.get('lastName', 'N/A')
            telegram_age = data.get('telegramAge', 0)
            total_rewards = data.get('totalRewards', 0)
            
            all_user_data.append([first_name, last_name, telegram_age, total_rewards])
            total_rewards_sum += total_rewards
        else:
            print(Fore.RED + f"Failed to fetch user data for token {token}.")
            continue
    
    table_data = [
        ["First Name", "Last Name", "Telegram Age", "Total Rewards"]
    ]
    table_data.extend(all_user_data)
    
    print(tabulate(table_data, headers='firstrow', tablefmt='grid'))
    print(Fore.GREEN + f"\nTotal Rewards: " + Fore.WHITE + f"{total_rewards_sum}" + Style.RESET_ALL)

def fetch_tasks(proxy=None):
    tokens = get_authorization_tokens()
    all_tasks_data = []
    task_ids = []

    for token in tokens:
        headers = get_headers(token)
        url = "https://cats-backend-cxblew-prod.up.railway.app/tasks/user?group=cats"
        
        proxies = {"http": proxy, "https": proxy} if proxy else None
        response = make_request_with_retries(url, headers, proxies)
        
        if response and response.status_code == 200:
            data = response.json()
            tasks = data.get('tasks', [])
            
            for task in tasks:
                task_info = [
                    task.get('id'),
                    task.get('title'),
                    task.get('type'),
                    task.get('rewardPoints'),
                    task.get('completed'),
                    task.get('isPending')
                ]
                all_tasks_data.append(task_info)
                task_ids.append(task.get('id'))
        else:
            print(Fore.RED + f"Failed to fetch tasks for token {token}.")
            continue

    if all_tasks_data:
        table_data = [
            ["ID", "Title", "Type", "Reward Points", "Completed", "Is Pending"]
        ]
        table_data.extend(all_tasks_data)
        
        print(Fore.WHITE + tabulate(table_data, headers='firstrow', tablefmt='grid'))
    else:
        print(Fore.YELLOW + "No tasks found.")
    
    return task_ids

def clear_tasks(task_ids, proxy=None):
    tokens = get_authorization_tokens()
    
    for token in tokens:
        headers = get_headers(token)
        
        for task_id in task_ids:
            # Log the task ID being attempted for completion
            print(Fore.WHITE + f"Attempting to complete task ID: {task_id}")

            url = f"https://cats-backend-cxblew-prod.up.railway.app/tasks/{task_id}/complete"  # Make sure this is the correct endpoint
            proxies = {"http": proxy, "https": proxy} if proxy else None
            response = make_request_with_retries(url, headers, proxies)
            
            if response and response.status_code == 200:
                data = response.json()
                if data.get("completed"):
                    print(Fore.GREEN + f"Task {task_id} marked as completed.")
                else:
                    print(Fore.RED + f"Task {task_id} could not be completed.")
            else:
                print(Fore.RED + f"Failed to mark task {task_id} as completed.")



def call_speculation_api(proxy=None):
    url = "https://cats-frontend.tgapps.store/cdn-cgi/speculation"
    proxies = {"http": proxy, "https": proxy} if proxy else None
    response = make_request_with_retries(url, {}, proxies)
    if response:
        print(Fore.GREEN + "Speculation API called successfully.")
    else:
        print(Fore.RED + "Failed to call Speculation API.")

def call_rum_api(proxy=None):
    url = "https://cloudflareinsights.com/cdn-cgi/rum"
    payload = {
        "resources": [],
        "referrer": "",
        "eventType": 1,
        "firstPaint": 272.20000000298023,
        "firstContentfulPaint": 0,
        "startTime": 1726909733843.4,
        "versions": {"js": "2024.6.1", "timings": 1},
        "pageloadId": "a673ddfb-6ce1-4fce-bc2f-1ac53e56d147",
        "location": "https://cats-frontend.tgapps.store/",
        "nt": "reload",
        "timingsV2": {"nextHopProtocol": "h2", "transferSize": 938, "decodedBodySize": 1295},
        "dt": "",
        "siteToken": "69e69bd702184c29ac1679abadd26f70",
        "st": 2
    }
    
    proxies = {"http": proxy, "https": proxy} if proxy else None
    response = make_request_with_retries(url, payload, proxies)
    if response:
        print(Fore.GREEN + "RUM API called successfully.")
    else:
        print(Fore.RED + "Failed to call RUM API.")


def main():
    print_welcome_message()
    proxy = get_proxy()
    print(Fore.WHITE + f"\nUsing proxy: {proxy}" if proxy else "No proxy in use.")
    
    # Call the Speculation API
    call_speculation_api(proxy)
    
    print(Fore.WHITE + f"\nDisplaying user information...")
    user_info(proxy)
    print(Fore.WHITE + f"\nFetching tasks...")
    task_ids = fetch_tasks(proxy)
    if task_ids:
        print(Fore.WHITE + f"\nClearing tasks...")
        clear_tasks(task_ids, proxy)

    # Call the RUM API
    call_rum_api(proxy)

# Example usage
if __name__ == "__main__":
    main()