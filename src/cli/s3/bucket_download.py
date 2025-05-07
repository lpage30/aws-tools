import argparse
import os
import sys

from util.logging import get_default_logger, initialize_logging
from s3.s3_client import S3Client
from util.aws_account_api import get_boto_session_aws_account

logger = get_default_logger()
def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=f"Export bucket records to csv.")

    parser.add_argument(
        "--log-level",
        type=str.lower,
        choices=["debug", "info", "warning", "error", "critical"],
        default="info",
        help="The level of logging output by this program",
    )
    parser.add_argument(
        "--aws-profile-name",
        type=str.lower,
        required=True,
        help="AWS profile name"
    )
    parser.add_argument(
        "--bucket",
        type=str,
        required=True,
        help="bucket from which to download",
    )
    parser.add_argument(
        "--key-prefix",
        type=str,
        required=True,
        help="key-prefix of objects to download",
    )
    parser.add_argument(
        "--output-directory",
        type=str,
        required=True,
        help="directory in which all objects will be downloaded",
    )
    parser.add_argument(
        "--no-verify-ssl",
        action="store_true",
        default=False,
        help="use no-verify-ssl with aws call",
    )

    args = parser.parse_args()
    return args

def main() -> None:
    args = parse_args()
    initialize_logging(args.log_level)

    try:
        boto_session_account = get_boto_session_aws_account(args.aws_profile_name)
    except Exception:
        logger.exception("Unable to obtain boto session account. %s", args.aws_profile_name)
        sys.exit(1)
    
    try:
        s3_client = S3Client(boto_session_account, args.no_verify_ssl)
    except Exception:
        logger.exception("Unable to instantiate s3 client. %s", args.aws_profile_name)
        sys.exit(1)
    try:
        s3_bucket = s3_client.get_bucket(args.bucket)
    except Exception:
        logger.exception("fetching bucket %s", args.bucket)
        sys.exit(1)
    try:
        s3_objects = s3_client.list_objects(s3_bucket, args.key_prefix)
    except Exception:
        logger.exception("list objects from bucket %s with key prefix %s", args.bucket, args.key_prefix)
        sys.exit(1)
    download_count = 0
    for s3_object in s3_objects:
        output_filepath = os.path.join(args.output_directory, s3_object.name)
        try:
            s3_client.get_object_to_file(args.bucket,  s3_object.name, output_filepath)
            download_count += 1
        except Exception:
            logger.exception("Failed downloading %s/%s to %s", args.bucket, key, output_filepath)
        
    logger.info("downloaded %d/%d objects to %s", download_count, len(s3_objects), args.output_directory)

