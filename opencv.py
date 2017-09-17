import cv2
import time
import os
#import config
import sys
import pprint
#from tqdm import tqdm

from helpers import send_face_detected




def sourceImagePaths(directory):
    result = []
    for filename in os.listdir(directory):
        if filename.endswith(".jpg"):
            result.append(os.path.join(directory, filename))
    return result


def main():
    # Loading and report setup
    report = {}
    report['corrupted'] = []
    face_cascade = cv2.CascadeClassifier(config.CASCADECLASSIFIER_PATH)

    # Image processing
    for imagepath in tqdm(sourceImagePaths(config.IMAGE_PATH)):
        image = cv2.imread(imagepath) 
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        except cv2.error:
            report['corrupted'].append(imagepath)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)
        nFaces = 0
        # Face analysis
        for (x, y, w, h) in faces:
            if not image is None:
                nFaces += 1
                # image = cv2.rectangle(image, (x, y), (x + w, y + h), (255, 0, 0), 2)
                # roi_gray = gray[y:y+h, x:x+w]
                roi_color = image[y:y + h, x:x + w]
                targetfile = os.path.split(imagepath)[1]
                targetfile = "".join(targetfile.split(".")[:-1]) + "_clipped_{}.jpg".format(nFaces)
                targetpath = os.path.join(config.TARGET_FOLDER, targetfile)
                print(targetpath)
                cv2.imwrite(targetpath, roi_color)
        report[imagepath] = nFaces

    # Report postprocessing
    report['classifier'] = config.CASCADECLASSIFIER_PATH
    report['countreport'] = {}
    for key in report:
        if not key in ['corrupted', 'countreport', 'classifier']:
            report['countreport'][report[key]] = report['countreport'].get(report[key], 0) + 1
    pprint.pprint(report)


if __name__ == '__main__':
    import django
    django.setup()

    face_cascade = cv2.CascadeClassifier('/home/fako/opencv-3.1.0/data/haarcascades/haarcascade_frontalface_default.xml')
    while True:
        cap = cv2.VideoCapture(0)
        time.sleep(2)
        ret, img = cap.read()
        cap.release()
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)


        faces = face_cascade.detectMultiScale(gray, 1.3, 5)
        for (x, y, w, h) in faces:
            print(w,h)
            if w >= 100 and h >= 100:
                send_face_detected()
#     img = cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
#     # roi_gray = gray[y:y+h, x:x+w]
#     # roi_color = img[y:y+h, x:x+w]

    #cv2.imshow('picture', img)

    #cv2.destroyAllWindows()

