import json

import requests


URL = "https://jsonplaceholder.typicode.com/users"


def fetch_users(user_id=None):
    params = {"id": user_id} if user_id is not None else None
    try:
        response = requests.get(URL, params=params, timeout=5)
        response.raise_for_status()
    except requests.exceptions.RequestException as error:
        print(f"Error retrieving users: {error}")
        return None

    users = response.json()
    if not isinstance(users, list):
        print("Error: The API response is not a list of users.")
        return None
    return users


def search_user_by_id(user_id):
    users = fetch_users(user_id)
    if users is None:
        return
    if not users:
        print(f"Error: No user found with ID {user_id}.")
        return

    show_users(users)


def transform_user_data(users):
    return [
        {
            "name": user["name"],
            "address": {
                "suite": user["address"]["suite"],
                "street": user["address"]["street"],
                "city": user["address"]["city"],
                "zipcode": user["address"]["zipcode"],
            },
        }
        for user in users
    ]


def save_results_to_json(users):
    transformed_users = transform_user_data(users)
    users_json = json.dumps(transformed_users, indent=4)
    with open("users.json", "w", encoding="utf-8") as json_file:
        json_file.write(users_json)
    print("Results saved to users.json")


def show_users(users):
    print("Users names and addresses:")
    print("-----------------")
    for user in users:
        address = user["address"]
        print(
            f"Name: {user['name']}, Address: {address['suite']}, "
            f"{address['street']}, {address['city']}, {address['zipcode']},"
        )


def show_all_source_data():
    users = fetch_users()
    if users is not None:
        show_users(users)


def main():
    print("Select an operation:")
    print("1. Search for a user by ID")
    print("2. Transform and save all users to users.json")
    print("3. Show all users from the data source")
    choice = input("Enter 1, 2, or 3: ").strip()

    if choice == "1":
        user_id = input("Enter the user ID: ").strip()
        search_user_by_id(user_id)
    elif choice == "2":
        users = fetch_users()
        if users is not None:
            save_results_to_json(users)
    elif choice == "3":
        show_all_source_data()
    else:
        print("Invalid choice. Please select 1, 2, or 3.")


if __name__ == "__main__":
    main()
