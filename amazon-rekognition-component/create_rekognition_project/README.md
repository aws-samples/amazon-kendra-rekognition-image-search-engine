<!-- # Create datasets, label images and generate manifest -->

# Create Rekognition Custom Labels Project

This section shows code examples of how an Amazon Rekognition model can be trained using custom images.

The context in the code is based upon crawling images from [AWS Blogs](https://aws.amazon.com/blogs/), hence it was written and structured based on the results generated from it.

## About project

### Labelling process

In order to train for all 200+ service icons, we have to think of a more scalable solution to label each image for both training and testing. Essentially, AWS Rekognition needs to be able to identify various services icons in a canvas of multiple icons. As such, we used to following approaches for training and testing images.

For training images, we used the AWS provided Asset Package to retrieve all the service icons. In the folder, there are several sizes for one icon (e.g. 16, 32, 48, 64, 5x64). For each image we applied the following modifications:

1. added the image on a white background
2. cropped the margins of the image
   As such, image icon will have at most 15 images. The manifest file would indicate the link to the images in S3 and label each image based on the file name.

For testing images, we created 10 canvases of randomly selected icons. Again, since we are training Rekognition to identify services icons in a canvas of icons, this would be a more scalable approach to ensuring every service icons is trained for. In comparison to manually labeling each service icons in an architecture diagram, the latter approach takes more time and may not account for more obscure services. For each service icon, we inserted it into each of the 10 canvases (200 service icons will create 2000 test data). Similar to the training data, the service icon at the center matches the name of the file where we indicate in the manifest. To create the bounding box, we hardcoded the values to draw a bounding on over the service icon in the middle which will indicate to Rekognition the service icon to train for.

For more information on creating manifest files, you may refer to this [link](https://docs.aws.amazon.com/rekognition/latest/customlabels-dg/md-create-manifest-file.html)

Ideally, a more accurate approach would be to train with actual architecture diagrams as words and arrows on the image may affect how Rekognition is trained. If time and budget is of lesser concern, SageMaker Ground Truth may be an option for labelling hundreds of images. You may learn more about SageMaker Ground Truth [here](https://aws.amazon.com/sagemaker/data-labeling/?sagemaker-data-wrangler-whats-new.sort-by=item.additionalFields.postDateTime&sagemaker-data-wrangler-whats-new.sort-order=desc).

## Prerequisites

The scripts need to be run on your local machine, with the list of prerequisites:

- [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html) installed and configured
- [Git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git) installed
- [Node.js](https://nodejs.org/en/download/) installed
- [Python](https://www.python.org/downloads/) installed

## How to run the script

1. Create a new directory, navigate to that directory in a terminal and clone the GitHub repository:

```
git clone <repo url>
```

2. Change directory to the create-rekognition-component/create_rekognition_project directory:

```
cd create-rekognition-component/create_rekognition_project
```

3. Run the script:

```
python3 create_datasets.py
```
