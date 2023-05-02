# Amazon Kendra Component

This component shows code examples of how items in an Amazon DynamoDB table can be indexed in Amazon Kendra.

The context in the code is based upon crawling images from [AWS Blogs](https://aws.amazon.com/blogs/), hence it was written and structured based on the results generated from it.

## Build With

- Python

## Prerequisites

- [Create an AWS Account](https://portal.aws.amazon.com/gp/aws/developer/registration/index.html) if you do not already have one and log in. The IAM user that you use must have sufficient permissions to make necessary AWS service calls and manage AWS resources.
- [Git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git) installed
- [Lambda execution role](https://docs.aws.amazon.com/lambda/latest/dg/lambda-intro-execution-role.html) configured with permissions to AWS services used
- [Amazon Kendra index](https://docs.aws.amazon.com/kendra/latest/dg/create-index.html) created
- [Amazon DynamoDB table](https://docs.aws.amazon.com/lambda/latest/dg/with-ddb-example.html#:~:text=outputfile.txt%20file.-,Create%20a%20DynamoDB%20table%20with%20a%20stream%20enabled,-Create%20an%20Amazon) created with a stream enabled, following the structure of an item below:

```
{
   "Item":{
      "OriginURL":{
         "S":"<source url in string>"
      },
      "PublishDate":{
         "S":"<date in string>"
      },
      "ArchitectureURL":{
         "S":"<image url in string>"
      },
      "Metadata":{
         "M":{
            "crawler":{
               "S":"<crawler data in string>"
            },
            "Rekognition":{
               "M":{
                  "labels":{
                     "S":"<identified labels in string>"
                  },
                  "textServices":{
                     "S":"<identified services in string>"
                  },
                  "textMetadata":{
                     "S":"<other metadata in string>"
                  }
               }
            }
         }
      },
      "Reference":{
         "L":"<reference links in list>"
      },
      "Title":{
         "S":"<source title in string>"
      }
   }
}
```

## How to run the script

1. [Create an AWS Lambda function](https://docs.aws.amazon.com/lambda/latest/dg/getting-started.html) in your AWS account
2. [Configure a stream as the event source](https://docs.aws.amazon.com/lambda/latest/dg/with-ddb.html#:~:text=%E2%80%93%20sns%3APublish-,Configuring%20a%20stream%20as%20an%20event%20source,-Create%20an%20event) of the function
3. [Insert an item](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/getting-started-step-2.html) into the Amazon DynamoDB table

## Testing

1. [Create a new test event](https://docs.aws.amazon.com/lambda/latest/dg/testing-functions.html) in the AWS Lambda function
2. Copy and paste the JSON content in `example-event.json` as the template of the test event
3. Run the function as a `Test`
