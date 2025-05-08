from datetime import datetime, timezone
from io import BytesIO
import re
from botocore.response import StreamingBody
from botocore.config import Config
from util.aws_account_api import BotoSessionAwsAccount
from typing import List
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
    
    def to_url(self, bucket_url_template: str) -> str:
        return bucket_url_template.replace('{region}', self.region).replace('{name}', self.name)
   
    @staticmethod
    def from_dict(dict_o: dict) -> "S3Bucket":
        return S3Bucket(name=dict_o['name'], region=dict_o['region'], created=datetime.fromisoformat(dict_o['created']))
   
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

    def __str__(self) -> str:
        return f"{self.bucket}.S3Object[name={'/'.join(self.full_path)},modified={self.modified.isoformat()}]"

    def to_url(self, bucket_url_template: str) -> str:
        return f"{self.bucket.to_url(bucket_url_template)}/{'/'.join(self.full_path)}"

    @staticmethod
    def from_dict(dict_o: dict) -> "S3Object":
        return S3Object(bucket=S3Bucket.from_dict(dict_o['bucket']), full_path=dict_o['full_path'], created=datetime.fromisoformat(dict_o['modified']))


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
        return result

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
        return result


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
        response = self.__client.put_object(Bucket=bucket, Key=key, Body=data)
        return response.get("VersionId")
    
    def put_object_from_file(self, bucket: str, key: str, input_filepath: str) -> None:
        self.__client.upload_file(Bucket=bucket,Key=key,Filename=input_filepath)

    def delete_object(self, bucket: str, key: str) -> str:
        response = self.__client.delete_object(Bucket=bucket, Key=key)
        return response.get("VersionId")

    def delete_bucket(self, bucket: str) -> None:
        self.__client.delete_bucket(Bucket=bucket)