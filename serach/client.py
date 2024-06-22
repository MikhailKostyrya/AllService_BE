from elasticsearch import Elasticsearch, Transport

class ElasticClient:
    def __init__(self):
        self.url = "158.160.91.177:9200"
        self._client = Elasticsearch(hosts=self.url, transport_class=Transport)
        self.index = "allservice"

    def search(self, query):
        request = {
            "query": {
                "multi_match": {
                    "query": query,
                    "fields": ['name', 'content', 'address', 'executor.content', 'category.category_name'],
                    "fuzziness": "auto"
                }
            }
        }

        response = self._client.search(index=self.index, body=request)
        return [val['_source']['id'] for val in response['hits']['hits']]

    def bulk(self, dict_to_send):
        self._client.bulk(index=self.index, body=dict_to_send)

    def indices(self):
        return self._client.indices
