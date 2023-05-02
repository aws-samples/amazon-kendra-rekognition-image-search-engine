import boto3
from botocore.exceptions import ClientError
import sys
import os
import logging
import csv
import json
import random
import string
import generate_manifest
from allowed_services import allowed_services

# ############# Global variables #############
S3_BUCKET = ""
REKOGNITION_PROJECT_NAME = ""
REGION = ""  # Set the AWS region
OUTPUT_DIR = "../image-output"
CSV_MANIFEST = "manifest.csv"
S3_PREFIX = "service-icons-blog"


rekognition = boto3.client("rekognition", region_name=REGION)
s3 = boto3.client("s3", region_name=REGION)


def create_custom_label_project():
    global REKOGNITION_PROJECT_NAME, S3_BUCKET
    charset = (
        string.digits + string.ascii_lowercase
    )  # Define the character set to choose from
    random_string = "".join(random.choices(charset, k=10))  # Generate the random string

    print("Creating Custom Label Project...")
    REKOGNITION_PROJECT_NAME = f"project-allie-service-detection-{random_string}"
    rekognition.create_project(ProjectName=REKOGNITION_PROJECT_NAME)
    print("Project Name: ", REKOGNITION_PROJECT_NAME)

    print("Creating Custom Label S3 Bucket...")
    S3_BUCKET = f"custom-labels-console-{REGION}-{random_string}"
    s3.create_bucket(
        Bucket=S3_BUCKET, CreateBucketConfiguration={"LocationConstraint": REGION}
    )
    print("Bucket Name: ", S3_BUCKET)


def upload_to_s3():
    print("Starting upload to S3...")
    count = 0
    for filename in os.listdir(OUTPUT_DIR):
        try:
            s3.upload_file(
                "{}/{}".format(OUTPUT_DIR, filename),
                S3_BUCKET,
                "{}/{}".format(S3_PREFIX, filename),
            )
            count += 1
            sys.stdout.write(
                "\rUploaded: {}/{}".format(count, len(os.listdir(OUTPUT_DIR)))
            )
            sys.stdout.flush()
        except ClientError as e:
            logging.error(e)


def create_csv(dataset):
    print("Creating manifest file...")
    with open(CSV_MANIFEST, "w", newline="") as file:
        writer = csv.writer(file)
        paginator = s3.get_paginator("list_objects_v2")
        pages = paginator.paginate(Bucket=S3_BUCKET, Prefix=S3_PREFIX)
        contents = []

        for page in pages:
            for obj in page["Contents"]:
                contents.append(obj)
        print("{} items".format(len(contents)))

        for obj in contents:
            if "canvas" in obj["Key"] and dataset == "TEST":
                label = extract_label(obj["Key"])
            elif dataset == "TRAINING" and "canvas" not in obj["Key"]:
                label = extract_label(obj["Key"])
            else:
                continue
            if label and label in allowed_services:  # swap if narrowing down services
                row = ["s3://{}/{}".format(S3_BUCKET, obj["Key"]), label]
                writer.writerow(row)


def extract_label(key):
    try:
        filename = key.split("/")[-1].split(".")[0]
        filename_list = filename.split("_")
        if filename_list[0] == "Arch":
            if (
                filename_list[1].split("-")[0] in ["Amazon", "AWS"]
                or filename_list[1] == "Elastic-Load-Balancing"
            ):
                return filename_list[1]
        elif filename_list[0] == "Res":
            return "{}-{}".format(filename_list[1], filename_list[2])
    except:
        print("{} has a different file name format".format(key))


def generate_manifest_file():
    generate_manifest.main(CSV_MANIFEST, REKOGNITION_PROJECT_NAME, "")


def upload_to_training():
    print("Uploading to rekognition...")

    describe_project_res = rekognition.describe_projects(
        ProjectNames=[REKOGNITION_PROJECT_NAME]
    )

    project = describe_project_res["ProjectDescriptions"][0]
    projectArn = project["ProjectArn"]
    try:
        old_dataset_arn = [
            x["DatasetArn"] for x in project["Datasets"] if x["DatasetType"] == "TRAIN"
        ][0]
        rekognition.delete_dataset(DatasetArn=old_dataset_arn)
    except:
        pass

    # dataset ARN required: aws rekognition describe-projects
    create_data_res = rekognition.create_dataset(
        DatasetType="TRAIN", ProjectArn=projectArn
    )

    dataset_arn = create_data_res["DatasetArn"]
    manifestfile = open("manifest.manifest").read()

    rekognition.update_dataset_entries(
        DatasetArn=dataset_arn, Changes={"GroundTruth": manifestfile}
    )

    describe_dataset_res = rekognition.describe_dataset(DatasetArn=dataset_arn)

    print("Dataset ARN: ", dataset_arn)
    print(
        "Dataset Status: ",
        json.dumps(describe_dataset_res, indent=4, sort_keys=True, default=str),
    )


def upload_to_test():
    print("Uploading to rekognition...")

    describe_project_res = rekognition.describe_projects(
        ProjectNames=[REKOGNITION_PROJECT_NAME]
    )

    project = describe_project_res["ProjectDescriptions"][0]
    projectArn = project["ProjectArn"]
    try:
        old_dataset_arn = [
            x["DatasetArn"] for x in project["Datasets"] if x["DatasetType"] == "TEST"
        ][0]
        rekognition.delete_dataset(DatasetArn=old_dataset_arn)
    except:
        pass

    # dataset ARN required: aws rekognition describe-projects
    create_data_res = rekognition.create_dataset(
        DatasetType="TEST", ProjectArn=projectArn
    )

    dataset_arn = create_data_res["DatasetArn"]
    manifestfile = open("manifest.manifest").read()

    rekognition.update_dataset_entries(
        DatasetArn=dataset_arn, Changes={"GroundTruth": manifestfile}
    )

    describe_dataset_res = rekognition.describe_dataset(DatasetArn=dataset_arn)

    print("Dataset ARN: ", dataset_arn)
    print(
        "Dataset Status: ",
        json.dumps(describe_dataset_res, indent=4, sort_keys=True, default=str),
    )


create_custom_label_project()
upload_to_s3()

create_csv("TRAINING")
generate_manifest_file()
upload_to_training()

create_csv("TEST")
generate_manifest_file()
upload_to_test()
