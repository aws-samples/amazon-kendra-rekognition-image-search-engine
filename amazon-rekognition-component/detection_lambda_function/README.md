# Detection Lambda Function

This section shows code examples of how an image is detected and contents identified using an Amazon Rekognition model trained with custom images.

The context in the code is based upon crawling images from [AWS Blogs](https://aws.amazon.com/blogs/), hence it was written and structured based on the results generated from it.

## Build With

- JavaScript

## Prerequisites

- [Create an AWS Account](https://portal.aws.amazon.com/gp/aws/developer/registration/index.html) if you do not already have one and log in. The IAM user that you use must have sufficient permissions to make necessary AWS service calls and manage AWS resources.
- [Git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git) installed
- [Lambda execution role](https://docs.aws.amazon.com/lambda/latest/dg/lambda-intro-execution-role.html) configured with permissions to AWS services used
- [API Gateway with HTTP custom integration](https://docs.aws.amazon.com/apigateway/latest/developerguide/api-gateway-create-api-step-by-step.html#api-gateway-create-resource-and-methods) created
- [Amazon Rekognition Custom Labels](https://docs.aws.amazon.com/rekognition/latest/customlabels-dg/getting-started.html) model created
- An API that retrieves official documentations of individual services identified

## How to run the script

1. [Create an AWS Lambda function](https://docs.aws.amazon.com/lambda/latest/dg/getting-started.html) in your AWS account
2. [Upload package.zip file](<https://docs.aws.amazon.com/lambda/latest/dg/gettingstarted-package.html#:~:text=East%20(UAE)%20Region.-,.zip%20file%20archives,-A%20.zip%20file>) into AWS Lambda
3. [Configure API Gateway as the event source](https://docs.aws.amazon.com/lambda/latest/dg/services-apigateway.html) of the function
4. [Send a POST request](https://docs.aws.amazon.com/apigateway/latest/developerguide/how-to-test-method.html) with a URL of an image, following the structure below:

```
{
    "body":{
      "url": <image url>
    }
}
```

## Testing

1. [Create a new test event](https://docs.aws.amazon.com/lambda/latest/dg/testing-functions.html) in the AWS Lambda function
2. Copy and paste the JSON content below as the template of the test event:

```
{
    "body":{
      "url": <image url>
    }
}
```

3. Run the function as a `Test`
