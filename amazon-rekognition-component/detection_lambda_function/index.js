const AWS = require("aws-sdk");
const axios = require("axios");

// API to retrieve information about individual services
const SERVICE_API = process.env.SERVICE_API;
// ARN of Amazon Rekognition model
const MODEL_ARN = process.env.MODEL_ARN;

const rekognition = new AWS.Rekognition();

exports.handler = async (event) => {
  const body = JSON.parse(event["body"]);
  let base64Binary = "";

  // Checks if the payload contains a url to the image or the image in base64
  if (body.url) {
    const base64Res = await new Promise((resolve) => {
      axios
        .get(body.url, {
          responseType: "arraybuffer",
        })
        .then((response) => {
          resolve(Buffer.from(response.data, "binary").toString("base64"));
        });
    });

    base64Binary = new Buffer.from(base64Res, "base64");
  } else if (body.byte) {
    const base64Cleaned = body.byte.split("base64,")[1];
    base64Binary = new Buffer.from(base64Cleaned, "base64");
  }

  // Pass the contents through the trained Custom Labels model and text detection
  const [labels, text] = await Promise.all([
    detectLabels(rekognition, base64Binary, MODEL_ARN),
    detectText(rekognition, base64Binary),
  ]);
  const texts = text.TextDetections.map((text) => ({
    DetectedText: text.DetectedText,
    ParentId: text.ParentId,
  }));

  // Compare between overlapping labels and retain the label with the highest confidence
  let filteredLabels = removeOverlappingLabels(labels);

  // Sort all the labels from most to least confident
  filteredLabels = sortByConfidence(filteredLabels);

  // Remove duplicate services in the list
  const services = retrieveUniqueServices(filteredLabels, texts);

  // Pass each service into the reference document API to retrieve the URL to the documentation
  const refLinks = await getReferenceLinks(services);

  var responseBody = {
    labels: filteredLabels,
    text: texts,
    ref_links: refLinks,
  };

  console.log("Response: ", response_body);

  const response = {
    statusCode: 200,
    headers: {
      "Access-Control-Allow-Origin": "*", // Required for CORS to work
    },
    body: JSON.stringify(responseBody),
  };
  return response;
};

const getReferenceLinks = async (services) => {
  var _ref_links = [];
  for (var i = 0; i < services.length; i += 5) {
    var result = await Promise.all(
      services.slice(i, i + 5).map((service) => {
        return getRef(service);
      })
    );
    _ref_links.push(...result);
  }

  // remove null
  _ref_links = _ref_links.filter((element) => {
    return element !== null;
  });

  var mapLinkToService = [];

  _ref_links.map((item) => {
    mapLinkToService[item.Link] = mapLinkToService[item.Link]
      ? mapLinkToService[item.Link] + ", " + item.Service
      : item.Service;
  });

  var ref_links = [];
  for (var key in mapLinkToService) {
    ref_links.push({
      Service: mapLinkToService[key],
      Link: key,
    });
  }
  return ref_links;
};

const retrieveUniqueServices = (filteredLabels, texts) => {
  var services = filteredLabels.map((label) => {
    return label.Name;
  });

  texts.map((text) => {
    var detected_text = text.DetectedText.toLowerCase();
    if (detected_text) {
      if (
        detected_text.includes("aws") ||
        detected_text.toLowerCase().includes("amazon")
      ) {
        detected_text = detected_text.replace("aws", "");
        detected_text = detected_text.replace("amazon", "");
        if (detected_text.trim() != "") {
          services.push(text.DetectedText.replaceAll(" ", "-"));
        }
      }
    }
  });
  var uSet = new Set(services);
  services = [...uSet];
  return services;
};

const removeOverlappingLabels = (labels) => {
  var filteredLabels = [];
  labels.CustomLabels.map((label) => {
    var left = label.Geometry.BoundingBox.Left;
    var top = label.Geometry.BoundingBox.Top;
    var width = label.Geometry.BoundingBox.Width;
    var height = label.Geometry.BoundingBox.Height;
    var pass = false;
    var i = filteredLabels.length;
    while (i > 0 && i--) {
      var item = filteredLabels[i];
      if (
        Math.abs(left - item.Geometry.BoundingBox.Left) <
          Math.max(width, item.Geometry.BoundingBox.Width) &&
        Math.abs(top - item.Geometry.BoundingBox.Top) <
          Math.max(height, item.Geometry.BoundingBox.Height)
      ) {
        if (item.Confidence > label.Confidence) {
          pass = true;
        } else {
          filteredLabels.splice(i, 1);
          break;
        }
      }
    }
    if (!pass) {
      filteredLabels.push({ ...label });
    }
  });
  return filteredLabels;
};

const detectLabels = async (rekognition, base64, model_arn) => {
  return new Promise((resolve, reject) => {
    rekognition.detectCustomLabels(
      {
        Image: { Bytes: base64 },
        ProjectVersionArn: model_arn,
        MinConfidence: 15,
      },
      function (err, data) {
        if (err) reject(err); // an error occurred
        else resolve(data); // successful response
      }
    );
  });
};

const detectText = async (rekognition, base64) => {
  return new Promise((resolve, reject) => {
    rekognition.detectText(
      {
        Image: { Bytes: base64 },
      },
      function (err, data) {
        if (err) reject(err); // an error occurred
        else resolve(data); // successful response
      }
    );
  });
};

const getRef = async (servicename) => {
  return new Promise((resolve, reject) => {
    // console.log("Service Name: ", servicename)

    var _servicename = servicename.toLowerCase();
    _servicename = _servicename.replace("aws", "");
    _servicename = _servicename.replace("amazon", "");

    axios
      .post(SERVICE_API, {
        QueryText: _servicename,
        PageNumber: 1,
        PageSize: 10,
        Locale: "en_us",
        Previous: "",
      })
      .then((response) => {
        if (response.data.ResultItems[0]) {
          resolve({
            Service: servicename,
            Link: response.data.ResultItems[0]["DocumentURI"],
          });
        } else {
          resolve(null);
        }
      });
  });
};

const sortByConfidence = (list) => {
  return list.sort((a, b) => b.Confidence - a.Confidence);
};
