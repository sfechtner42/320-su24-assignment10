"""
Main driver for a simple social network project using a functional approach
"""

import csv
import logging
import pathlib
from peewee import IntegrityError
from context_manager import Connection

# pylint: disable = C0301, E1101, W0718, W0613, W1514, E1121

USER_TABLE = "UserModel"
STATUS_TABLE = "StatusModel"
PICTURE_TABLE = "PictureModel"

logging.basicConfig(level=logging.INFO)

# Configure logging
logging.basicConfig(
    filename='A09_logger.txt',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filemode='a'
)

def log_decorator(func):
    '''log decorator that can be added to a function. Returns a function_logs.txt file'''

    def wrapper(*args, **kwargs):
        logging.info("Calling function %s with arguments %s %s", func.__name__, args, kwargs)
        result = func(*args, **kwargs)
        logging.info("Function %s returned %s", func.__name__, result)
        return result

    return wrapper


@log_decorator
def init_database(db_path):
    """Initialize the database by creating user, status, and picture tables."""
    with Connection(db_path) as db:
        db.create_table('users', ['user_id', 'user_name', 'user_last_name', 'user_email'])
        db.create_table('statuses', ['status_id', 'user_id', 'status_text'])
        db.create_table('pictures', ['picture_id', 'user_id', 'picture_path'])

    print("Database initialized successfully.")


# Load databases
def load_users(db_path, filename):
    """
    Opens a CSV file with user data and adds it to the database using ContextManager.
    """
    try:
        with open(filename, encoding="utf-8", newline="") as csvfile:
            reader = csv.DictReader(csvfile)
            with Connection(db_path) as db:
                user_table = db.user_table
                for row in reader:
                    if all(
                            key in row and row[key]
                            for key in ["USER_ID", "EMAIL", "NAME", "LASTNAME"]
                    ):
                        user_data = {
                            "user_id": row["USER_ID"],
                            "user_email": row["EMAIL"],
                            "user_name": row["NAME"],
                            "user_last_name": row["LASTNAME"],
                        }
                        try:
                            user_table.insert(**user_data)
                        except IntegrityError:
                            print(f"Failed to add user due to IntegrityError: {user_data}")
            return True
    except (FileNotFoundError, KeyError) as e:
        print(f"An error occurred while loading users: {e}")
        return False


def load_status_updates(db_path, filename):
    """
    Opens a CSV file with status update data and adds it to the database using ContextManager.
    """
    try:
        with open(filename, encoding="utf-8", newline="") as csvfile:
            reader = csv.DictReader(csvfile)
            with Connection(db_path) as db:
                status_table = db.status_table
                for row in reader:
                    if all(
                            key in row and row[key]
                            for key in ["STATUS_ID", "USER_ID", "STATUS_TEXT"]
                    ):
                        status_data = {
                            "status_id": row["STATUS_ID"],
                            "user_id": row["USER_ID"],
                            "status_text": row["STATUS_TEXT"],
                        }
                        try:
                            status_table.insert(**status_data)
                        except IntegrityError:
                            print(f"Failed to add status due to IntegrityError: {status_data}")
            return True
    except (FileNotFoundError, KeyError) as e:
        print(f"An error occurred while loading statuses: {e}")
        return False


def validate_length(value, max_length):
    """Utility function to validate the length of a given value."""
    if len(value) > max_length:
        print(f"Value '{value}' exceeds maximum length of {max_length} characters.")
        return False
    return True


# User-related functions

def add_user(db_path, user_id, user_name, user_last_name, user_email):
    """Add a new user to the database."""
    with Connection(db_path) as db:
        user_table = db.user_table
        try:
            user_table.insert(user_id=user_id, user_name=user_name, user_last_name=user_last_name,
                              user_email=user_email)
            print(f"User {user_id} added successfully.")
            return True
        except Exception as e:
            print(f"Error adding user: {e}")
            return False


def update_user(db_path, user_id, user_name=None, user_last_name=None, user_email=None):
    """
    Updates the values of an existing user.

    Requirements:
    - Returns False if there are any errors.
    - Otherwise, it returns True.
    """
    try:
        with Connection(db_path) as db:
            user_table = db.user_table

            # Check if the user exists
            user_to_modify = user_table.find_one(user_id=user_id)
            if not user_to_modify:
                print("User not found.")
                return False

            # Prepare the update data
            updated_data = {}
            if user_id:
                updated_data["user_id"] = user_id
            if user_email:
                updated_data['user_email'] = user_email
            if user_name:
                updated_data['user_name'] = user_name
            if user_last_name:
                updated_data['user_last_name'] = user_last_name

            if not updated_data:
                print("No fields to update.")
                return False

            # first delete the old record and then insert the updated record.
            with db.ds.transaction():
                # First, remove the old record
                user_table.delete(user_id=user_id)
                # Insert the updated record
                user_table.insert(**updated_data)

            print(f"User {user_id} updated successfully.")
            return True
    except Exception as e:
        print(f"Error updating user: {user_id}. Exception message: {e}")
        return False


def delete_user(user_id):
    """Delete a user and associated statuses and pictures from the database."""
    with Connection() as db:
        try:
            # Flag to track if all deletions are successful
            all_statuses_deleted = True
            user_deleted = False

            # Retrieve and delete all statuses associated with the user
            statuses = db.status_table.find(user_id=user_id)
            for status in statuses:
                status_id = status["status_id"]
                try:
                    status_to_delete = db.status_table.find_one(status_id=status_id)
                    if status_to_delete:
                        db.status_table.delete(id=status_to_delete["id"])
                    else:
                        print(f"Status record not found for status_id: {status_id}")
                        all_statuses_deleted = False
                except Exception as e:
                    print(f"Failed to delete status with status_id: {status_id}. Error: {e}")
                    all_statuses_deleted = False

            # Delete the user
            user_to_delete = db.user_table.find_one(user_id=user_id)
            if user_to_delete:
                db.user_table.delete(id=user_to_delete["id"])
                user_deleted = True
            else:
                print(f"User record not found for user_id: {user_id}")
                user_deleted = False

            # Return True only if both statuses and user were successfully deleted
            return all_statuses_deleted and user_deleted

        except Exception as e:
            print(f"An error occurred while deleting user: {e}")
            return False


def search_user(db_path):
    """
    Returns a function to search for a user by user_id in the database using ContextManager.
    """

    def search(user_id):
        with Connection(db_path) as db:
            try:
                user = db.user_table.find_one(user_id=user_id)
                if user is None:
                    print(f"User with user_id {user_id} not found.")
                    return None
                return user
            except Exception as e:
                print(f"An error occurred while searching for user_id {user_id}: {e}")
                return None

    return search

# Status-related functions

def add_status(db_path, status_id, user_id, status_text):
    """Add a new status update to the database."""
    with Connection(db_path) as db:
        try:
            user_table = db.user_table
            status_table = db.status_table
            # Ensure the user exists before adding status
            if user_table.find_one(user_id=user_id):
                status_table.insert(user_id=user_id, status_id=status_id, status_text=status_text)
                print(f"Status {status_id} added successfully.")
            else:
                print(f"User {user_id} does not exist.")
        except Exception as e:
            print(f"Error adding status: {e}")


def update_status(db_path, status_id, user_id=None, status_text=None):
    """Update the text of an existing status."""
    try:
        with Connection(db_path) as db:
            status_table = db.status_table

            # Check if the status exists
            status_to_modify = status_table.find_one(status_id=status_id)
            if not status_to_modify:
                print(f"Status record not found for status_id: {status_id}")
                return False

            # Prepare the update data, keeping the old user_id if not provided
            updated_data = {
                "status_id": status_id,  # Always keep the status_id
                "user_id": user_id if user_id else status_to_modify["user_id"],  # Keep the old user_id if not provided
            }

            if status_text:
                updated_data["status_text"] = status_text
            else:
                updated_data["status_text"] = status_to_modify[
                    "status_text"]  # Keep the old status_text if not updating

            # No fields to update
            if not updated_data:
                print("No fields to update.")
                return False

            # Delete the old record first, then add the updated record
            with db.ds.transaction():
                status_table.delete(status_id=status_id)
                status_table.insert(**updated_data)
                print(f"Status {status_id} updated successfully.")
                return True
    except Exception as e:
        print(f"Error updating status: {status_id}. Exception message: {e}")
        return False


def delete_status(status_id):
    """Delete a status update from the database."""
    with Connection() as db:
        statuses = db.status_table.find(status_id=status_id)
        for status in statuses:
            status_id = status["status_id"]
            try:
                status_to_delete = db.status_table.find_one(status_id=status_id)
                if status_to_delete:
                    db.status_table.delete(id=status_to_delete["id"])
                    return True
                print(f"Status record not found for status_id: {status_id}")
                return False
            except Exception as e:
                print(f"Error deleting status: {e}")
                return False


def search_status(db_path, status_id):
    """
    Searches for a status in the database and returns its data if found using ContextManager.
    """
    with Connection(db_path) as db:
        try:
            # Correctly query the status table
            status = db.status_table.find_one(status_id=status_id)
            if status is None:
                print(f"Status with status_id {status_id} not found.")
                return None
            return status
        except Exception as e:
            print(f"An error occurred while searching for status_id {status_id}: {e}")
            return None


def deconstruct_tags(tags):
    '''
    Deconstructs a string of tags into a list of tags
    '''
    tags = " " + tags  # Add extra space at the start so split works
    tags_list = tags.split(" #")
    return sorted(tags_list[1:])  # Skip the first empty slot and return a sorted list


def save_picture_to_disk(user_id, picture_id, tags):
    '''
    Saves the picture to disk by creating appropriate directories
    '''
    # Deconstruct the tags into a list
    tag_list = deconstruct_tags(tags)

    # Create the folder path and make the directories
    folder_path = pathlib.Path("pictures") / user_id / pathlib.Path(*tag_list)
    folder_path.mkdir(parents=True, exist_ok=True)  # Create directories if they don't exist

    # Create the file path and create an empty file
    file_path = folder_path / f"{picture_id}.png"
    with open(file_path, "w"):
        pass  # Creating an empty file (replace with actual file saving logic)

    print(f"Picture saved to: {file_path}")


def add_picture(user_id, tags):
    """
    Adds a picture to the database for a specific user and saves it to disk.
    """
    with Connection() as db:
        picture = db.picture_table.model_class
        user = db.user_table.model_class

        # Check if the user ID exists in the USER_TABLE
        user_exists = user.select().where(user.user_id == user_id).exists()

        if not user_exists:
            print(f"User with ID {user_id} does not exist. Cannot add picture.")
            return False

        # Find the last picture entry in the PICTURE_TABLE by ordering by ID descending
        last_picture = picture.select().order_by(picture.id.desc()).limit(1).first()

        # Generate a new picture_id
        if last_picture:
            last_id = int(last_picture.id)
        else:
            last_id = 0

        new_picture_id = str(last_id + 1).zfill(10)  # Increment the last picture ID

        # Insert the new picture into the database
        picture_data = {
            'picture_id': new_picture_id,
            'user_id': user_id,
            'tags': tags
        }

        try:
            # Insert the new picture into the database
            db.picture_table.insert(**picture_data)
            print(f"Picture {new_picture_id} added successfully for user {user_id}.")

            # Save the picture to disk after successfully adding it to the database
            save_picture_to_disk(user_id, new_picture_id, tags)

            return True
        except IntegrityError:
            print(f"Failed to add picture due to IntegrityError: {picture_data}")
            return False


def list_user_images(db_path, user_id):
    """Recursively lists all image paths for a given user."""

    def find_images(directory):
        """Helper function to recursively find images in the given directory."""
        images = []
        for item in directory.iterdir():
            if item.is_dir():
                images.extend(find_images(item))
            elif item.is_file() and item.suffix == ".png":
                file_name = item.name
                relative_path = item.relative_to(folder_path)
                images.append((user_id, str(relative_path), file_name))
        return images

    folder_path = pathlib.Path("pictures") / user_id

    try:
        if not folder_path.exists():
            print(f"No images found for user {user_id}.")
            return []

        images = find_images(folder_path)

        if images:
            return images
        print(f"No images found for user {user_id}.")
        return []

    except Exception as e:
        print(f"Error retrieving pictures: {e}")
        return []


def reconcile_images(db_path, user_id):
    """
    Reconcile the images listed in the database with actual image files in the given directory.
    Returns:
        dict: A dictionary with two lists: 'in_db_not_on_disk' and 'on_disk_not_in_db'.
    """
    images_on_disk = list_user_images(db_path, user_id)
    images_in_db = []

    with Connection(db_path) as conn:
        records = conn.picture_table.find(user_id=user_id)
        for record in records:
            tags_path = pathlib.Path(*deconstruct_tags(record["tags"]))
            # Construct the full path with the image file name and extension
            full_image_path = tags_path.joinpath(f"{record['picture_id']}.png")
            images_in_db.append((user_id, str(full_image_path), f"{record['picture_id']}.png"))

    # Print out the lists for debugging
    print("Images on Disk:", images_on_disk)
    print("Images in DB:", images_in_db)

    # Compare the full paths in both sets
    missing_in_db = set(images_on_disk) - set(images_in_db)
    missing_on_disk = set(images_in_db) - set(images_on_disk)

    # Print out the differences for debugging
    # print("Images not in database:", missing_in_db)
    # print("Images not on disk:", missing_on_disk)

    return missing_in_db, missing_on_disk
