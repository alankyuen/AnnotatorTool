installation
-------------
pip install numpy pathlib opencv-python lxml flickrapi



how to use
------------

[I] download images
	python flickrapi_test.py
        
    [1] set up queries = ["pen", "book"] to save 500 images of each

[II] set up "config.txt"
    
    [1] "object" : the object class you want to annotate
    [2] "image_folder" : the image folder path that contains all the objects in the same object class that you want to annotate
    [3] "window_size" : the size of the window of the annotation tool
    [4] "controls_dict" : the controls for the annotation tool
    [5] "savedir" : the folder path to save annotations
    [6] "autosave_time_cycle" : the time cycle it takes to autosave (default is 10 seconds)

[III] annotate images
	python annotate_tool.py
    --> input "yes" or "y" into terminal once you've reached the end.
    --> you do not have to reach the end, you can wait for an autosave and then skip to [IV]

    Default controls (you can change this in the controls_dict in config.txt)
    ———————————————————————————
    C - Confirm picture 
        (save annotation)
    A - Select Entire Image 
        (easy select, if the whole picture is 1 object)
    P - Next Image
        (does not save any annotation)
    O - Previous Image
        (does not delete any annotations)
    S - Deselect Last Bounding Box
        (when you mess up on a bounding box)
    D - Delete current image annotation
        (when you don't want annotations for the particular image -- like a faulty image)

[IV] If you were not able to reach the end of the photos in annotation and get all the XML files, run convert_to_XML.py on the autosaved data.