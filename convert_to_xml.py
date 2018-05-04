import os, json
from pathlib import Path
from generate_xml import write_xml

configs_path = str( Path(os.getcwd()) / "config.txt" )
configs_json = json.load(open(configs_path, "r"))

# constants
image_folder = configs_json["image_folder"] #folder with images to load
savedir = configs_json["savedir"] #folder to save annotations


annotations_json = {}
annotations_json_savepath = str( Path(os.getcwd()) / "annotations" / "annotations_json.txt" )
annotations_json = json.load(open(annotations_json_savepath, 'r'))

for key in annotations_json.keys():
    object_list = annotations_json[key]["object_list"]
    tl_list = annotations_json[key]["tl_list"]
    br_list = annotations_json[key]["br_list"]
    image_path = annotations_json[key]["image_path"]

    write_xml(image_folder, image_path, object_list, tl_list, br_list, savedir)