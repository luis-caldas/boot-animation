#!/usr/bin/env nix-shell
#!nix-shell --pure -i python3 -p python3Packages.Wand

# Normal imports
import os
import json
import time
import zipfile

from wand.api import library as WandLibrary
from wand.color import Color as WandColor
from wand.image import Image as WandImage

# Project Configuration
import config


def iprint(*strin, success=False) -> None:
    print("[ %s %s %s ]" % (
        "\033[93;1m" if not success else "\033[92;1m",
        "!" if not success else "✓", "\033[0m"
    ), *strin)


def main():

    iprint("Loading resolutions")

    # Get our path
    local_path = os.path.dirname(__file__)

    # Join the path of the main assets
    default_assets_path = os.path.join(
        local_path, "assets", "themes", config.DEFAULT_THEME
    )

    # Store the different types of top images
    top_imgs_ref = {}

    iprint("Loading and resizing top part of images")

    # Create the top image for each custom resolution
    for name, resolutions in config.RESOLUTIONS.items():

        # The size of the top must the 1/3 of the smallest side
        top_size = int(min(resolutions) / 3)

        # Load the top image
        top_img = WandImage()
        with WandColor("transparent") as background_color:
            WandLibrary.MagickSetBackgroundColor(
                top_img.wand, background_color.resource
            )
        top_img.read(filename=os.path.join(default_assets_path, "top.png"))
        # Needs to be a square
        top_img.resize(top_size, top_size)

        # Store the data
        top_imgs_ref[name] = top_img

    iprint("Counting and loading bottom part of images")

    # Get the bottom parts
    bottom_imgs = sorted([name for name in os.listdir(default_assets_path) if "bottom" in name])
    bottom_imgs_ref = []

    # Iterate the bottom images and load them into memory
    for each_img in bottom_imgs:
        bottom_imgs_ref.append(WandImage(filename=os.path.join(default_assets_path, each_img)))

    # Files structurer
    images = {}

    iprint("Assembling images")

    # Assemble all the images
    for name, each_top in top_imgs_ref.items():
        # Images for a specific resolution
        specific_images = []
        for each_bottom in bottom_imgs_ref:
            # The new width should be the one of the bigger image
            new_width = max(each_top.width, each_bottom.width)
            # The new height should be the sum of all plus a responsive spacing
            new_height = int(each_top.height + (each_top.height / 2) + each_bottom.height)

            # Create the new image with the new dimensions
            new_img = WandImage(width=new_width, height=new_height)

            # Calculate the center offsets
            top_offset = int((new_width / 2) - (each_top.width / 2))
            bottom_offset = int((new_width / 2) - (each_bottom.width / 2))

            # Add the images
            new_img.composite(image=each_top, left=top_offset, top=0)
            new_img.composite(image=each_bottom, left=bottom_offset, top=(new_height - each_bottom.height))

            # Add the generated image to the list
            specific_images.append(new_img)

        # Append it all to the images
        images[name] = {
            "resolutions": config.RESOLUTIONS[name],
            "list": specific_images
        }

    iprint(f"Generating {config.DESCRIPTION_FILE} files")

    # Create the description files
    for name, each in images.items():
        string = "%s\n%s\n" % (
            "%d %d %d" % (
                each["list"][0].width,
                each["list"][0].height,
                config.REFRESH_RATE
            ),
            "%c %d %d %s" % ('p', 0, 0, config.FOLDER_NAME)
        )
        each["description"] = string

    iprint("Creating output directories")

    # Create the bootanimations
    for name, each in images.items():
        ref_path = os.path.join(config.DISTRIBUTE, config.ANDROID_FOLDER, name)
        each["path"] = ref_path
        os.makedirs(ref_path, exist_ok=True)

    iprint("Zipping files")

    # Create the zip files
    for name, each in images.items():
        zip_now = zipfile.ZipFile(
            os.path.join(each["path"], config.OUTPUT_NAME), 'w',
            compression=zipfile.ZIP_STORED
        )

        # Add the description file
        zip_now.writestr(config.DESCRIPTION_FILE, each["description"])

        # Iterate the images and write them to the zip
        for index, each_img in enumerate(each["list"]):
            zip_now.writestr(
                os.path.join(config.FOLDER_NAME, "part%05d.png" % index),
                each_img.make_blob("png")
            )

        # Close the zip
        zip_now.close()

    iprint("Done", success=True)


if __name__ == "__main__":
    main()
