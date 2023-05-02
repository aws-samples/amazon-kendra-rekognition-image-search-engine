# Web Crawler Component

This component shows code examples of how images can be crawled, provided as input to an Amazon Rekognition model to determine the content.

The context in the code is based upon crawling images from [AWS Blogs](https://aws.amazon.com/blogs/), hence it was written and structured based on the results generated from it.

## Build With

- JavaScript

## Prerequisites

The scripts need to be run on your local machine, with the list of prerequisites:

- [Create an AWS Account](https://portal.aws.amazon.com/gp/aws/developer/registration/index.html) if you do not already have one and log in. The IAM user that you use must have sufficient permissions to make necessary AWS service calls and manage AWS resources.
- [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html) installed and configured
- [Git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git) installed
- [Node.js](https://nodejs.org/en/download/) installed
- An Amazon Rekognition Custom Labels model created fronted by an API Gateway.
- An API that has the contents of the AWS blog posts that can be crawled from.
- An API that retrieves official documentations of individual services identified.
- [Amazon DynamoDB table](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/getting-started-step-1.html) created, following the structure of an item below:

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

1. Create a new directory, navigate to that directory in a terminal and clone the GitHub repository:

```
git clone <repo url>
```

2. Change directory to the web-crawler-component directory:

```
cd web-crawler-component
```

3. Install dependencies:

```
npm install
```

4. Run the script:

```
npm run start
```
