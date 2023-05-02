# Copyright 2021 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# PDX-License-Identifier: MIT-0 (For details, see https://github.com/awsdocs/amazon-rekognition-custom-labels-developer-guide/blob/master/LICENSE-SAMPLECODE.)

from datetime import datetime, timezone
import argparse
import logging
import csv
import os

"""
Purpose
Amazon Rekognition Custom Labels model example used in the service documentation:
Shows how to create an image-level (classification) manifest file from a CSV file. 
You can specify multiple image level labels per image.
CSV file format is
image,label,label,..
If necessary, use the bucket argument to specify the S3 bucket folder for the images.

"""

logger = logging.getLogger(__name__)


def check_duplicates(csv_file, deduplicated_file, duplicates_file):
    """
    Checks for duplicate images in a CSV file. If duplicate images
    are found, deduplicated_file is the deduplicated CSV file - only the first
    occurence of a duplicate is recorded. Other duplicates are recorded in duplicates_file.
    :param csv_file: The source CSV file
    :param deduplicated_file: The deduplicated CSV file to create. If no duplicates are found
    this file is removed.
    :param duplicates_file: The duplicate images CSV file to create. If no duplicates are found
    this file is removed.
    :return: True if duplicates are found, otherwise false.
    """

    logger.info(f"Deduplicating {csv_file}.")

    duplicates_found = False

    # Find duplicates
    with open(csv_file, "r") as f, open(deduplicated_file, "w") as dedup, open(
        duplicates_file, "w"
    ) as duplicates:
        reader = csv.reader(f, delimiter=",")
        dedup_writer = csv.writer(dedup)
        duplicates_writer = csv.writer(duplicates)

        entries = set()
        for row in reader:
            # Skip empty lines
            if row == []:
                continue

            key = row[0]
            if key not in entries:
                dedup_writer.writerow(row)
                entries.add(key)
            else:
                duplicates_writer.writerow(row)
                duplicates_found = True

    if duplicates_found:
        logger.info(f"Duplicates found check {duplicates_file}.")
    else:
        os.remove(duplicates_file)
        os.remove(deduplicated_file)

    return duplicates_found


def create_manifest_file(csv_file, manifest_file, s3_path, project_name):
    """
    Reads a CSV file and creates a Custom Labels classification manifest file
    :param csv_file: The source CSV file
    :param manifest_file: The name of the manifest file to create.
    :param s3_path: The S3 path to the folder that contains the images.
    """
    logger.info(f"Processing CSV file {csv_file}.")

    image_count = 0
    label_count = 0

    with open(csv_file, newline="") as csvfile, open(manifest_file, "w") as output_file:
        image_classifications = csv.reader(csvfile, delimiter=",", quotechar="|")

        # process each row (image) in CSV file
        for row in image_classifications:
            source_ref = str(s3_path) + row[0]
            image_json = '{"source-ref": "' + source_ref + '",'
            label_json = ""
            last_line = ""
            image_count += 1

            if "canvas" in row[0]:
                # process each image level label
                for index in range(1, len(row)):
                    image_level_label = row[index]

                    # Skip empty columns
                    if image_level_label == "":
                        continue
                    label_count += 1

                    label_json += (
                        '"'
                        + project_name
                        + '-train_BB":{"annotations":[{"left":688,"top":434,"width":130,"height":133,"class_id":0}],"image_size":[{"width":1502,"height":997,"depth":3}]},"'
                        + project_name
                        + '-train_BB-metadata":{"job-name":"labeling-job/'
                        + project_name
                        + '-train_BB","class-map":{"0":"'
                        + image_level_label
                        + '"},"human-annotated":"yes","objects":[{"confidence":1}],"creation-date":"'
                        + datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")
                        + '",'
                    )

                    # label_json += '"' + image_level_label + '": 1,'\
                    #     '"' + image_level_label + '-metadata":'\
                    #     '{"confidence": 1,'\
                    #     '"job-name": "labeling-job/' + image_level_label + '",'\
                    #     '"class-name": "' + image_level_label + '",'\
                    #     '"human-annotated": "yes",'\
                    #     '"creation-date": "' + datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%f')  + '",'

                    last_line = '"type": "groundtruth/object-detection"},'
                    if index == len(row) - 1:
                        last_line = '"type": "groundtruth/object-detection"}}'

                    label_json += last_line
            else:
                # process each image level label
                for index in range(1, len(row)):
                    image_level_label = row[index]

                    # Skip empty columns
                    if image_level_label == "":
                        continue
                    label_count += 1

                    label_json += (
                        '"' + image_level_label + '": 1,'
                        '"' + image_level_label + '-metadata":'
                        '{"confidence": 1,'
                        '"job-name": "labeling-job/' + image_level_label + '",'
                        '"class-name": "' + image_level_label + '",'
                        '"human-annotated": "yes",'
                        '"creation-date": "'
                        + datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")
                        + '",'
                    )

                    last_line = '"type": "groundtruth/image-classification"},'
                    if index == len(row) - 1:
                        last_line = '"type": "groundtruth/image-classification"}}'

                    label_json += last_line
            json_line = image_json + label_json + "\n"
            # write the image JSON Line
            output_file.write(json_line)

    output_file.close()
    logger.info(
        f"Finished creating manifest file {manifest_file}.\n"
        f"Images: {image_count}\nLabels: {label_count}"
    )
    return image_count, label_count


def add_arguments(parser):
    """
    Adds command line arguments to the parser.
    :param parser: The command line parser.
    """

    parser.add_argument("csv_file", help="The CSV file that you want to process.")

    parser.add_argument("project_name", help="The name of the Rekognition project")

    parser.add_argument(
        "--s3_path",
        help="The S3 bucket and folder path for the images."
        " If not supplied, column 1 is assumed to include the S3 path.",
        required=False,
    )


def main(csv_file, project_name, s3_path):
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    try:
        manifest_file = os.path.splitext(csv_file)[0] + ".manifest"
        duplicates_file = f"duplicates-{csv_file}"
        deduplicated_file = f"deduplicated-{csv_file}"

        # Create mainfest file if there are no duplicate images.
        if check_duplicates(csv_file, deduplicated_file, duplicates_file):
            print(
                f"Duplicates found. Use {duplicates_file} to view duplicates and then update {deduplicated_file}. "
            )
            print(
                f"{deduplicated_file} contains the first occurence of a duplicate. "
                "Update as necessary with the correct label information."
            )
            print(f"Re-run the script with {deduplicated_file}")
        else:
            print("No duplicates found. Creating manifest file")

            image_count, label_count = create_manifest_file(
                csv_file, manifest_file, s3_path, project_name
            )

            print(
                f"Finished creating manifest file: {manifest_file} \n"
                f"Images: {image_count}\nLabels: {label_count}"
            )

    except FileNotFoundError as err:
        logger.exception(f"File not found.:{err}")
        print(f"File not found: {err}. Check your input CSV file")

    except Exception as err:
        logger.exception(f"An error occured:{err}")
        print(f"An error occured:{err}")


if __name__ == "__main__":
    main()
