import argparse
from datetime import datetime, timedelta
from util.json_helpers import json_dump

from cli.arg_functions import split_flatten_array_arg, datetime_from_string
from util.logging import get_default_logger, initialize_logging
from s3.s3_client import S3Client, DateRange
from util.aws_account_api import BotoSessionAwsAccount, call_for_each_region, get_profile_region

logger = get_default_logger()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=f"list all objects with bucket name like provided skeleton and object name like provided skeleton",
        formatter_class=argparse.RawTextHelpFormatter
    )

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
        "--regions",
        nargs="+",
        default=[],
        help="list of regions to search"
    )
    parser.add_argument(
        "--bucket-like-name",
        type=str,
        required=True,
        help="skeletal name of buckets to search",
    )
    parser.add_argument(
        "--bucket-min-age-days",
        default=0,
        help="exclude buckets younger than this many days.",
    )
    parser.add_argument(
        "--bucket-max-age-days",
        type=int,
        help="exclude buckets older than this many days.",
    )
    parser.add_argument(
        "--bucket-after-date",
        type=datetime_from_string,
        help="include buckets created on or after this date",
    )

    parser.add_argument(
        "--bucket-before-date",
        type=datetime_from_string,
        help="include buckets created on or before this date",
    )

    parser.add_argument(
        "--object-like-name",
        type=str,
        required=True,
        help="skeletal name of objects to list",
    )
    parser.add_argument(
        "--object-min-age-days",
        default=0,
        help="exclude objects younger than this many days.",
    )
    parser.add_argument(
        "--object-max-age-days",
        type=int,
        help="exclude objects older than this many days.",
    )

    parser.add_argument(
        "--object-after-date",
        type=datetime_from_string,
        help="include objects modified on or after this date",
    )

    parser.add_argument(
        "--object-before-date",
        type=datetime_from_string,
        help="include objects modified on or before this date",
    )

    parser.add_argument(
        "--output-filepath",
        type=str,
        required=True,
        help="full path of file where bucket/object JSON will be written",
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
    regions = split_flatten_array_arg(args.regions) if args.regions is not None and 0 < len(args.regions) else [get_profile_region(args.aws_profile_name)]
    bucket_date_range = DateRange()
    if 0 < args.bucket_min_age_days:
        bucket_date_range.end = datetime.today() - timedelta(days=args.bucket_min_age_days)
    if args.bucket_max_age_days is not None:
        bucket_date_range.start = datetime.today() - timedelta(days=args.bucket_max_age_days)

    if args.bucket_after_date is not None:
        if bucket_date_range.start is None or bucket_date_range.start < args.bucket_after_date:
            bucket_date_range.start = args.bucket_after_date

    if args.bucket_before_date is not None:
        if bucket_date_range.end is None or args.bucket_before_date < bucket_date_range.end:
            bucket_date_range.end = args.bucket_before_date

    object_date_range = DateRange()
    if 0 < args.object_min_age_days:
        object_date_range.end = (datetime.today() - timedelta(days=args.object_min_age_days))
    if args.object_max_age_days is not None:
        object_date_range.start = (datetime.today() - timedelta(days=args.object_max_age_days))

    if args.object_after_date is not None:
        if object_date_range.start is None or object_date_range.start < args.object_after_date:
            object_date_range.start = args.object_after_date

    if args.object_before_date is not None:
        if object_date_range.end is None or args.object_before_date < object_date_range.end:
            object_date_range.end = args.object_before_date

    logger.info(f"Listing {args.aws_profile_name} sourced objects where Bucket like {args.bucket_like_name} in {bucket_date_range} and object like {args.object_like_name} in {object_date_range} across regions [{','.join(regions)}]")
    s3_objects = []

    def collect_objects(session: BotoSessionAwsAccount):
        try:
            s3_client = S3Client(session, args.no_verify_ssl)
        except Exception:
            logger.exception(f"Unable to instantiate s3 client. {session.boto_session.profile_name}")
            return
        try:
            s3_buckets = s3_client.list_buckets_like(args.bucket_like_name, bucket_date_range)
        except Exception:
            logger.exception(f"list buckets like {args.bucket_like_name} region {session.boto_session.region_name}")
            return
        s3_region_objects = []
        for s3_bucket in s3_buckets:
            try:
                s3_region_objects.extend(s3_client.list_objects_like(s3_bucket, args.object_like_name, object_date_range))
            except Exception:
                logger.exception(f"list objects in {s3_bucket.name} ({session.aws_account.region}) like {args.object_like_name}")
                return
        s3_objects.extend(s3_region_objects)
        logger.info(f"Collected {len(s3_region_objects)} objects across {len(s3_buckets)} buckets in {session.aws_account.region}")

    call_for_each_region(lambda session: collect_objects(session), regions, args.aws_profile_name)
    
    s3_objects.sort(reverse=True)

    with open(args.output_filepath, 'w') as of:
        json_dump({
            'datetime': datetime.now().isoformat(),
            'args': {
                'profile': args.aws_profile_name,
                'regions': regions,
                'bucket_args': {
                    'like_name': args.bucket_like_name,
                    'date_range': bucket_date_range.__str__(),
                },
                'object_args': {
                    'like_name': args.object_like_name,
                    'date_range': object_date_range.__str__(),
                }
            },
            'result': {
                's3_objects': s3_objects
            }
        }, of)

    logger.info(f"{len(s3_objects)} bucket/object names written as JSON to {args.output_filepath}")
