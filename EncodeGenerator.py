import os
import cv2
import face_recognition
import pickle
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://faceattendance-a570e-default-rtdb.firebaseio.com/",
    'storageBucket': "faceattendance-a570e.appspot.com"
})

#  Import student images
folderPath = 'Images'
pathList = os.listdir(folderPath)
imgList = []
studentIds = []
for path in pathList:
    imgList.append(cv2.imread(os.path.join(folderPath, path)))  # Add images to list
    studentIds.append(os.path.splitext(path)[0])  # Add student ids to list

    fileName = f'{folderPath}/{path}'
    bucket = storage.bucket()
    blob = bucket.blob(fileName)
    blob.upload_from_filename(fileName)


def findEncodings(imagesList):
    encodeList = []
    for img in imagesList:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  # opencv uses BGR, face-rec uses RGB
        encode = face_recognition.face_encodings(img)[0]
        encodeList.append(encode)

    return encodeList


print('Starting to encode')
encodeListKnown = findEncodings(imgList)  # numpy
# print(encodeListKnown[0].ndim)

encodeListKnownWithIds = [encodeListKnown, studentIds]
print('Encoding done')

file = open("EncodeFile.p", "wb")
pickle.dump(encodeListKnownWithIds, file)
file.close()
print('File saved')
