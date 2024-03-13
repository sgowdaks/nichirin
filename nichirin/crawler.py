from pyspark.sql import SparkSession

import requests

# Create a Spark session
spark = SparkSession.builder.appName("URLMapOperations").getOrCreate()

solr_query = { "q": "*:*","fl": "url"}
solr_core_url = "http://localhost:8983/solr/crawldb/select"
response = requests.get(solr_core_url, params=solr_query)

data = response.json()
urls = [doc["url"][0] for doc in data["response"]["docs"]]

#converts data to RDD by connceting to spark sessions
rdd = spark.sparkContext.parallelize(urls)

def get_html_content(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception if the request fails
        return response.text
    except requests.RequestException as e:
        print(f"Error fetching content from {url}: {e}")
        return None 

# Get HTML content for each URL
mapped_rdd = rdd.map(lambda x: (x, get_html_content(x)))

#rdd is converted back to dataframe 
df_mapped = mapped_rdd.toDF(['url', 'html_content'])

df_mapped.show(truncate=False)

spark.stop()
    