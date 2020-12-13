## 이메일 발송 래퍼 기능.
from threading import Thread
from flask_mail import Message
from app import mail
#from app import mail, app
from flask import current_app


# 이메일을 비동기적으로 보내기

def send_async_email(app, msg):
    with app.app_context(): # 어플리케이션 컨텍스트가 생성되어 current_app 변수를 통해 애플리케이션 인스턴스에 액세스 할 수 있도록 함. 
                            # current_app - 활성화된 어플리케이션을 위한 인스턴스
        mail.send(msg) 





# 이메일을 보내면 애플리케이션 속도가 상당히 느려짐 
#  전자 메일을 보낼 때 발생하는 모든 상호 작용으로 인해 작업이 느려지고,
#  전자메일을 받는데 보통 몇 초가 걸리며, 수신자의 전자 메일 서버가 느리거나 여러 수신자가 있는경우에는 더 오래 걸릴 수 있다.
# send_email()함수를 비동기적으로 보내기
# -> 함수가 호출되면 이메일 전송 작업이 백그라운드에서 발생하도록 예약되어 
#    send_email() 애플리케이션이 전송되는 이메일과 동시에 계속 실행될 수 있도록 즉시 반환

# Python은 여러가지 방식으로 비동기 작업을 실행할 수 있도록 지원
#   -> threading 및 multiprocessiong 모듈로 수행 

# 이메일 발송 래퍼 기능.
def send_email(subject, sender, recipients, text_body, html_body ):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    #mail.send(msg)   # -> 이메일 비동기적으로 보내기위해 send_async_email() 함수에서 작성함.
    
    Thread( target=send_async_email, args=(current_app._get_current_object(), msg) ).start() 
    #Thread( target=send_async_email, args=(app, msg) ).start() 
    # threading 모듈의 Thread 클래스를 통해 호출되는 백그라운드 스레드에서 실행됨 
    # 이메일 전송은 스레드에서 실행되며 프로세스가 완료되면 스레드가 종료되고 스스로 정리됨
    # msg 인수 뿐만아니라 응용프로그램 인스턴스도 전송함

    # Flask는 함수 간에 인수를 전달할 필요가 없도록 컨텍스트를 사용 
    #   -> 애플리케이션 컨텍스트, 요청 컨텍스트
    #   -> 대부분의 경우 이러한 컨텍스트는 프레임워크에서 자동으로 관리되지만
    #       애플리케이션이 사용자 지정 스레드를 시작할 대 해당 스레드에 대한 컨텍스트를 수동으로 만들어야 할 수 있음.

    # 응용 프로그램 컨텍스트가 작동하도록 해야하는 많은 확장이 있는데, 
    #   이는 인수로 전달되지 않고도 Flask 응용 프로그램 인스턴스를 찾을 수 있기 때문
    #   -> 구성이 app.config 객체에 저장되어 있기 때문
    #   이것이 Flask-Mail의 상황.




