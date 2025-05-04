import argparse
import sys

from util.logging import get_default_logger, initialize_logging
from s3.s3_client import S3Client
from util.aws_account_api import get_boto_session_aws_account

logger = get_default_logger()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=f"list all object names in named bucket like provided skeleton")

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
        "--bucket-name",
        type=str,
        default=None,
        help="Name of bucket in which to search",
    )
    parser.add_argument(
        "--like-name",
        type=str,
        default=None,
        help="skeletal name of objects to list",
    )
    parser.add_argument(
        "--output-filepath",
        type=str,
        default=None,
        help="full path of file where bucket/object names will be written",
    )
    args = parser.parse_args()
    return args


def main() -> None:
    args = parse_args
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
        s3_objects = s3_client.list_objects_like(args.bucket_name, args.like_name)
    except Exception:
        logger.exception(f"list objects in {args.bucket_name} like {args.like_name}")
        sys.exit(1)

    with open(args.output_filepath, 'a+') as of:
        for name in s3_objects:
            of.write(f"{args.bucket_name}/{name}\n")
    logger.info(f"{len(s3_objects)} bucket/object names written to {args.output_filepath}")
