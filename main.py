"""
Name:                Nilay Shah
Enrollment No:       22002171210088
Batch:               B1 - 2

Facial Recognition Attendance System
"""
import time
from datetime import datetime
import os
import pickle
import cv2
import face_recognition
import numpy as np
import cvzone
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://faceattendance-a570e-default-rtdb.firebaseio.com/",
    'storageBucket': "faceattendance-a570e.appspot.com"
})

bucket = storage.bucket()

cap = cv2.VideoCapture(0)
cap.set(3, 640)  # Set Width
cap.set(4, 480)  # Set Height

imgBackground = cv2.imread('Resources/background.png')

#  Import modes to list
folderModePath = 'Resources/Modes'
modePathList = os.listdir(folderModePath)
imgModeList = []
for path in modePathList:
    imgModeList.append(cv2.imread(os.path.join(folderModePath, path)))
# print(len(imgModeList))


#  Load the EncodeFile
print("Loading encoded file...")
file = open("EncodeFile.p", "rb")
encodeListKnownWithIds = pickle.load(file)
file.close()
encodeListKnown, studentIds = encodeListKnownWithIds
# print(studentIds)
print("Loaded encoded file")

modeType = 0
counter = 0  # Retrieve data only once when detected
id = -1
imgStudent = []
try:
    while True:
        if cv2.waitKey(1) & 0xFF == ord('q'):
            cv2.destroyAllWindows()
            break
        success, img = cap.read()

        imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
        imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

        faceCurrentFrame = face_recognition.face_locations(imgS)  # Get location of only face
        encodeCurrentFrame = face_recognition.face_encodings(imgS, faceCurrentFrame)  # Get encoding of the face only

        imgBackground[162:162 + 480, 55:55 + 640] = img # Set webcam position
        imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType] # Set mode

        if faceCurrentFrame:  # If there's a face

            for encodeFace, faceLocation in zip(encodeCurrentFrame, faceCurrentFrame):
                matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
                faceDistance = face_recognition.face_distance(encodeListKnown, encodeFace)
                # print("matches", matches)
                # print("distances", faceDistance)

                matchIndex = np.argmin(faceDistance)
                print(faceDistance)
                if faceDistance[matchIndex] <= 0.44:
                    if matches[matchIndex]:

                        # print("Known Face Detected")
                        # print(studentIds[matchIndex])
                        y1, x2, y2, x1 = faceLocation
                        y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                        bbox = 55 + x1, 162 + y1, x2 - x1, y2 - y1
                        imgBackground = cvzone.cornerRect(imgBackground, bbox, rt=0)

                        id = studentIds[matchIndex]

                        if counter == 0:
                            cvzone.putTextRect(imgBackground, "Loading", (275, 400))
                            cv2.imshow("Face", imgBackground)
                            cv2.waitKey(1)
                            if cv2.getWindowProperty("Face", cv2.WND_PROP_VISIBLE) < 1:
                                break
                            counter = 1
                            modeType = 1
                else:
                    y1, x2, y2, x1 = faceLocation
                    y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                    bbox = 55 + x1, 162 + y1, x2 - x1, y2 - y1
                    imgBackground = cvzone.cornerRect(imgBackground, bbox, rt=0,colorC=(0,0,255))


            if counter != 0:
                if counter == 1:
                    if cv2.getWindowProperty("Face", cv2.WND_PROP_VISIBLE) < 1:
                        break
                    # Get Data 1 time
                    studentInfo = db.reference(f'Students/{id}').get()
                    print(studentInfo)
                    # Get Image
                    blob = bucket.get_blob(f'Images/{id}.png')
                    array = np.frombuffer(blob.download_as_string(), np.uint8)
                    imgStudent = cv2.imdecode(array, cv2.COLOR_BGRA2BGR)

                    # Update date
                    # try:
                    datetimeObject = datetime.strptime(studentInfo['last_attendance_time'],
                                                           "%Y-%m-%d %H:%M:%S")
                    # except (TypeError, Exception):
                    #     cv2.destroyAllWindows()
                    #     print('Corrupt DB')
                    #     break
                    secondsElapsed = (datetime.now() - datetimeObject).total_seconds()

                    if secondsElapsed > 30:
                        ref = db.reference(f'Students/{id}')
                        studentInfo['total_attendance'] += 1
                        ref.child('total_attendance').set(studentInfo['total_attendance'])
                        ref.child('last_attendance_time').set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                    else:
                        modeType = 3
                        counter = 0
                        imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]
                        if cv2.getWindowProperty("Face", cv2.WND_PROP_VISIBLE) < 1:
                            break

                if modeType != 3:

                    if 10 < counter < 20:
                        modeType = 2

                    imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]

                    if counter <= 10:
                        cv2.putText(imgBackground, str(studentInfo['total_attendance']), (850, 125), cv2.FONT_HERSHEY_SIMPLEX,
                                    1, (255, 255, 255), 1)
                        cv2.putText(imgBackground, str(studentInfo['major']), (1006, 550), cv2.FONT_HERSHEY_SIMPLEX,
                                    0.3, (255, 255, 255), 1)
                        cv2.putText(imgBackground, str(id), (1006, 493), cv2.FONT_HERSHEY_SIMPLEX,
                                    0.4, (255, 255, 255), 1)
                        cv2.putText(imgBackground, str(studentInfo['standing']), (910, 625), cv2.FONT_HERSHEY_SIMPLEX,
                                    0.6, (100, 100, 100), 1)
                        cv2.putText(imgBackground, str(studentInfo['sem']), (1025, 625), cv2.FONT_HERSHEY_SIMPLEX,
                                    0.6, (100, 100, 100), 1)
                        cv2.putText(imgBackground, str(studentInfo['starting_year']), (1125, 625), cv2.FONT_HERSHEY_SIMPLEX,
                                    0.6, (100, 100, 100), 1)

                        (w, h), _ = cv2.getTextSize(studentInfo['name'], cv2.FONT_HERSHEY_SIMPLEX, 1, 1)
                        offset = (414 - w) // 2
                        cv2.putText(imgBackground, str(studentInfo['name']), (808 + offset, 445), cv2.FONT_HERSHEY_SIMPLEX,
                                    1, (50, 50, 50), 1)

                        imgBackground[175:175 + 216, 909:909 + 216] = imgStudent

                    counter += 1

                    if counter >= 20:
                        counter = 0
                        modeType = 0
                        studentInfo = []
                        imgStudent = []
                        imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]
        else:
            modeType = 0
            counter = 0
            imgBackground[162:162 + 480, 55:55 + 640] = img

        # cv2.imshow("Webcam", img)
        cv2.imshow("Face", imgBackground)
        cv2.waitKey(1)

        if cv2.getWindowProperty("Face", cv2.WND_PROP_VISIBLE) < 1:
            break
except (KeyboardInterrupt, Exception) as e:
    print('Crashed!')

cv2.destroyAllWindows()