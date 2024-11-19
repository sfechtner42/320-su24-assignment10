"""
Provides a basic frontend for the social network project
"""

import sys
import main
from context_manager import Connection, DB_PATH


# pylint: disable = C0301, W0718


def load_users():
    """
    Loads user accounts from a file
    """
    filename = input("Enter filename of user file: ")
    if not main.load_users(DB_PATH,filename):
        print("An error occurred while loading users.")
    else:
        print("Accounts loaded successfully.")


def load_status_updates():
    """
    Loads status updates from a file
    """
    filename = input("Enter filename for status file: ")
    if not main.load_status_updates(DB_PATH, filename):
        print("An error occurred while loading status updates.")
    else:
        print("Status updates loaded successfully.")


def add_user():
    '''
    Adds a new user
    '''
    user_id = input("User ID: ")
    if not main.validate_length(user_id, 30):
        return  # Exit the function if validation fails

    user_name = input("User name: ")
    if not main.validate_length(user_name, 30):
        return  # Exit the function if validation fails

    user_last_name = input("User last name: ")
    if not main.validate_length(user_last_name, 100):
        return  # Exit the function if validation fails

    email = input("User email: ")  # No length limit specified for email

    user_data = {
        "user_id": user_id,
        "user_email": email,
        "user_name": user_name,
        "user_last_name": user_last_name
    }

    if not main.add_user(DB_PATH, user_id, user_name, user_last_name, email):
        print(f"Failed to add user: {user_data}")
    else:
        print("User added successfully.")


def update_user():
    """
    Updates information for an existing user.
    """
    user_id = input('User ID: ')
    user_name = input('User name: ')
    user_last_name = input('User last name: ')
    user_email = input('User email: ')

    # Call the function with correct argument order
    if main.update_user(DB_PATH, user_id, user_name, user_last_name, user_email):
        print("User was successfully updated")
    else:
        print("An error occurred while trying to update user; check user ID")

def search_user():
    """
    Searches for a user in the database.
    """
    user_id = input('Enter user ID to search: ')
    search_function = main.search_user(DB_PATH)
    result = search_function(user_id)
    if result:
        print(f"User ID: {result['user_id']}")
        print(f"Email: {result['user_email']}")
        print(f"Name: {result['user_name']}")
        print(f"Last name: {result['user_last_name']}")
    else:
        print("User not found")


def delete_user():
    """
    Deletes a user from the database.
    """
    user_id = input("Enter user ID to delete: ")
    if main.delete_user(user_id):
        print("User was successfully deleted.")
    else:
        print("An error occurred while trying to delete user; check user ID")


def add_status():
    """
    Adds a new status to the database.
    """
    status_id = input("Status ID: ")
    user_id = input("User ID: ")
    status_text = input("Status text: ")

    if main.add_status(DB_PATH, status_id, user_id, status_text) is None:
        print("New status was successfully added.")
    else:
        print("An error occurred while trying to add the new status.")


def update_status():
    '''
    Updates information for an existing status.
    '''
    status_id = input("Enter status ID to update: ")

    # Prompt for user_id but allow blank input (to keep the old user_id)
    user_id = input("User ID (leave blank/press enter to keep the current user_id): ")

    # Prompt for status text but allow blank input (to keep the old status_text)
    status_text = input("Enter new status text (leave blank/press enter to keep the current status text): ")

    # Pass user_id and status_text to main.update_status, but leave them as None if blank
    if main.update_status(DB_PATH, status_id, user_id if user_id else None, status_text if status_text else None):
        print("Status was successfully updated.")
    else:
        print("An error occurred while trying to update status; check user and status IDs.")


def search_status():
    """
    Searches for a status in the database.
    """
    status_id = input('Enter status ID to search: ')
    result = main.search_status(DB_PATH, status_id)  # Call search_status correctly

    if result:
        print(f"Status ID: {result['status_id']}")
        print(f"User ID: {result['user_id']}")
        print(f"Status text: {result['status_text']}")
    else:
        print("Status not found")

def delete_status():
    """
    Deletes a status from the database.
    """
    status_id = input("Enter status ID to delete: ")
    if main.delete_status(status_id):
        print("Status was successfully deleted.")
    else:
        print("An error occurred while trying to delete status; check status ID")


def add_picture():
    """
    Adds a picture for a user.
    """
    user_id = input("User ID: ")
    tags = input("Enter hashtags (space-separated): ")
    if not main.validate_length(tags, 100):
        return  # Exit the function if validation fails

    if main.add_picture(user_id, tags):
        print("Picture added successfully.")
    else:
        print("An error occurred while adding the picture.")


def list_user_images():
    """
    Lists all images for a user.
    """
    user_id = input("User ID: ")

    try:
        images = main.list_user_images(DB_PATH, user_id)

        if images:
            print(f"Images for user {user_id}:")
            for img in images:
                print(f"Path: {img}")
        else:
            print("No images found.")

    except Exception as e:
        print(f"An error occurred: {e}")

def reconcile_images():
    """
    Reconciles images stored in the database with those on disk.
    """
    user_id = input("User ID: ")
    not_in_db, not_on_disk = main.reconcile_images(DB_PATH, user_id)

    if not_in_db or not_on_disk:
        print(f"Images not in database: {not_in_db}")
        print(f"Images not on disk: {not_on_disk}")
    else:
        print("No discrepancies found.")

def quit_program():
    '''
    Quits the program.
    '''
    sys.exit()


if __name__ == "__main__":
    with Connection(DB_PATH) as connection:
        user_table = connection.user_table
        status_table = connection.status_table
        picture_table = connection.picture_table
        menu_options = {
            "A": load_users,
            "B": load_status_updates,
            "C": add_user,
            "D": update_user,
            "E": search_user,
            "F": delete_user,
            "G": add_status,
            "H": update_status,
            "I": search_status,
            "J": delete_status,
            "K": add_picture,
            "L": list_user_images,
            "M": reconcile_images,
            "Q": quit_program,
        }

    while True:
        user_selection = input(
            """
                            A: Load user database
                            B: Load status database
                            C: Add user
                            D: Update user
                            E: Search user
                            F: Delete user
                            G: Add status
                            H: Update status
                            I: Search status
                            J: Delete status
                            K: Add picture
                            L: List user images
                            M: Reconcile images
                            Q: Quit

                            Please enter your choice: """
        ).upper()

        if user_selection in menu_options:
            menu_options[user_selection]()
        else:
            print("Invalid option")
