import random
import warnings
warnings.filterwarnings("ignore", category=UserWarning, message='SymbolDatabase.GetPrototype() is deprecated')
import cv2
import csv
from cvzone.HandTrackingModule import HandDetector
import cvzone
import time

# Inicjalizacja przechwytywania wideo z domyślnej kamery.
cap = cv2.VideoCapture(0)
cap.set(3, 1280)  # Ustawienie szerokości ramki wideo.
cap.set(4, 720)   # Ustawienie wysokości ramki wideo.

# Inicjalizacja detektora dłoni z maksymalnie jedną dłonią na ekranie.
detector = HandDetector(maxHands=2, detectionCon=1)

class Quiz():
    def __init__(self, data):
        self.pytanie, self.odp1, self.odp2, self.odp3, self.odp4, self.prawOdp = data
        self.prawOdp = int(self.prawOdp)
        self.userOdp = None

    def update(self, cursor, bboxs):
        for i, bbox in enumerate(bboxs):
            x1, y1, x2, y2 = bbox
            if x1 < cursor[0] < x2 and y1 < cursor[1] < y2:
                self.userOdp = i + 1
                cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), cv2.FILLED)

# Wczytanie pytań z pliku CSV.
pathCSV = "pytania.csv"
with open(pathCSV, newline='\n') as f:
    reader = csv.reader(f)
    pytaniaLista = [Quiz(row) for row in reader]

random.shuffle(pytaniaLista)
pytanieNumer = 0
pytaniaSuma = 1 #len(pytaniaLista)
graStart = False
quizZakonczony = False

while True:
    success, img = cap.read()
    img = cv2.flip(img, 1)
    hands, img = detector.findHands(img)

    if not graStart:
        img, bboxStart = cvzone.putTextRect(img, "Start", [300, 250], 2, 2, offset=50, border=5)
        img, bboxQuit = cvzone.putTextRect(img, "Wyjdz", [800, 250], 2, 2, offset=50, border=5)

        if hands:
            cursor = hands[0]['lmList'][8]
            if 300 < cursor[0] < 750 and 250 < cursor[1] < 320:
                graStart = True
                time.sleep(1)
            elif 300 < cursor[0] < 750 and 500 < cursor[1] < 570:
                break
    elif not quizZakonczony:
        if pytanieNumer < pytaniaSuma:
            quiz = pytaniaLista[pytanieNumer]
            bboxs = []
            img, _ = cvzone.putTextRect(img, quiz.pytanie, [100, 100], 2, 2, offset=50, border=5)
            bboxs = [cvzone.putTextRect(img, getattr(quiz, f'odp{i+1}'), [100 if i % 2 == 0 else 800, 250 if i < 2 else 500], 2, 2, offset=50, border=5)[1] for i in range(4)]

            if hands:
                cursor = hands[0]['lmList'][8]
                length, info = detector.findDistance(hands[0]['lmList'][8], hands[0]['lmList'][12])
                if length < 30:
                    quiz.update(cursor, bboxs)
                    if quiz.userOdp is not None:
                        time.sleep(1)
                        pytanieNumer += 1

            # Pasek postępu
            barValue = 150 + (950 // pytaniaSuma) * pytanieNumer
            cv2.rectangle(img, (150, 600), (barValue, 650), (0, 255, 0), cv2.FILLED)
            cv2.rectangle(img, (150, 600), (1100, 650), (255, 0, 255), 5)
            img, _ = cvzone.putTextRect(img, f'{round((pytanieNumer / pytaniaSuma) * 100)}%', [1130, 635], 2, 2, offset=16)


        else:

            quizZakonczony = True

    if quizZakonczony:
        score = 0
        for quiz in pytaniaLista:
            if quiz.prawOdp == quiz.userOdp:
                score += 1
        score = round((score / pytaniaSuma) * 100, 2)
        img, _ = cvzone.putTextRect(img, "Quiz Zakonczony", [250, 300], 2, 2, offset=50, border=5)
        img, _ = cvzone.putTextRect(img, f'Twoj rezultat: {score}%', [700, 300], 2, 2, offset=50, border=5)
        cv2.putText(img, "Przygotowal zespol STONKS-Together: Artur, Bogdan, Konrad, Radoslaw All rights reserved", (1, 700), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    cv2.imshow("Quiz", img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()