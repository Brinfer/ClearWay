from imageai.Detection import VideoObjectDetection
import os

def forFrame(frame_number, output_array, output_count):
    if(output_count):
        for i in range(output_count["bicycle"]):
            print("Vélo détecté avec une probabilité de : {:.2f} %".format(output_array[i]["percentage_probability"]))


def ImageAI_videoObjectDetection(speed, path):
    execution_path = os.getcwd()

    detector = VideoObjectDetection()
    detector.setModelTypeAsYOLOv3()
    detector.setModelPath(os.path.join(execution_path , "imageAI_algorithm/yolo.h5"))
    detector.loadModel(detection_speed=speed)

    custom_objects = detector.CustomObjects(bicycle=True)

    video_path = detector.detectObjectsFromVideo(
        custom_objects=custom_objects,
        input_file_path=os.path.join(execution_path, path),
        output_file_path=os.path.join(execution_path+"/output_videos", path[13:-4]+"_imageAI_"+speed),
        #save_detected_video=False,
        frames_per_second=1,
        log_progress=False,
        per_frame_function=forFrame,
        minimum_percentage_probability=50)

    print(video_path)
