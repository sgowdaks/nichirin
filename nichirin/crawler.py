from pyspark.sql import SparkSession, Row
from .retriever.solr_index_docs import SolrIndex
from bs4 import BeautifulSoup
from utils.data_utils import validate_url

import requests
import json

# Create a Spark session
spark = SparkSession.builder.appName("URLMapOperations").getOrCreate()

solr_query = { "q":"status:UNFETCHED","fl": "id,url"}
solr_core_url = "http://localhost:8983/solr/crawldb/select"
response = requests.get(solr_core_url, params=solr_query)

data = response.json()
urls = [(doc["url"], doc['id']) for doc in data["response"]["docs"]]

#converts data to RDD by connceting to spark sessions
rdd = spark.sparkContext.parallelize(urls)

def get_html_content(input):
    url, id = input
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
                
        return new_urls, text
    
    except requests.RequestException as e:
        print(f"Error fetching content from {url}: {e}")
        return None 

# Get HTML content for each URL
mapped_rdd = rdd.map(lambda x: (x, get_html_content(x)))
single_partition_rdd = mapped_rdd.repartition(1)

#print(single_partition_rdd.take(5))  # Print the first 5 elements
#rdd is converted back to dataframe 
df_mapped = single_partition_rdd.map(lambda x: Row(url=x[0][0], id=x[0][1], outlinks=x[1][0], text=x[1][1])).toDF()


si = SolrIndex(data_path=None, core="crawldb")

total_rows = df_mapped.count()

def addfields(df_batch):
    json_objects = []
    for json_string in df_batch.toJSON().collect():
        data = json.loads(json_string)
        
        text = data['text']
        data['text'] = {"add":text}
        
        outlinks = data['outlinks']
        outlinks = validate_url(data['url'], outlinks)
        data['outlinks'] = {"add":outlinks}

        data['status'] = {"set":"FETCHED"}

        json_objects.append(data)
    return json_objects

# Loop through the DataFrame in batches of 1000 rows
for offset in range(0, total_rows, si.batch_size):
    df_batch = df_mapped.limit(si.batch_size).offset(offset)
    stream = addfields(df_batch)
    si.index_docs(solr_url=si.solr_url, stream=stream)
    si.commit(solr_url=si.solr_url)

si.commit(solr_url=si.solr_url)

df_mapped.show(truncate=False)

spark.stop()
    