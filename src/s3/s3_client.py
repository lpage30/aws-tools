from io import BytesIO
import re
from botocore.response import StreamingBody
from botocore.config import Config
from util.aws_account_api import BotoSessionAwsAccount
from typing import List

class S3Client:
    def __init__(self, boto_session: BotoSessionAwsAccount) -> None:
        self.__client = boto_session.boto_session.client(
                service_name='s3',
                config=Config(
                    retries={
                        'max_attempts': 10,
                        'mode': 'standard'
                    }
                )
            )

    def list_buckets_like(self, like_name: str) -> List[str]:
        result = []
        regex = re.compile(like_name, re.IGNORECASE)
        continuationToken: str | None = None
        while True:
            response = self.__client.list_buckets() if continuationToken is None else self.__client.list_buckets(ContinuationToken=continuationToken)
            continuationToken = response['ContinuationToken'] if 'ContinuationToken' in response else None
            for bucket in response['Buckets']:
                if regex.match(bucket['Name']) is not None:
                    result.append(bucket['Name'])
            if continuationToken is None:
                break
        return result

    def list_objects_like(self, bucket: str, like_name: str) -> List[str]:
        result = []
        regex = re.compile(like_name, re.IGNORECASE)
        continuationToken: str | None = None
        while True:
            response = self.__client.list_objects_v2(Bucket=bucket) if continuationToken is None else self.__client.list_objects_v2(Bucket=bucket, ContinuationToken=continuationToken)
            continuationToken = response['ContinuationToken'] if 'ContinuationToken' in response else None
            for obj in response['Contents']:
                if regex.match(obj['Key']) is not None:
                    result.append(obj['Key'])
            if continuationToken is None:
                break
        return result


    def list_objects(self, bucket: str, key_prefix: str) -> List[str]:
        result = []
        response = self.__client.list_objects_v2(Bucket=bucket, Prefix=key_prefix)
        for content in response.get("Contents"):
            result.append(content.get("Key"))
        return result

    def get_object(self, bucket: str, key: str) -> StreamingBody():
        response = self.__client.get_object(Bucket=bucket, Key=key)
        return response.get("Body")

    def get_object_to_file(self, bucket: str, key: str, output_filepath: str) -> None:
        self.__client.download_file(Bucket=bucket,Key=key,Filename=output_filepath)

    def create_bucket(self, bucket: str) -> str:
        response = self.__client.create_bucket(Bucket=bucket)
        return response.get("Location")

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