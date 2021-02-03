import cv2, imagezmq
import numpy as np
import time
image_hub = imagezmq.ImageHub()
while True:
    rpi_name, image = image_hub.recv_image()
    image = np.rot90(image, 2)
    print(f'Took this long : {round(time.time()-int(rpi_name))}')
    cv2.imshow('bin', image)
    cv2.waitKey(1)
    image_hub.send_reply(b'OK')