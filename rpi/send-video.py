import time, socket, imagezmq
from imutils.video import VideoStream

sender = imagezmq.ImageSender(connect_to='tcp://192.168.1.74:5555')
#rpi_name = socket.gethostname()
rpi_name = time.time()
picam = VideoStream(usePiCamera=True).start()
time.sleep(2.0)
while True:
    rpi_name = time.time()
    image = picam.read()
    sender.send_image(rpi_name, image)(py)