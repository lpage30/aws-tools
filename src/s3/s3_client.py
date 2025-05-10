from datetime import datetime, timezone
from io import BytesIO
import re
from botocore.response import StreamingBody
from botocore.config import Config
from util.aws_account_api import BotoSessionAwsAccount
from typing import List
import urllib
from util.logging import get_default_logger

class DateRange:
    def __init__(self, start: datetime|None = None, end: datetime|None = None):
        self.start = start
        self.end = end

    @property
    def start(self) -> datetime|None:
        return self._start

    @start.setter
    def start(self, value: datetime|None) -> None:
        self._start = value.replace(tzinfo=timezone.utc) if value is not None else None

    @property
    def end(self) -> datetime|None:
        return self._end

    @end.setter
    def end(self, value: datetime|None) -> None:
        self._end = value.replace(tzinfo=timezone.utc) if value is not None else None


    def __str__(self) -> str:
        if self.start is None and self.end is None:
            return f"DateRange[any-date]"
        elif self.start is None:
            return f"DateRange[before({self.end.isoformat()})]"
        elif self.end is None:
            return f"DateRange[after({self.start.isoformat()})]"
        return f"DateRange[between({self.start.isoformat()},{self.end.isoformat()})]"
    
    def in_range(self, dt: datetime) -> bool:
        if self.start is None and self.end is None:
            return True
        utc_dt = dt
        if dt.tzinfo is None:
            utc_dt = dt.replace(tzinfo=timezone.utc)
        if self.start is None:
            return utc_dt <= self.end
        if self.end is None:
            return self.start <= utc_dt
        return self.start <= utc_dt and utc_dt <= self.end

class S3Bucket:
    def __init__(self, name:str, region: str, created: datetime):
        self.name = name
        self.region = region
        self.created = created

    def __str__(self) -> str:
        return f"S3Bucket[name={self.name},region={self.region},created={self.created.isoformat()}]"
    
    def __lt__(self, other) -> bool:
        if self.created.__eq__(other.created):
            return self.name.__lt__(other.name)
        return self.created.__lt__(other.created)
    
    def to_url(self, bucket_url_template: str) -> str:
        return bucket_url_template.replace('{region}', self.region).replace('{name}', self.name)
   
    @staticmethod
    def from_dict(dict_o: dict) -> "S3Bucket":
        return S3Bucket(name=dict_o['name'], region=dict_o['region'], created=datetime.fromisoformat(dict_o['created']))
 
class S3Object:
    def __init__(self, bucket: S3Bucket, full_path: List[str], modified: datetime, size: int):
        self.bucket = bucket
        self.full_path = full_path
        self.modified = modified
        self.size = size

    def __str__(self) -> str:
        return f"{self.bucket}.S3Object[name={'/'.join(self.full_path)},modified={self.modified.isoformat()},size={self.size}]"

    def __lt__(self, other) -> bool:
        if self.modified.__eq__(other.modified):
            if self.name.__eq__(other.name):
                return self.size.__lt__(other.size)
            return self.name.__lt__(other.name)
        return self.modified.__lt__(other.modified)

    @staticmethod
    def from_dict(dict_o: dict) -> "S3Object":
        return S3Object(bucket=S3Bucket.from_dict(dict_o['bucket']), full_path=dict_o['full_path'], created=datetime.fromisoformat(dict_o['modified']), size=dict_o['size'])

class S3URL:
    def __init__(self, s3_url_template: str | None = None):
        self.s3_url_template = S3URL.default_template()
        if s3_url_template is not None:
            self.s3_url_template = s3_url_template

    def to_url(self, s3_object: S3Object) -> str:
        region = s3_object.bucket.region
        bucket_name = s3_object.bucket.name
        object_full_path = '/'.join(s3_object.full_path)
        return self.s3_url_template.format(region=region, bucket_name=bucket_name, object_full_path = object_full_path)
    
    @staticmethod
    def default_template() -> str:
        return "http://s3.{region}.amazonaws.com/{bucket_name}/{object_full_path}"
    
    @staticmethod
    def is_valid_url_template(s3_url_template: str) -> bool:
        bucket_name = 'BUCKET_NAME'
        region = 'REGION'
        object_full_path = 'OBJECT/FULL/PATH'
        try:
            urllib.parse(s3_url_template.format(region=region, bucket_name=bucket_name, object_full_path = object_full_path))
            return True
        except:
            return False

    @staticmethod
    def template_help() -> str:
        return """A string containing fields expressed within '{}': {region}, {bucket_name}, {object_full_path}
ie. http://s3.{region}.amazonaws.com/{bucket_name}/{object_full_path}
{region} - region in which bucket was found
{bucket_name} - name of bucket for object
{object_full_path} - full path of object in bucket ie. folder/subfolder/object_name, or, if no folder, object_name
"""

class S3Client:
    def __init__(self, boto_session: BotoSessionAwsAccount, no_verify_ssl=False) -> None:
        logger = get_default_logger()
        try:
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
        except Exception:
            logger.exception(f"Unable to obtain S3 client no-verify-ssl={no_verify_ssl} from {boto_session.aws_account.name}")
            raise
        logger.debug(f"Obtained S3 client no-verify-ssl={no_verify_ssl} from {boto_session.aws_account.name}")


    def list_buckets_like(self, like_name: str, date_range: DateRange=DateRange(start=None,end=None), exact_name_match=False) -> List[S3Bucket]:
        logger = get_default_logger()
        result: List[S3Bucket] = []
        regex = re.compile(like_name, re.IGNORECASE)
        is_match = lambda name: regex.match(name) is not None
        if exact_name_match:
            is_match = lambda name: name == like_name
            
        continuationToken: str | None = None
        logger.debug(f"listing buckets named {'exactly' if exact_name_match else 'like'} {like_name} in {date_range}")
        try:
            while True:
                try:
                    response = self.__client.list_buckets() if continuationToken is None else self.__client.list_buckets(ContinuationToken=continuationToken)
                    continuationToken = response['ContinuationToken'] if 'ContinuationToken' in response else None
                    buckets = response['Buckets'] if 'Buckets' in response else []
                    for bucket in buckets:
                        if is_match(bucket['Name']):
                            created = bucket['CreationDate']
                            region = bucket['BucketRegion'] if 'BucketRegion' in bucket else self.__default_region
                            if date_range.in_range(created):
                                result.append(S3Bucket(name=bucket['Name'], region=region, created=created))                        
                    if continuationToken is None:
                        break
                except KeyError:
                    logger.error(f"KeyError: response={response}")
                    raise
        except Exception:
            logger.exception(f"AWS S3 list_buckets Failed for buckets named {'exactly' if exact_name_match else 'like'} {like_name} in {date_range}")
            raise
        logger.debug(f"Obtained {len(result)} buckets named {'exactly' if exact_name_match else 'like'} {like_name} in {date_range}")
        return result.sort(reverse=True)

    def list_objects_like(self, bucket: S3Bucket, like_name: str, date_range: DateRange=DateRange(start=None,end=None), exact_name_match=False) -> List[S3Object]:
        logger = get_default_logger()
        result: List[S3Object] = []
        regex = re.compile(like_name, re.IGNORECASE)
        is_match = lambda name: regex.match(name) is not None
        if exact_name_match:
            is_match = lambda name: name == like_name

        logger.debug(f"listing objects for bucket {bucket} where objects named {'exactly' if exact_name_match else 'like'} {like_name} in {date_range}")
        continuationToken: str | None = None
        try:
            while True:
                try:
                    response = self.__client.list_objects_v2(Bucket=bucket.name) if continuationToken is None else self.__client.list_objects_v2(Bucket=bucket, ContinuationToken=continuationToken)
                    continuationToken = response['ContinuationToken'] if 'ContinuationToken' in response else None
                    contents = response['Contents'] if 'Contents' in response else []
                    for obj in contents:
                        full_path = obj['Key'].split('/')
                        if is_match(full_path[-1]) is not None:
                            modified = obj['LastModified']
                            if date_range.in_range(modified):
                                result.append(S3Object(bucket=bucket, full_path=full_path, modified=modified))
                    if continuationToken is None:
                        break
                except KeyError:
                    logger.error(f"KeyError: response={response}")
                    raise
        except Exception:
            logger.exception(f"AWS S3 list_objects_v2 Failed for bucket {bucket} and objects named {'exactly' if exact_name_match else 'like'} {like_name} in {date_range}")
            raise
        logger.debug(f"Obtained {len(result)} objects for bucket {bucket} where objects named {'exactly' if exact_name_match else 'like'} {like_name} in {date_range}")
        return result.sort(reverse=True)


    def list_objects(self, bucket: S3Bucket, key_prefix: str) -> List[S3Object]:
        logger = get_default_logger()
       
        result: List[S3Object] = []
        logger.debug(f"listing objects for bucket {bucket} where objects have prefix {key_prefix}")
        try:
            response = self.__client.list_objects_v2(Bucket=bucket.name, Prefix=key_prefix)
            contents = response['Contents'] if 'Contents' in response else []
            for content in contents:
                result.append(S3Object(bucket=bucket, full_path=content.get('Key').split('/'), modified=content.get("LastModified")))
        except Exception:
            logger.exception(f"AWS S3 list_objects_v2 Failed for bucket {bucket} where objects have prefix {key_prefix}")
            raise
        logger.debug(f"Obtained {len(result)} objects for bucket {bucket} where objects have prefix {key_prefix}")
        return result.sort(reverse=True)

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
        response = self.__client.put_object(Bucket=bucket, Key=key, Body=data)
        return response.get("VersionId")
    
    def put_object_from_file(self, bucket: str, key: str, input_filepath: str) -> None:
        self.__client.upload_file(Bucket=bucket,Key=key,Filename=input_filepath)

    def delete_object(self, bucket: str, key: str) -> str:
        response = self.__client.delete_object(Bucket=bucket, Key=key)
        return response.get("VersionId")

    def delete_bucket(self, bucket: str) -> None:
        self.__client.delete_bucket(Bucket=bucket)