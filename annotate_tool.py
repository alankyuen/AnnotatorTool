import os, cv2, time, json
from generate_xml import write_xml
import numpy as np
from datetime import datetime
from pathlib import Path

configs_path = str( Path(os.getcwd()) / "config.txt" )
configs_json = json.load(open(configs_path, "r"))

# constants
image_folder = configs_json["image_folder"] #folder with images to load
savedir = configs_json["savedir"] #folder to save annotations
obj = configs_json["object"] #object class 
window_size = configs_json["window_size"] #the annotation tool window size
controls_dict = configs_json["controls_dict"] #controls for the annotation tool
autosave_time_cycle = configs_json["autosave_time_cycle"] #10 seconds


class ROI:
    def __init__(self, img, total_num_photos, controls):
        self.rects = []
        
        
        self.controls_dict = controls

        self.window_name = "ROI"
        self.bounding = False
        self.img = img
        self.frame = self.img.copy()
        self.overlay = self.img.copy()

        self.annotation_stage = 0 #0 for in-progress, 1 for confirm
        self.current_photo_id = 0
        self.total_num_photos = total_num_photos

    def resetFrame(self):
        self.frame = self.img.copy()
        self.overlay = self.img.copy()


    def getBBox(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            self.bounding = True
            self.rects.append([-1,-1,-1,-1])
            self.rects[-1][0] = x
            self.rects[-1][1] = y
            self.annotation_stage = 0

        elif self.bounding and event == cv2.EVENT_MOUSEMOVE:
            self.rects[-1][2] = x - self.rects[-1][0] #width
            self.rects[-1][3] = y - self.rects[-1][1] #height

        elif event == cv2.EVENT_LBUTTONUP:
            if(x == self.rects[-1][0] or y == self.rects[-1][1]):
                self.bounding = False
                self.rects.pop()
                return

            self.bounding = False

            self.rects[-1][2] = x - self.rects[-1][0] #width
            self.rects[-1][3] = y - self.rects[-1][1] #height

    def selectROI(self):

        cv2.setMouseCallback(self.window_name, self.getBBox)
        
        

    def displayFrame(self):
        

        pending_color = (0, 0, 255)
        confirm_color = (0, 255, 0)

        if (self.annotation_stage != 1):
            bbox_color = pending_color
        else:
            bbox_color = confirm_color

        for rect in self.rects:
            x,y,w,h = rect
            cv2.rectangle(self.frame, (x, y), (x+w, y+h), bbox_color, -1)
            cv2.addWeighted(self.overlay, 0.3, self.frame, 0.7, 0, self.frame)


        font = cv2.FONT_HERSHEY_SIMPLEX

        photo_progress_text = "{}/{}".format(self.current_photo_id, self.total_num_photos) #photoprogress
        cv2.putText(self.frame, photo_progress_text, (20,50), font, 2, (255,0,0), 2, cv2.LINE_AA)

        num_objects_bounded = "{}# objects bounded".format(len(self.rects)) #number of objects in annotation
        cv2.putText(self.frame, num_objects_bounded, (20,100), font, 2, (255,0,0), 2, cv2.LINE_AA)

        cv2.imshow(self.window_name, self.frame)

    def run(self, current_photo_id, annotations):
        
        self.current_photo_id = current_photo_id

        #annotations_json[current_photo_id] = { "object_list" : object_list, "tl_list" : tl_list, "br_list" : br_list } 
        if(annotations is not None):

            self.rects = []

            if("tl_list" in annotations.keys()):
                for i in range(len(annotations["tl_list"])):
                    x = annotations["tl_list"][i][0]
                    y = annotations["tl_list"][i][1]
                    w = annotations["br_list"][i][0] - x
                    h = annotations["br_list"][i][1] - y
                    self.rects.append([x,y,w,h])

        acceptable = False
        while not acceptable:
            #read frame from camera
            self.resetFrame()
            self.selectROI()
            self.displayFrame()

            key = (cv2.waitKey(1) & 0xFF)

            #press C to confirm
            if(key == ord(self.controls_dict["confirm"])) and len(self.rects) > 0:
                
                if(self.annotation_stage == 0):
                    #ask for confirmation
                    self.annotation_stage = 1

                elif(self.annotation_stage == 1):
                    #accept bounding box
                    acceptable = True
                    self.destructor()

            #press A to select the entire image
            elif(key == ord(self.controls_dict["select_all"])):
                #entire image
                w = self.frame.shape[1]
                h = self.frame.shape[0]
                self.rects = [[0,0,w,h]]

            #press P to pass the image ( do not make new annotation because the image sucks or you've already done it )
            elif(key == ord(self.controls_dict["next_image"])):
                #skip
                acceptable = True
                self.rects = []
                self.destructor()

            #press O to go to the previous image
            elif(key == ord(self.controls_dict["prev_image"])):
                return None

            #press S to deselect the last bounding box
            elif(key == ord(self.controls_dict["deselect"])):
                #cancel last bounding box
                if(len(self.rects)>0):
                    self.rects.pop()

            #press D to delete the annotation 
            elif(key == ord(self.controls_dict["delete"])):
                #return the delete signal
                return -1

        return self.rects

    def destructor(self):
        cv2.destroyWindow('ROI')

# global constants
img = None
tl_list = []
br_list = []
object_list = []

if __name__ == '__main__':

    #get the center window location 
    import tkinter as tk
    root = tk.Tk()
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    window_location = (int((screen_width - window_size[0])/2.0),int((screen_height - window_size[1])/2.0))


    annotations_json = {}
    current_photo_id = 0

    photos_path_list = [ img_path for n, img_path in list(enumerate(os.scandir(image_folder))) ]
    total_num_photos = len(photos_path_list)

    annotations_json_savepath = str( Path(os.getcwd()) / "annotations" / "annotations_json.txt" )
    autosave_timestamps = [time.time(), time.time()]

    if __name__ == '__main__':

        quit = False
        while not quit:

            if(current_photo_id >= total_num_photos):
                #save annotations
                confirmation = input("Done? y/n ") #confirmation
                if(confirmation.lower() == "y" or confirmation.lower() == "yes"):
                    json.dump(annotations_json, open(annotations_json_savepath, 'w'))

                    for key in annotations_json.keys():
                        object_list = annotations_json[key]["object_list"]
                        tl_list = annotations_json[key]["tl_list"]
                        br_list = annotations_json[key]["br_list"]
                        image_path = annotations_json[key]["image_path"]

                        write_xml(image_folder, image_path, object_list, tl_list, br_list, savedir)
                    quit = True
                    break
                else:
                    current_photo_id = total_num_photos - 1
                    continue

            elif(current_photo_id in annotations_json.keys()):
                current_photo_annotation = annotations_json[current_photo_id]
            
            else:
                current_photo_annotation = None


            autosave_timestamps[1] = time.time()
            if(autosave_timestamps[1] - autosave_timestamps[0] >= autosave_time_cycle):
                autosave_timestamps[0] = autosave_timestamps[1]
                json.dump(annotations_json, open(annotations_json_savepath, 'w'))
                print("Autosaved at {}".format(str(datetime.now())))

            #set up window
            cv2.namedWindow("ROI",cv2.WINDOW_NORMAL)
            cv2.moveWindow("ROI", window_location[0], window_location[1])

            #load photo
            image_file = photos_path_list[current_photo_id]
            img = image_file

            if not (image_file.path[-4:] in [".jpg",".png"]):
                continue  #if photo is not .jpg or .png file
            
            image = cv2.imread(image_file.path) #cv2 read in image
            image_size_y, image_size_x, _ = image.shape #get shape

            #get (x,y) resize for image
            if(image_size_x >= image_size_y):
                image_size_y *= float(window_size[0])/image_size_x
                image_size_x = window_size[0]
            else:
                image_size_x *= float(window_size[0])/image_size_y
                image_size_y = window_size[0]

            #resize photo
            cv2.resizeWindow("ROI", window_size[0],window_size[1])
            
            #display image
            cv2.imshow("ROI", image)

            #run annotation tool
            selector = ROI(image, total_num_photos, controls_dict)

            #this is a while loop that waits for a command
            boxes = selector.run(current_photo_id, current_photo_annotation) 

            """
            boxes returns
            --------------
                - list( bbox1, bbox2, ...)
                - empty list (to continue)
                - None (to go back)
                - (-1) (to delete annotation)
            """

            if(boxes is None):
                #go to a previous song
                if(current_photo_id > 0):
                    current_photo_id -= 1

            elif(isinstance(boxes, int)):
                if(boxes == -1):
                    #delete annotation and move onto the next photo
                    if(current_photo_id in annotations_json.keys()):
                        del annotations_json[current_photo_id]

                    if(current_photo_id < total_num_photos):
                        current_photo_id += 1
            
            else:
                if(len(boxes) > 0):

                    object_list = []
                    tl_list = []
                    br_list = []
                    
                    for box in boxes:
                        object_list.append(obj)
                        tl_list.append([box[0], box[1]])
                        br_list.append([box[0]+box[2], box[1]+box[3]])
                    
                    annotations_json[current_photo_id] = { "object_list" : object_list, "image_path" : img.path, "tl_list" : tl_list, "br_list" : br_list } 

                #go to the next song
                if(current_photo_id < total_num_photos):
                    current_photo_id += 1