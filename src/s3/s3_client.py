from datetime import datetime
from io import BytesIO
import json
import re
from botocore.response import StreamingBody
from botocore.config import Config
from util.aws_account_api import BotoSessionAwsAccount
from typing import List
from attrs import define

@define(auto_attribs=True)
class DateRange:
    start: datetime|None
    end: datetime|None

def to_dict_value(o):
    if isinstance(o, datetime):
        return o.isoformat()
    return o.__dict__

class S3Bucket:
    def __init__(self, name:str, region: str, created: datetime):
        self.name = name
        self.region = region
        self.created = created

    def to_url(self, bucket_url_template: str) -> str:
        return bucket_url_template.replace('{region}', self.region).replace('{name}', self.name)

    def to_json(self) -> str:
        return json.dumps(self, default=to_dict_value, sort_keys=True, indent=4)
    
    @staticmethod
    def from_dict(dict_o: dict) -> "S3Bucket":
        return S3Bucket(name=dict_o['name'], region=dict_o['region'], created=datetime.fromisoformat(dict_o['created']))

    @staticmethod
    def from_json(json_str: str) -> "S3Bucket":
        return S3Bucket.from_dict(json.loads(json_str))
    
    @staticmethod
    def is_valid_url_template(bucket_url_template: str) -> bool:
        return '{region}' in bucket_url_template and '{name}' in bucket_url_template

    @staticmethod
    def default_bucket_url_template() -> str:
        return "http://s3.{region}.amazonaws.com/{name}"
    
    @staticmethod
    def bucket_url_template_help() -> str:
        return "A string containing {region} and {name} to be replace by bucket region and name. ie. " + S3Bucket.default_bucket_url_template()



class S3Object:
    def __init__(self, bucket: S3Bucket, full_path: List[str], modified: datetime):
        self.bucket = bucket
        self.full_path = full_path
        self.modified = modified

    
    def to_url(self, bucket_url_template: str) -> str:
        return f"{self.bucket.to_url(bucket_url_template)}/{'/'.join(self.full_path)}"

    def to_json(self) -> str:
        return json.dumps(self, default=to_dict_value, sort_keys=True, indent=4)

    @staticmethod
    def from_dict(dict_o: dict) -> "S3Object":
        return S3Object(bucket=S3Bucket.from_dict(dict_o['bucket']), full_path=dict_o['full_path'], created=datetime.fromisoformat(dict_o['modified']))

    @staticmethod
    def from_json(json_str: str) -> "S3Object":
        return S3Object.from_dict(json.loads(json_str))



class S3Client:
    def __init__(self, boto_session: BotoSessionAwsAccount, no_verify_ssl=False) -> None:
        self.__default_region = boto_session.aws_account.region
        self.__client = boto_session.boto_session.client(
                service_name='s3',
                config=Config(
                    retries={
                        'max_attempts': 10,
                        'mode': 'standard'
                    }
                ),
                verify=not(no_verify_ssl)
            )

    def list_buckets_like(self, like_name: str, date_range: DateRange=DateRange(start=None,end=None), exact_name_match=False) -> List[S3Bucket]:
        result: List[S3Bucket] = []
        regex = re.compile(like_name, re.IGNORECASE)
        is_match = lambda name: regex.match(name) is not None
        if exact_name_match:
            is_match = lambda name: name == like_name
            
        continuationToken: str | None = None
        while True:
            response = self.__client.list_buckets() if continuationToken is None else self.__client.list_buckets(ContinuationToken=continuationToken)
            continuationToken = response['ContinuationToken'] if 'ContinuationToken' in response else None
            for bucket in response['Buckets']:
                if is_match(bucket['Name']):
                    created = bucket['CreationDate']
                    if (date_range.start is None or date_range.start <= created) and (date_range.end is None or created <= date_range.end):
                        result.append(S3Bucket(name=bucket['Name'], region=bucket['BucketRegion'], created=created))                        
            if continuationToken is None:
                break
        return result

    def list_objects_like(self, bucket: S3Bucket, like_name: str, date_range: DateRange=DateRange(start=None,end=None), exact_name_match=False) -> List[S3Object]:
        result: List[S3Object] = []
        regex = re.compile(like_name, re.IGNORECASE)
        is_match = lambda name: regex.match(name) is not None
        if exact_name_match:
            is_match = lambda name: name == like_name

        continuationToken: str | None = None
        while True:
            response = self.__client.list_objects_v2(Bucket=bucket.name) if continuationToken is None else self.__client.list_objects_v2(Bucket=bucket, ContinuationToken=continuationToken)
            continuationToken = response['ContinuationToken'] if 'ContinuationToken' in response else None
            for obj in response['Contents']:
                full_path = obj['key'].split('/')
                if is_match(full_path[-1]) is not None:
                    modified = obj['LastModified']
                    if (date_range.start is None or date_range.start <= modified) and (date_range.end is None or modified <= date_range.end):
                        result.append(S3Object(bucket=bucket, full_path=full_path, modified=modified))
            if continuationToken is None:
                break
        return result


    def list_objects(self, bucket: S3Bucket, key_prefix: str) -> List[S3Object]:
        result: List[S3Object] = []
        response = self.__client.list_objects_v2(Bucket=bucket.name, Prefix=key_prefix)
        for content in response.get("Contents"):
            result.append(S3Object(bucket=bucket, full_path=content.get('key').split('/'), modified=content.get("LastModified")))
        return result

    def get_bucket(self, bucket: str, date_range: DateRange=DateRange(start=None,end=None)) -> S3Bucket:
        buckets = self.list_buckets_like(bucket, date_range, True)
        return buckets[0]

    def get_object(self, bucket: S3Bucket, key: str) -> S3Object:
        response = self.__client.get_object(Bucket=bucket.name, Key=key)
        return S3Object(bucket=bucket, full_path=key.split('/'), modified=response.get("LastModified"))

    def get_object_body(self, bucket: str, key: str) -> StreamingBody:
        response = self.__client.get_object(Bucket=bucket.name, Key=key)
        return response.get("Body")

    def get_object_to_file(self, bucket: str, key: str, output_filepath: str) -> None:
        self.__client.download_file(Bucket=bucket,Key=key,Filename=output_filepath)

    def create_bucket(self, bucket: str) -> S3Bucket:
        response = self.__client.create_bucket(Bucket=bucket)
        return S3Bucket(name=bucket, region=self.__default_region, created=datetime.now())

    def put_object(self, bucket: str, key: str, data: BytesIO ) -> str:
        response = self.__client.put_object(Bucket=bucket, key=key, Body=data)
        return response.get("VersionId")
    
    def put_object_from_file(self, bucket: str, key: str, input_filepath: str) -> None:
        self.__client.upload_file(Bucket=bucket,Key=key,Filename=input_filepath)

    def delete_object(self, bucket: str, key: str) -> str:
        response = self.__client.delete_object(Bucket=bucket, key=key)
        return response.get("VersionId")

    def delete_bucket(self, bucket: str) -> None:
        self.__client.delete_bucket(Bucket=bucket)