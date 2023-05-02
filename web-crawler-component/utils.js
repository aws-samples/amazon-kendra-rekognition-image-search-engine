import axios from "axios";
import AWS from "aws-sdk";

// Configuration
AWS.config.update({ region: process.env.REGION });

/** Global variables */
// API to identify images
const LABEL_API = process.env.LABEL_API;
// API to get relevant documentations of individual services
const DOCUMENTATION_API = process.env.DOCUMENTATION_API;
// Create the DynamoDB service object
const dynamoDB = new AWS.DynamoDB({ apiVersion: "2012-08-10" });

// Function to identify image using an API that calls Amazon Rekognition model
function identifyImageHighConfidence(image_url) {
  return axios
    .post(LABEL_API, {
      url: image_url,
    })
    .then((res) => {
      let data = res.data;
      let rekogLabels = new Set();
      let rekogTextServices = new Set();
      let rekogTextMetadata = new Set();

      data.labels.forEach((element) => {
        if (element.Confidence >= 40) rekogLabels.add(element.Name);
      });

      data.text.forEach((element) => {
        if (
          element.DetectedText.includes("AWS") ||
          element.DetectedText.includes("Amazon")
        ) {
          rekogTextServices.add(element.DetectedText);
        } else {
          rekogTextMetadata.add(element.DetectedText);
        }
      });
      rekogTextServices.delete("AWS");
      rekogTextServices.delete("Amazon");
      return {
        labels: rekogLabels,
        textServices: rekogTextServices,
        textMetadata: Array.from(rekogTextMetadata).join(", "),
      };
    })
    .catch((error) => console.error(error));
}

// Function that PUTS item into Amazon DynamoDB table
function putItemDDB(
  originUrl,
  publishDate,
  imageUrl,
  crawlerData,
  rekogData,
  referenceLinks,
  title,
  tableName
) {
  console.log("WRITE TO DDB");
  console.log("originUrl :   ", originUrl);
  console.log("publishDate:  ", publishDate);
  console.log("imageUrl: ", imageUrl);
  let write_params = {
    TableName: tableName,
    Item: {
      OriginURL: { S: originUrl },
      PublishDate: { S: formatDate(publishDate) },
      ArchitectureURL: {
        S: imageUrl,
      },
      Metadata: {
        M: {
          crawler: {
            S: crawlerData,
          },
          Rekognition: {
            M: {
              labels: {
                S: Array.from(rekogData.labels).join(", "),
              },
              textServices: {
                S: Array.from(rekogData.textServices).join(", "),
              },
              textMetadata: {
                S: rekogData.textMetadata,
              },
            },
          },
        },
      },
      Reference: referenceLinks,
      Title: {
        S: title,
      },
    },
  };

  dynamoDB.putItem(write_params, function (err, data) {
    if (err) {
      console.log("*** DDB Error", err);
    } else {
      console.log("Successfuly inserted in DDB", data);
    }
  });
}

// Function that formats date
function formatDate(date) {
  return date.replace("+0000", "+00:00");
}

// Function that gets reference links of individual services
function getReferenceLink(serviceName) {
  serviceName = serviceName.toLowerCase();
  serviceName = serviceName.replace("aws", "");
  serviceName = serviceName.replace("amazon", "");
  serviceName = serviceName.replace("-", " ");

  console.log("QueryText : ", serviceName);
  return axios
    .post(DOCUMENTATION_API, {
      QueryText: serviceName,
      PageNumber: 1,
      PageSize: 10,
      Locale: "en_us",
      Previous: "",
    })
    .then(function (response) {
      if (
        response != undefined &&
        response.data != undefined &&
        response.data.ResultItems[0] != undefined &&
        response.data.ResultItems[0].DocumentURI != undefined
      ) {
        let referenceLink = response.data.ResultItems[0].DocumentURI;
        return referenceLink;
      } else return "not found";
    })
    .catch(function (error) {
      console.log(error);
    });
}

async function getReferenceList(listService1, listService2) {
  listService1 = Array.from(listService1);
  listService2 = Array.from(listService2);

  let allReferenceLinks = new Set();
  let serviceLinkList = [];
  console.log("list service 1 :\n", listService1);
  for (let index = 0; index < listService1.length; index++) {
    let serviceName1 = listService1[index];
    console.log("serviceName1 : ", serviceName1);
    serviceName1 = serviceName1.trim();

    if (serviceName1 == "") continue;
    let referenceLink1 = await getReferenceLink(serviceName1);

    if (!allReferenceLinks.has(referenceLink1)) {
      serviceLinkList.push({
        M: {
          service: {
            S: serviceName1,
          },
          link: {
            S: referenceLink1,
          },
        },
      });

      allReferenceLinks.add(referenceLink1);
    }
  }

  console.log("list service 2 :\n", listService2);
  for (let index = 0; index < listService2.length; index++) {
    let serviceName2 = listService2[index];
    let referenceLink2 = await getReferenceLink(serviceName2);
    if (!allReferenceLinks.has(referenceLink2)) {
      serviceLinkList.push({
        M: {
          service: {
            S: serviceName2,
          },
          link: {
            S: referenceLink2,
          },
        },
      });
      allReferenceLinks.add(referenceLink2);
    }
  }
  return serviceLinkList;
}

export { putItemDDB, identifyImageHighConfidence, getReferenceList };
