import requests
from bs4 import BeautifulSoup
import getpass
import os
import csv

session = requests.Session()
protected_url = "https://live.musonisystem.com/phoenix/index.php/Loan/Loan/55739"
login_url = "https://live.musonisystem.com/phoenix/index.php/Site/Login"
headers = { 
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

def login_to_website(username, password):
    session.get(login_url, headers=headers)
    payload = {
        "LoginForm[username]": username, 
        "LoginForm[password]": password,
        "lang": "en",
        "yt0": "Login"
    }

    response = session.post(login_url, data=payload, headers=headers, allow_redirects=False)
    if response.status_code == 302:
        print(f"Login successful! Server is redirecting us to {response.headers.get('location')}.")
        # Manually follow the redirect now to establish the session fully
        session.get(response.headers['Location'], headers=headers)

        return True

    else:
        print(f"Login failed. Server returned status code {response.status_code}.")
        return False    

def fetch_protected_page():

    Protected_response = session.get(protected_url, headers=headers)
    soup = BeautifulSoup(Protected_response.content, 'html.parser')

    transactions_table = soup.find(id="transactionTable")

    if not transactions_table:
        print("Could not find the transactions table on the protected page.")
        return None

    transaction_list  = []
    tbody = transactions_table.find('tbody')

    if tbody:
        for row in tbody.find_all('tr'):
            cells = row.find_all('td')

            if len(cells) >= 8:
                tx_type = cells[2].get_text(strip=True)

                if tx_type.lower() == "repayment":
                    transaction = {
                        "date": cells[0].get_text(strip=True),
                        "submitted_on": cells[1].get_text(strip=True),
                        "Transaction_Type": tx_type,
                        "Transaction_Id": cells[3].get_text(strip=True),
                        "credit": cells[5].get_text(strip=True),
                        "balance": cells[6].get_text(strip=True),
                        "payment_details": cells[7].get_text(strip=True),
                    }
                    transaction_list.append(transaction)


        print(f"\n--- Found {len(transaction_list)} Repayment Records ---")
        for repayment in transaction_list:
            print(repayment)
            
        # 2. Save filtered results directly to a CSV file
        if transaction_list:

            folder_path = "../data"
            csv_columns = ["date", "submitted_on", "Transaction_Type", "Transaction_Id","credit", "balance", "payment_details"]
            csv_file =os.path.join(folder_path, "repayments.csv")
            
            try:
                with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
                    writer = csv.DictWriter(file, fieldnames=csv_columns)
                    writer.writeheader()
                    for data in transaction_list:
                        writer.writerow(data)
                print(f"\n Success: Filtered repayments saved to '{csv_file}'")
            except IOError:
                print("\n Error occurred while writing the CSV file.")
    else:
        print("Table body (tbody) is empty or missing.")



if __name__ == "__main__":
    # Prompt the user for credentials cleanly
    user_input = input("Enter your username: ")
    # getpass hides the password on screen while you type
    pass_input = getpass.getpass("Enter your password: ") 

    if login_to_website(user_input, pass_input):
        table = fetch_protected_page()
