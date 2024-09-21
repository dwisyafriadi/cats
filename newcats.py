import requests
from tabulate import tabulate
from colorama import Fore, Style

# Function to read all authorization tokens from query.txt
def get_authorization_tokens():
    with open('query.txt', 'r') as file:
        return [line.strip() for line in file if line.strip()]

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

def user_info():
    tokens = get_authorization_tokens()
    all_user_data = []
    total_rewards_sum = 0
    
    for token in tokens:
        headers = get_headers(token)
        url = "https://cats-backend-cxblew-prod.up.railway.app/user"
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            # Extract required fields
            first_name = data.get('firstName', 'N/A')
            last_name = data.get('lastName', 'N/A')
            telegram_age = data.get('telegramAge', 0)
            total_rewards = data.get('totalRewards', 0)
            
            # Collect user data
            all_user_data.append([first_name, last_name, telegram_age, total_rewards])
            total_rewards_sum += total_rewards  # Accumulate total rewards
        else:
            print(Fore.RED + f"Failed to fetch user data for token {token}. Status code: {response.status_code}")
            continue  # Continue to the next token
    
    # Prepare data for tabulate
    table_data = [
        ["First Name", "Last Name", "Telegram Age", "Total Rewards"]
    ]
    table_data.extend(all_user_data)
    
    # Print table
    print(tabulate(table_data, headers='firstrow', tablefmt='grid'))
    
    # Print total rewards sum with color
    print(Fore.GREEN + f"\nTotal Rewards: " + Fore.WHITE + f"{total_rewards_sum}" + Style.RESET_ALL)

def fetch_tasks():
    tokens = get_authorization_tokens()
    all_tasks_data = []
    task_ids = []  # List to store task IDs

    for token in tokens:
        headers = get_headers(token)
        url = "https://cats-backend-cxblew-prod.up.railway.app/tasks/user?group=cats"
        response = requests.get(url, headers=headers)
        
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
                task_ids.append(task.get('id'))  # Collect task IDs
        else:
            print(Fore.RED + f"Failed to fetch tasks for token {token}. Status code: {response.status_code}")
            continue  # Continue to the next token

    # Prepare data for tabulate
    if all_tasks_data:
        table_data = [
            ["ID", "Title", "Type", "Reward Points", "Completed", "Is Pending"]
        ]
        table_data.extend(all_tasks_data)
        
        # Print tasks table
        print(Fore.WHITE + tabulate(table_data, headers='firstrow', tablefmt='grid'))
    else:
        print(Fore.YELLOW + "No tasks found.")
    
    return task_ids  # Return the list of task IDs

def clear_tasks(task_ids):
    tokens = get_authorization_tokens()
    
    for token in tokens:
        headers = get_headers(token)
        
        for task_id in task_ids:
            url = f"https://cats-backend-cxblew-prod.up.railway.app/tasks/{task_id}/check"
            response = requests.post(url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("completed"):
                    print(Fore.GREEN + f"Task {task_id} marked as completed.")
                else:
                    print(Fore.RED + f"Task {task_id} could not be completed.")
            else:
                print(Fore.RED + f"Failed to mark task {task_id} as completed. Status code: {response.status_code}")

def main():
    print_welcome_message()
    print(Fore.WHITE + f"\nDisplaying user information...")
    user_info()
    print(Fore.WHITE + f"\nFetching tasks...")
    task_ids = fetch_tasks()
    if task_ids:
        print(Fore.WHITE + f"\nClearing tasks...")
        clear_tasks(task_ids)

# Example usage
if __name__ == "__main__":
    main()
