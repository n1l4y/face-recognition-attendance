import os
from datetime import datetime
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import pandas as pd
import cv2

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://faceattendance-a570e-default-rtdb.firebaseio.com/"
})

ref = db.reference('Students')

def resize_save_img(input_path, new_name):
    image = cv2.imread(input_path)
    resized_image = cv2.resize(image, (216, 216))
    output_filename = os.path.join("Images/", new_name + ".png")
    cv2.imwrite(output_filename, resized_image)


def add_test_data():
    data = {
        "22002171210088": {
            "name": "Nilay Shah",
            "major": "Computer Science",
            "starting_year": 2022,
            "total_attendance": 12,
            "standing": "G",
            "sem": 3,
            "last_attendance_time": "2024-04-03 08:48:34"
        },
        "22002171210033": {
            "name": "Elon Musk",
            "major": "Physics",
            "starting_year": 2021,
            "total_attendance": 7,
            "standing": "G",
            "sem": 6,
            "last_attendance_time": "2024-04-03 08:48:34"
        }
    }

    for key, value in data.items():
        ref.child(key).set(value)


# add_test_data()

### Add Data yourself

df = pd.read_csv('New_Data.csv')

data = dict()
for index, row in df.iterrows():
    try:
        name = row['name']
        enrollment_no = str(int(row['enrollment_no']))
        sem = row['sem']
        major = row['major']
        starting_year = row['starting_year']
        standing = row['standing']
        total_attendance = row['total_attendance']
        pic_path = row['pic_path']

        resize_save_img(pic_path, enrollment_no)
    except (cv2.error, Exception):
        print(f'Failed to add {name}')
        continue

    data[enrollment_no] = {
        "name": name,
        "major": major,
        "starting_year": starting_year,
        "total_attendance": total_attendance,
        "standing": standing,
        "sem": sem,
        "last_attendance_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

for key, value in data.items():
    try:
        ref.child(key).set(value)
    except (ValueError, Exception) as e:
        print(f'Entry failed for {key}')
        continue