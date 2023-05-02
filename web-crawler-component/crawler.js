import axios from "axios";
import puppeteer from "puppeteer";
import {
  putItemDDB,
  identifyImageHighConfidence,
  getReferenceList,
} from "./utils.js";

/** Global variables */
const blogPostsApi = process.env.BLOG_POSTS_API;
const IMAGE_URL_PATTERN =
  "<pattern in the url that identified as link to image>";
const DDB_Table = process.env.DDB_Table;

// Function that retrieves URLs of records from a public API
function getURLs(blogPostsApi) {
  // Return a list of URLs
  return axios
    .get(blogPostsApi)
    .then((response) => {
      var data = response.data.items;
      console.log("RESPONSE:");
      const blogLists = data.map((blog) => [
        blog.item.additionalFields.link,
        blog.item.dateUpdated,
      ]);
      return blogLists;
    })
    .catch((error) => console.error(error));
}

// Function that crawls content of individual URLs
async function crawlFromUrl(urls) {
  const browser = await puppeteer.launch({
    executablePath: "/usr/bin/chromium-browser",
  });
  // const browser = await puppeteer.launch();

  const page = await browser.newPage();

  let numOfValidArchUrls = 0;

  for (let index = 0; index < urls.length; index++) {
    console.log("index: ", index);
    let blogURL = urls[index][0];
    let dateUpdated = urls[index][1];

    await page.goto(blogURL);
    console.log("blogUrl:", blogURL);
    console.log("date:", dateUpdated);

    // Identify and get image from post based on URL pattern
    const images = await page.evaluate(() =>
      Array.from(document.images, (e) => e.src)
    );
    const filter1 = images.filter((img) => img.includes(IMAGE_URL_PATTERN));
    console.log("all images:", filter1);

    // Validate if image is an architecture diagram
    for (let index_1 = 0; index_1 < filter1.length; index_1++) {
      const imageUrl = filter1[index_1];

      const rekog = await identifyImageHighConfidence(imageUrl);

      if (rekog) {
        if (rekog.labels.size >= 2) {
          console.log("Rekog.labels.size = ", rekog.labels.size);
          console.log("Selected image url  = ", imageUrl);

          let articleSection = [];
          let metadata = await page.$$('span[property="articleSection"]');

          for (let i = 0; i < metadata.length; i++) {
            const element = metadata[i];
            const value = await element.evaluate(
              (el) => el.textContent,
              element
            );
            console.log("value: ", value);
            articleSection.push(value);
          }

          const title = await page.title();
          const allRefLinks = await getReferenceList(
            rekog.labels,
            rekog.textServices
          );

          numOfValidArchUrls = numOfValidArchUrls + 1;

          putItemDDB(
            blogURL,
            dateUpdated,
            imageUrl,
            articleSection.toString(),
            rekog,
            { L: allRefLinks },
            title,
            DDB_Table
          );

          console.log("numOfValidArchUrls = ", numOfValidArchUrls);
        }
      }
      if (rekog && rekog.labels.size >= 2) {
        break;
      }
    }
  }
  console.log("valid arch : ", numOfValidArchUrls);
  await browser.close();
}

async function startCrawl() {
  // Get a list of URLs
  // Extract architecture image from those URLs
  const urls = await getURLs(blogPostsApi);

  if (urls) console.log("Crawling urls completed");
  else {
    console.log("Unable to crawl images");
    return;
  }
  await crawlFromUrl(urls);
}

startCrawl();
