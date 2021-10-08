import time
import os
import matplotlib.pyplot as plt
from imageAI import ImageAI_videoObjectDetection
from openCV import OpenCV_videoObjectDetection

dict = {}

input_path = "input_videos/bicycle_1fps.mp4"

#Line used to see all the error messages about the nvidia gpu we don't have
#It enables the next function calls to not loose time with error messages
ImageAI_videoObjectDetection("fast", input_path)

for filename in os.listdir("output_videos"):
    if not filename.startswith('.'): #To not remove the .keep file
        os.remove("output_videos/" + filename)

start_time = time.time()
ImageAI_videoObjectDetection("normal", input_path)
dict["imageAI_normal"] = time.time() - start_time

start_time = time.time()
ImageAI_videoObjectDetection("fast", input_path)
dict["imageAI_fast"] = time.time() - start_time

start_time = time.time()
ImageAI_videoObjectDetection("fastest", input_path)
dict["imageAI_fastest"] = time.time() - start_time

start_time = time.time()
ImageAI_videoObjectDetection("flash", input_path)
dict["imageAI_flash"] = time.time() - start_time

start_time = time.time()
OpenCV_videoObjectDetection((320, 320), input_path)
dict["openCV_320"] = time.time() - start_time

start_time = time.time()
OpenCV_videoObjectDetection((416, 416), input_path)
dict["openCV_416"] = time.time() - start_time

start_time = time.time()
OpenCV_videoObjectDetection((608, 608), input_path)
dict["openCV_608"] = time.time() - start_time

fig = plt.figure()

x = dict.keys()
y = dict.values()

plt.xticks(rotation='vertical')

plt.xlabel("Paramètres")
plt.ylabel("Temps (en s)")
plt.bar(x, y, color=['blue']*4 + ['red']*3)

for index, data in enumerate(y):
    plt.text(x=index-0.3, y=data+0.3, s="{:.2f}".format(data), color='black', fontweight='bold')

spacing = 0.300
fig.subplots_adjust(bottom=spacing)
plt.savefig("result_1fps.png")
plt.show()