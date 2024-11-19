'''API to Display Users, Images, and Discrepancies'''

import pathlib
from flask import Flask, jsonify
from flask_restful import Api, Resource
from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.orm import sessionmaker

from main import deconstruct_tags

# pylint: disable = C0301
app = Flask(__name__)
api = Api(app)

# Configure the SQLite database
DATABASE_URL = 'sqlite:///databaseA10.db'
db_connect = create_engine(DATABASE_URL)
Session = sessionmaker(bind=db_connect)
session = Session()

# Reflect the database schema to access existing tables
metadata = MetaData()

# Define tables based on their names in the database, reflecting the schema
users = Table('users', metadata, autoload_with=db_connect)
pictures = Table('pictures', metadata, autoload_with=db_connect)


# API Resources
class Users(Resource):
    """Displays all users in database"""

    def get(self):
        """Fetch all users from the database."""
        conn = db_connect.connect()
        query = users.select()
        users_result = conn.execute(query).fetchall()

        users_list = [row._asdict() for row in users_result]  # Convert each row to dict

        if users_list:
            return jsonify(users_list)  # Return as a JSON array
        return jsonify([])


class Images(Resource):
    """Displays all images in database"""

    def get(self):
        """Fetch all images from the database."""
        conn = db_connect.connect()
        query = pictures.select()
        images_result = conn.execute(query).fetchall()

        images_list = [row._asdict() for row in images_result]

        if images_list:
            return jsonify(images_list)  # Return as a JSON array
        return jsonify([])


class Differences(Resource):
    """Displays all differences in database and disk"""

    def get(self):
        """Find discrepancies between image records and actual files on disk."""
        conn = db_connect.connect()
        users_list = self.get_users_list(conn)

        differences = []
        for user in users_list:
            user_id = user['user_id']  # Access user_id from the dictionary

            db_images = self.get_images_from_db(conn, user_id)
            disk_images = self.get_images_from_disk(user_id)

            # Compare and find discrepancies
            missing_in_db = set(disk_images) - set(db_images)
            missing_on_disk = set(db_images) - set(disk_images)

            if missing_in_db or missing_on_disk:
                differences.append({
                    "user_id": user_id,
                    "missing_in_db": list(missing_in_db),
                    "missing_on_disk": list(missing_on_disk)
                })

        return jsonify(differences)

    def get_users_list(self, conn):
        """Fetch and return the list of users."""
        users_query = users.select()
        users_result = conn.execute(users_query).fetchall()
        return [user._asdict() for user in users_result]

    def get_images_from_db(self, conn, user_id):
        """Fetch and return the list of image paths from the database."""
        db_images = []
        records_query = pictures.select().where(pictures.c.user_id == user_id)
        records_result = conn.execute(records_query).fetchall()
        records_list = [record._asdict() for record in records_result]

        for record in records_list:
            tags_path = pathlib.Path(user_id) / pathlib.Path(*deconstruct_tags(record['tags']))
            full_image_path = tags_path.joinpath(f"{record['picture_id']}.png")
            db_images.append(str(full_image_path))
        return db_images

    def get_images_from_disk(self, user_id):
        """List image files on disk for a given user."""
        disk_images = []
        folder_path = pathlib.Path("pictures") / user_id
        if folder_path.exists():
            for img_path in folder_path.rglob('*.png'):
                disk_images.append(str(img_path.relative_to(folder_path.parent)))
        return disk_images


# Add resource routes to the API
api.add_resource(Users, '/users')
api.add_resource(Images, '/images')
api.add_resource(Differences, '/differences')

if __name__ == '__main__':
    app.run(debug=True)
