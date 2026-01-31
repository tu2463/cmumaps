"""Download all floorplan SVG files from S3 to verify uploads"""

import os
from s3_utils import client, bucket_name

# S3 source path
S3_SOURCE = "floorplan_svg/"
# Local destination folder
LOCAL_DESTINATION = "floorplan_svg_downloaded"


def download_all_svg_files():
    """Download all SVG files from S3 floorplan_svg folder"""
    success_count = 0
    fail_count = 0

    # Create local destination folder if it doesn't exist
    os.makedirs(LOCAL_DESTINATION, exist_ok=True)

    # List all objects in the floorplan_svg folder
    objects = client.list_objects(bucket_name, prefix=S3_SOURCE, recursive=True)

    for obj in objects:
        # Skip if not an SVG file
        if not obj.object_name.endswith(".svg"):
            continue

        # Extract relative path (e.g., "floorplan_svg/building/floor.svg" -> "building/floor.svg")
        relative_path = obj.object_name[len(S3_SOURCE):]
        local_file_path = os.path.join(LOCAL_DESTINATION, relative_path)

        # Create building subfolder if needed
        os.makedirs(os.path.dirname(local_file_path), exist_ok=True)

        try:
            client.fget_object(bucket_name, obj.object_name, local_file_path)
            print(f"Downloaded: {obj.object_name}")
            success_count += 1
        except Exception as e:
            print(f"Failed to download {obj.object_name}: {e}")
            fail_count += 1

    print(f"\nDownload complete: {success_count} succeeded, {fail_count} failed")
    print(f"Files saved to: {LOCAL_DESTINATION}/")


if __name__ == "__main__":
    download_all_svg_files()
