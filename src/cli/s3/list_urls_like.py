import argparse
import sys

from util.logging import get_default_logger, initialize_logging
from s3.s3_client import S3Client
from util.aws_account_api import get_boto_session_aws_account

logger = get_default_logger()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=f"list all s3 urls with bucket name like provided skeleton and object name like provided skeleton")

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
        help="AWS profile name"
    )
    parser.add_argument(
        "--bucket-like-name",
        type=str,
        default=None,
        help="skeletal name of buckets to search",
    )
    parser.add_argument(
        "--object-like-name",
        type=str,
        default=None,
        help="skeletal name of objects to list",
    )
    parser.add_argument(
        "--output-filepath",
        type=str,
        default=None,
        help="full path of file where s3://bucket/object names will be written",
    )
    args = parser.parse_args()
    return args


def main() -> None:
    args = parse_args()
    initialize_logging(args.log_level)

    try:
        boto_session_account = get_boto_session_aws_account(args.aws_profile_name)
    except Exception:
        logger.exception(f"Unable to obtain boto session account. {args.aws_profile_name}")
        sys.exit(1)

    try:
        s3_client = S3Client(boto_session_account)
    except Exception:
        logger.exception(f"Unable to instantiate s3 client. {args.aws_profile_name}")
        sys.exit(1)

    try:
        s3_buckets = s3_client.list_buckets_like(args.bucket_like_name)
    except Exception:
        logger.exception(f"list buckets like {args.bucket_like_name}")
        sys.exit(1)
    s3_urls = []

    for bucket_name in s3_buckets:
        try:
            s3_objects = s3_client.list_objects_like(bucket_name, args.object_like_name)
        except Exception:
            logger.exception(f"skipping list objects in {bucket_name} like {args.object_like_name}")
            continue
        for name in s3_objects:
            s3_urls.append(f"s3://{bucket_name}/{name}")

    with open(args.output_filepath, 'a+') as of:
        for url in s3_urls:
            of.write(f"{url}\n")
    logger.info(f"{len(s3_urls)} s3 urls written to {args.output_filepath}")
