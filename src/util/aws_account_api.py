import boto3
from attrs import define
from typing import Callable, List
from util.logging import get_default_logger

@define(auto_attribs=True)
class AwsAccount:
    name: str
    region: str
    id: str

@define(auto_attribs=True)
class BotoSessionAwsAccount:
    aws_account: AwsAccount
    boto_session: boto3.session.Session


def get_profile_region(profile: str) -> str:
    return boto3.session.Session(profile_name=profile).region_name


def get_boto_session_aws_account(profile: str, region: str|None = None, roleArn: str|None = None) -> BotoSessionAwsAccount:
    logger = get_default_logger()
    try:
        if region is None and roleArn is None:
            name = f"{profile}"
            boto_session = boto3.session.Session(profile_name=profile)
        elif roleArn is None:
            name = f"{profile}.{region}"
            boto_session = boto3.session.Session(profile_name=profile, region_name=region)
        elif region is None:
            name = f"{profile}.{roleArn.split(':')[-1]}"
            assumed_role = boto3.client('sts').assume_role(RoleArn=roleArn,RoleSessionName=name)
            boto_session = boto3.session.Session(
                profile_name=profile,
                aws_access_key_id=assumed_role['Credentials']["AccessKeyId"],
                aws_secret_access_key=assumed_role['Credentials'],
                aws_session_token=assumed_role['Credentials'],
            )
        else:
            name = f"{profile}.{region}.{roleArn.split(':')[-1]}"
            assumed_role = boto3.client('sts').assume_role(RoleArn=roleArn,RoleSessionName=name)
            boto_session = boto3.session.Session(
                profile_name=profile,
                region_name=region,
                aws_access_key_id=assumed_role['Credentials']["AccessKeyId"],
                aws_secret_access_key=assumed_role['Credentials'],
                aws_session_token=assumed_role['Credentials'],
            )
    except Exception:
        logger.exception(f"Unable to obtain boto session account. {name}")
        raise

    try:
        sts_account_dict = boto_session.client('sts').get_caller_identity()
        aws_account = AwsAccount(name=name, region=boto_session.region_name, id=sts_account_dict['Account'])
    except Exception:
        logger.exception(f"Unable to obtain sts caller identity. {name}")
        raise
    logger.debug(f"Obtained boto AWS session {name}")
    return BotoSessionAwsAccount(aws_account=aws_account, boto_session=boto_session)


def call_for_each_region(callback: Callable[[BotoSessionAwsAccount], None], regions: List[str], profile: str, roleArn: str|None = None):
    logger = get_default_logger()
    for region in regions:
        try:
            boto_session_account = get_boto_session_aws_account(profile, region, roleArn)
        except Exception:
            return
        try:
            callback(boto_session_account)
        except Exception:
            logger.exception(f"Failed calling callback. {profile}, {region}, {roleArn}")
            return
