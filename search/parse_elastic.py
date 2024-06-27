from os import environ
import django
from django.forms import model_to_dict
from elasticsearch.exceptions import NotFoundError

environ.setdefault('DJANGO_SETTINGS_MODULE', 'AllService_BE.settings')
django.setup()

from catalog.models import Service, ExecutorData
from .client import ElasticClient

class ElasticParser:
    def __init__(self):
        self.json_services = []
        self.client = ElasticClient()

    def fill_elastic(self):
        self.delete_index()
        self.create_index()
        self.parse_services()

    def delete_index(self):
        try:
            self.client.indices().delete(index=self.client.index)
        except NotFoundError as ignore:
            pass

    def create_index(self):
        self.client.indices().create(index=self.client.index)

    def parse_services(self):
        services = Service.objects.select_related('executor').all()
        for service in services:
            service_dict = model_to_dict(service, fields=[field.name for field in service._meta.fields if field.name != 'executor'])
            executor_dict = model_to_dict(service.executor, fields=[field.name for field in ExecutorData._meta.fields])
            service_dict['executor'] = executor_dict
            self.json_services.append({"index": {"_index": self.client.index, "_id": service.id}})
            self.json_services.append(service_dict)
        self.client.bulk(self.json_services)

ElasticParser().fill_elastic()
