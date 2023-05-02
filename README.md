## Build an Image Search Engine with Amazon Kendra and Amazon Rekognition

This repository contains scripts and code samples referenced by a blog post that talks about how an image search engine can be build using Amazon Kendra and Amazon Rekogition.

In particular, the example codes shown relates to the process of crawling images online, training a custom image recognition model and identifying images using the model. The identified images and its contents are indexed and made searchable intelligently through the use of natural language.

There are three directories in this repository:

1. amazon-rekognition-component
   - This component shows code examples of how datasets of custom images are created and labelled to be used to train a custom image recognition model.
2. web-crawler-component
   - This component shows code examples of how images can be crawled and its content stored in a database.
3. amazon-kendra-component
   - This component shows code examples of how contents of individual images crawled, can be structured as documents and indexed, ready to be searched.

Disclaimer: The context in the code is based upon crawling images from [AWS Blogs](https://aws.amazon.com/blogs/), hence it was written and structured based on the results generated from it.

## Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

## License

This library is licensed under the MIT-0 License. See the LICENSE file.
