# Face Recognition Attendance System

Implementation of a attendance system using the face-recognition module, with Firebase 

## Installation

Python Version: 3.7

Microsoft Visual Studio: C/C++ 

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install following packages:

```bash
pip install cmake==3.25.0
pip install dlib==9.24.0
pip install face-recognition
pip install cvzone
pip install opencv-python===4.5.4.60
```

Add serviceAccountKey.json from Firebase database to project root
## Usage

```python
import face-recognition

# Get location of only face
faceCurrentFrame = face_recognition.face_locations(imgS)  
# Get encoding of the face only
encodeCurrentFrame = face_recognition.face_encodings(imgS, faceCurrentFrame)  

# Compare
matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
faceDistance = face_recognition.face_distance(encodeListKnown, encodeFace)
```

## Contributing

Pull requests are welcome. For major changes, please open an issue first
to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License

[MIT](https://choosealicense.com/licenses/mit/)