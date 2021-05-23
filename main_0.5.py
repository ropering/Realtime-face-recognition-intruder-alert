
'''스레딩 라이브러리'''
import threading
'''얼굴인식 라이브러리'''
import cv2
'''시간측정 라이브러리'''
import time
from datetime import datetime
'''메일 전송 라이브러리'''
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
'''이미지 전송 라이브러리'''
from email.mime.image import MIMEImage


'''카메라 사용 전 선언부'''
recognizer = cv2.face.LBPHFaceRecognizer_create()
recognizer.read('trainer/trainer.yml')
cascadePath = 'xml/haarcascade_frontalface_default.xml'
faceCascade = cv2.CascadeClassifier(cascadePath)
font = cv2.FONT_HERSHEY_SIMPLEX

id = 0

# 이런식으로 사용자의 이름을 사용자 수만큼 추가해준다.
names = ['None','OMG']

# 카메라 초기설정
cap = cv2.VideoCapture(0)
cap.set(3, 640) # set video widht
cap.set(4, 480) # set video height

# 얼굴을 인식하는 최소 창 크기 설정 
minW = 0.1*cap.get(3)
minH = 0.1*cap.get(4)

class Thread1(threading.Thread):
    def run(self):
        '''반복문으로 얼굴인식'''
        global id
        while True:
            ret, img = cap.read()
            img = cv2.flip(img, -1)
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = faceCascade.detectMultiScale(
                gray,     
                scaleFactor=1.2,
                minNeighbors=5,     
                minSize=(int(minW), int(minH))
            )
            for (x,y,w,h) in faces:
                cv2.rectangle(img,(x,y),(x+w,y+h),(0,255,0),2)
                id, confidence = recognizer.predict(gray[y:y+h, w:w+w])

                if confidence < 100:
                    id = names[id]
                    confidence = "  {0}%".format(round(100 - confidence)+65)
                else:
                    id = "unknown"
                    confidence = "  {0}%".format(round(100 - confidence)+65)

                cv2.putText(img, str(id), (x+5, y-5), font, 1, (255,255,255), 2)
                cv2.putText(img, str(confidence), (x+5, y+h-5), font, 1, (255,255,0), 1)


            cv2.imshow('video',img)
            k = cv2.waitKey(30) & 0xff
            if k == 27: # press 'ESC' to quit
                break
    

class Thread2(threading.Thread):
    def run(self) -> None:
        while(1):
            if id == "unknown":
                print("이메일을 전송합니다")
                '''메일 초기설정'''
                sender_email = "" # 보내는 이메일 주소
                receiver_email = "" # 받는 이메일 주소
                password = input("Type your password and press enter:")
                

                message = MIMEMultipart("alternative")
                message["Subject"] = "multipart test"
                message["From"] = sender_email
                message["To"] = receiver_email

                html = """\
                <html>
                <body>
                    <p><h1>
                    침입자를 발견하였습니다!
                    <h1><p>
                </body>
                </html>
                """

                '''사진촬영 & 저장 부분'''
                ret, frame = cap.read()
                cv2.imwrite('cctv.png',frame, params=[cv2.IMWRITE_PNG_COMPRESSION,0])
                # cap.release()
                print("image capture & save completed")

                '''텍스트 & 이미지 첨부'''
                open_image = open('cctv.png', 'rb').read()
                part2 = MIMEText(html, "html")
                part3 = MIMEImage(open_image, "png")    
                message.attach(part2)
                message.attach(part3)

                '''메일 전송'''
                print("sending mail.....")
                rec = datetime.now() #메일전송시간 측정을 위한 변수

                context = ssl.create_default_context()
                with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
                    server.login(sender_email, password)
                    server.sendmail(
                        sender_email, receiver_email, message.as_string()
                        )
                print('send mail completed')
                print('메일 전송에 걸린 시간 : {}초 입니다!'.format(datetime.now() - rec))

                time.sleep(10)

# cap.release()
# cv2.destroyAllWindows() 

t1 = Thread1
t2 = Thread2

t1.start()
t2.start()