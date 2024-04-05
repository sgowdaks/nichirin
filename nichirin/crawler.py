from pyspark.sql import SparkSession, Row
from .retriever.solr_index_docs import SolrIndex
from bs4 import BeautifulSoup
from .utils.data_utils import validate_url

import requests
import json


# Create a Spark session
class Fetchndump:
    def __init__(self):
        self.spark = SparkSession.builder.appName("URLMapOperations").getOrCreate()
        self.si = SolrIndex(data_path=None, core="crawldb")
        self.depth = 5

    def solrfetch(self):
        solr_query = {"q": "status:UNFETCHED", "fl": "id,url,fetch_depth"}
        solr_core_url = "http://localhost:8983/solr/crawldb/select"
        response = requests.get(solr_core_url, params=solr_query)

        data = response.json()
        # depth = data["response"]["docs"]['fetch_depth']
        data = [
            (doc["url"], doc["id"], doc["fetch_depth"])
            for doc in data["response"]["docs"]
        ]
        return data

    def get_html_content(self, input):
        url, id, fd = input
        try:
            response = requests.get(url)
            response.raise_for_status()  # Raise an exception if the request fails
            soup = BeautifulSoup(response.text, "html.parser")

            for script in soup(["script", "style"]):
                script.extract()

            text = soup.body.get_text()

            new_urls = []

            anchor_tags = soup.find_all("a")
            for tag in anchor_tags:
                url = tag.get("href")
                if url:
                    new_urls.append(url)

            new_urls = validate_url(url, new_urls)
            return new_urls, text

        except requests.RequestException as e:
            print(f"Error fetching content from {url}: {e}")
            return None

    def addfields(self, urls, fetch_depth):
        json_objects = []
        for url in urls:
            data = {"url": url, "fetch_depth": fetch_depth + 1, "status": "UNFETCHED"}
            json_objects.append(data)
        # FIX ME URL
        self.si.index_docs("http://localhost:8983/solr/crawldb/", json_objects)

    def updatefields(self, df_batch):
        json_objects = []
        for json_string in df_batch.toJSON().collect():
            data = json.loads(json_string)

            if data["fetch_depth"] >= self.depth:
                data["status"] = {"set": "FETCHED"}
                continue

            text = data["text"]
            data["text"] = {"add": text}

            outlinks = data["outlinks"]

            # FIX ME
            self.addfields(outlinks, data["fetch_depth"])

            data["outlinks"] = {"add": outlinks}

            data["status"] = {"set": "FETCHED"}

            json_objects.append(data)
        return json_objects

    def spark_rdd(self, urls):
        rdd = self.spark.sparkContext.parallelize(urls)

        # Get HTML content for each URL
        mapped_rdd = rdd.map(lambda x: (x, self.get_html_content(x)))
        single_partition_rdd = mapped_rdd.repartition(1)

        # print(single_partition_rdd.take(5))  # Print the first 5 elements
        # rdd is converted back to dataframe
        df_mapped = single_partition_rdd.map(
            lambda x: Row(
                url=x[0][0], id=x[0][1], depth=x[0][2], outlinks=x[1][0], text=x[1][1]
            )
        ).toDF()

        self.si = SolrIndex(data_path=None, core="crawldb")
        total_rows = df_mapped.count()

        self.si.commit(solr_url=self.si.solr_url)
        df_mapped.show(truncate=False)

        # Loop through the DataFrame in batches of 1000 rows
        for offset in range(0, total_rows, self.si.batch_size):
            df_batch = df_mapped.limit(self.si.batch_size).offset(offset)
            stream = self.updatefields(df_batch)
            self.si.index_docs(solr_url=self.si.solr_url, stream=stream)
            self.si.commit(solr_url=self.si.solr_url)


ft = Fetchndump()

urls = ft.solrfetch()

while len(urls) > 0:
    ft.spark_rdd(urls)
    urls = ft.solrfetch()

ft.spark.stop()
