import boto3
from attrs import define

@define(auto_attribs=True)
class AwsAccount:
    name: str
    region: str
    id: str

@define(auto_attribs=True)
class BotoSessionAwsAccount:
    aws_account: AwsAccount
    boto_session: boto3.session.Session

def get_boto_session_aws_account(profile: str, region: str|None = None, roleArn: str|None = None) -> BotoSessionAwsAccount:
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
    sts_account_dict = boto_session.client('sts').get_caller_identity()
    aws_account = AwsAccount(name=name, region=boto_session.region_name, id=sts_account_dict['Account'])
    return BotoSessionAwsAccount(aws_account=aws_account, boto_session=boto_session)