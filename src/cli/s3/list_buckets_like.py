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
        description=f"list all bucket names like provided skeleton",
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
        default=None,
        help="list of regions to search"
    )

    parser.add_argument(
        "--like-name",
        type=str,
        required=True,
        help="skeletal name of buckets to list",
    )
    parser.add_argument(
        "--min-age-days",
        default=0,
        help="exclude buckets younger than this many days.",
    )
    parser.add_argument(
        "--max-age-days",
        type=int,
        help="exclude buckets older than this many days.",
    )
    parser.add_argument(
        "--after-date",
        type=datetime_from_string,
        help="include buckets created on or after this date",
    )

    parser.add_argument(
        "--before-date",
        type=datetime_from_string,
        help="include buckets created on or before this date",
    )

    parser.add_argument(
        "--output-filepath",
        type=str,
        required=True,
        help="full path of file where names will be written",
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
    date_range = DateRange()
    if 0 < args.min_age_days:
        date_range.end = datetime.today() - timedelta(days=args.min_age_days)
    if args.max_age_days is not None:
        date_range.start = datetime.today() - timedelta(days=args.max_age_days)

    if args.after_date is not None:
        if date_range.start is None or date_range.start < args.after_date:
            date_range.start = args.after_date

    if args.before_date is not None:
        if date_range.end is None or args.before_date < date_range.end:
            date_range.end = args.before_date

    logger.info(f"Listing {args.aws_profile_name} sourced buckets where Bucket like {args.like_name} in {date_range} across regions [{','.join(regions)}]")

    s3_buckets = []

    def collect_buckets(session: BotoSessionAwsAccount):
        try:
            s3_client = S3Client(session, args.no_verify_ssl)
        except Exception:
            logger.exception(f"Unable to instantiate s3 client. {args.aws_profile_name}")
            return
        try:
            s3_region_buckets = s3_client.list_buckets_like(args.like_name, date_range)
        except Exception:
            logger.exception(f"list buckets like {args.like_name} region {session.boto_session.region_name}")
            return
        s3_buckets.extend(s3_region_buckets)
        logger.info(f"Collected {len(s3_region_buckets)} buckets in {session.aws_account.region}")



    call_for_each_region(lambda session: collect_buckets(session), regions, args.aws_profile_name)
    s3_buckets.sort(reverse=True)
    with open(args.output_filepath, 'w') as of:
        json_dump({
            'datetime': datetime.now().isoformat(),
            'args': {
                'profile': args.aws_profile_name,
                'regions': regions,
                'bucket_args': {
                    'like_name': args.like_name,
                    'date_range': date_range.__str__(),
                },
            },
            'result': {
                'output_count': len(s3_buckets),
                's3_buckets': s3_buckets
            }
        }, of)
        
    logger.info(f"{len(s3_buckets)} bucket names written as JSON to {args.output_filepath}")
