"""Upload all floorplan SVG files to S3"""

import os
from s3_utils import upload_generic_file

# Path to local floorplan_svg folder
LOCAL_SVG_FOLDER = "floorplan_svg"
# S3 destination path
S3_DESTINATION = "floorplan_svg"


def upload_all_svg_files():
    """Upload all SVG files from floorplan_svg folder to S3, preserving folder structure"""
    success_count = 0
    fail_count = 0

    # Iterate through building folders
    for building in os.listdir(LOCAL_SVG_FOLDER):
        building_path = os.path.join(LOCAL_SVG_FOLDER, building)

        # Skip if not a directory
        if not os.path.isdir(building_path):
            continue

        # Iterate through SVG files in building folder
        for filename in os.listdir(building_path):
            if not filename.endswith(".svg"):
                continue

            local_file_path = os.path.join(building_path, filename)
            s3_object_name = f"{S3_DESTINATION}/{building}/{filename}"

            success = upload_generic_file(
                local_file_path, s3_object_name, file_type="svg+xml"
            )

            if success:
                success_count += 1
            else:
                fail_count += 1

    print(f"\nUpload complete: {success_count} succeeded, {fail_count} failed")


if __name__ == "__main__":
    upload_all_svg_files()
