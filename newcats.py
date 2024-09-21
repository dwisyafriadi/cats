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
        response = requests.get(url, headers=headers, proxies=proxies)
        
        if response.status_code == 200:
            data = response.json()
            first_name = data.get('firstName', 'N/A')
            last_name = data.get('lastName', 'N/A')
            telegram_age = data.get('telegramAge', 0)
            total_rewards = data.get('totalRewards', 0)
            
            all_user_data.append([first_name, last_name, telegram_age, total_rewards])
            total_rewards_sum += total_rewards
        else:
            print(Fore.RED + f"Failed to fetch user data for token {token}. Status code: {response.status_code}")
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
        start_time = time.time()
        response = requests.get(url, headers=headers, proxies=proxies)
        elapsed_time = time.time() - start_time
        
        print(Fore.WHITE + f"Request time for token: {elapsed_time:.2f} seconds")
        
        if response.status_code == 200:
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
            print(Fore.RED + f"Failed to fetch tasks for token {token}. Status code: {response.status_code}")
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
            url = f"https://cats-backend-cxblew-prod.up.railway.app/tasks/{task_id}/check"
            proxies = {"http": proxy, "https": proxy} if proxy else None
            response = requests.post(url, headers=headers, proxies=proxies)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("completed"):
                    print(Fore.GREEN + f"Task {task_id} marked as completed.")
                else:
                    print(Fore.RED + f"Task {task_id} could not be completed.")
            else:
                print(Fore.RED + f"Failed to mark task {task_id} as completed. Status code: {response.status_code}")

def update_query_id():
    # This function can be left empty since it automatically reads all data from query.txt
    pass

def main():
    print_welcome_message()
    proxy = get_proxy()
    print(Fore.WHITE + f"\nUsing proxy: {proxy}" if proxy else "No proxy in use.")
    
    print(Fore.WHITE + f"\nDisplaying user information...")
    user_info(proxy)
    print(Fore.WHITE + f"\nFetching tasks...")
    task_ids = fetch_tasks(proxy)
    if task_ids:
        print(Fore.WHITE + f"\nClearing tasks...")
        clear_tasks(task_ids, proxy)

# Example usage
if __name__ == "__main__":
    main()
