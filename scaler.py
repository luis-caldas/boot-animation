#!/usr/bin/env nix-shell
#!nix-shell --pure -i python3 -p python39Packages.Wand
# -*- coding: utf-8 -*-

# normal imports
import os
import json
import time
import zipfile

from wand.api import library as WandLibrary
from wand.color import Color as WandColor
from wand.image import Image as WandImage

# project configurations
import config


def iprint(*strin, success=False) -> None:
    print("[ %s %s %s ]" % (
        "\033[93;1m" if not success else "\033[92;1m", "!" if not success else "✓", "\033[0m"
    ), *strin)


def main():

    iprint("Loading resolutions")

    # load needed resolutions to memory
    res = {}
    with open("resolutions.json", 'r') as file:
        res = json.load(file)["res"]

    # store the different types of top images
    top_imgs_ref = []

    iprint("Loading and resizing top part of images")

    # create the top image for each custom resolution
    for each in res:

        # the size of the top must the 1/3 of the smallest side
        top_size = int(min(each) / 3)

        # load the top image
        top_img = WandImage()
        with WandColor("transparent") as background_color:
            WandLibrary.MagickSetBackgroundColor(top_img.wand, background_color.resource)
        top_img.read(filename="assets/top.png")
        top_img.resize(top_size, top_size)

        # store the data
        top_imgs_ref.append(top_img)

    iprint("Counting and loading bottom part of images")

    # get the bottom parts
    bottom_imgs = sorted([name for name in os.listdir("assets") if "bottom" in name])
    bottom_imgs_ref = []

    # iterate the bottom images and load them into memory
    for each_img in bottom_imgs:
        bottom_imgs_ref.append(WandImage(filename=os.path.join("assets", each_img)))

    # files structurer
    images = []

    iprint("Assembling images")

    # assemble all the images
    for index, each_top in enumerate(top_imgs_ref):
        # images for a specific resolution
        specific_images = []
        for each_bottom in bottom_imgs_ref:
            # the new width should be the one of the bigger image
            new_width = max(each_top.width, each_bottom.width)
            # the new height should be the sum of all plus a responsive spacing
            new_height = int(each_top.height + (each_top.height / 2) + each_bottom.height)

            # create the new image with the new dimensions
            new_img = WandImage(width=new_width, height=new_height)

            # calculate the center offsets
            top_offset = int((new_width / 2) - (each_top.width / 2))
            bottom_offset = int((new_width / 2) - (each_bottom.width / 2))

            # add the images
            new_img.composite(image=each_top, left=top_offset, top=0)
            new_img.composite(image=each_bottom, left=bottom_offset, top=(new_height - each_bottom.height))

            # add the generated image to the list
            specific_images.append(new_img)

        # append it all to the images
        images.append([res[index], specific_images])

    iprint("Generating desc.txt files")

    # create the description files
    for each in images:
        string = "%s\n%s\n" % (
            "%d %d %d" % (
                each[1][0].width,
                each[1][0].height,
                config.REFRESH_RATE
            ),
            "%c %d %d %s" % ('p', 0, 0, config.FOLDER_NAME)
        )
        each.append(string)

    iprint("Creating output directories")

    # create the bootanimations
    for each in images:
        ref_path = os.path.join("dist", "%dx%d" % (each[0][0], each[0][1]))
        each.append(ref_path)
        os.makedirs(ref_path, exist_ok=True)

    iprint("Zipping files")

    # create the zip files
    for each in images:
        zip_now = zipfile.ZipFile(os.path.join(each[3], "bootanimation.zip"), 'w', compression=zipfile.ZIP_STORED)

        # add the description file
        zip_now.writestr("desc.txt", each[2])

        # iterate the images and write them to the zip
        for index, each_img in enumerate(each[1]):
            zip_now.writestr(os.path.join(config.FOLDER_NAME, "part%05d.png" % index), each_img.make_blob("png"))

        # close the zip
        zip_now.close()

    iprint("Done", success=True)


if __name__ == "__main__":
    main()
