import argparse
import os
import sys

from util.logging import get_default_logger, initialize_logging
from s3.s3_client import S3Client
from util.aws_account_api import get_boto_session_aws_account

logger = get_default_logger()
def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=f"Import csv records to bucket.",
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
        "--bucket",
        type=str,
        required=True,
        help="bucket to upload into",
    )

    parser.add_argument(
        "--input-directory",
        type=str,
        required=True,
        help="directory from which all files will uploaded into bucket",
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
        s3_keys = os.listdir(args.input_directory)
    except Exception:
        logger.exception("list contents of directory %s", args.input_directory)
        sys.exit(1)
    file_count = 0
    upload_count = 0
    for key in s3_keys:
        input_filepath = os.path.join(args.input_directory, key)
        if not(os.path.isfile(input_filepath)):
            continue
        file_count += 1
        try:
            s3_client.put_object_from_file(args.bucket, key, input_filepath)
            upload_count += 1
        except Exception:
            logger.exception("Failed uploading %s to %s/%s to %s", input_filepath, args.bucket, key)
        
    logger.info("uploaded %d/%d objects from %s to bucket %s", upload_count, file_count, args.input_directory, args.bucket)

