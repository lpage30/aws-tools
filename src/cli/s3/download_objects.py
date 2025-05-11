import argparse
import os
from s3.s3_client import S3Client
from util.aws_account_api import get_boto_session_aws_account
from util.json_helpers import json_load, json_dump
from util.logging import get_default_logger, initialize_logging
from s3.s3_client import  S3Object

logger = get_default_logger()

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=f"Download top X S3 Objects listed in input file to directory",
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
        "--top-count",
        default=1,
        type=int,
        help="download the most recent this many objects."
    )

    parser.add_argument(
        "--input-filepath",
        type=str,
        required=True,
        help="full path of file containing bucket/object JSON",
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
    
    s3_objects = []
    s3_download_datetime = None
    output_dirpath = os.path.dirname(args.input_filepath)
    logger.info(f"Loading S3 Object definitions from {args.input_filepath}")
    try:
        with open(args.input_filepath, 'r') as inF:
            data = json_load(inF)
            if 'datetime' in data:
                s3_download_datetime = data['datetime']
            if 'result' in data:
                data = data['result']
                logger.info(f"1) result")
            if 's3_objects' in data:
                data = data['s3_objects']
            if isinstance(data, list):
                s3_objects = [S3Object.from_dict(o) for o in data]
                s3_objects.sort(reverse=True)
                logger.debug(f"Loaded {len(s3_objects)} S3 Objects")
            else:
                raise TypeError(f"Data not type list. {args.input_filepath}")
        
    except Exception:
        logger.exception(f"Failed loading S3 objects from {args.input_filepath}")
        return
        
    download_count = min(len(s3_objects), args.top_count)

    logger.info(f"downloading top {download_count}/{len(s3_objects)} S3 Objects to {output_dirpath}")
    s3_downloads = []
    try:
        session = get_boto_session_aws_account(args.aws_profile_name)
        s3_client = S3Client(session, args.no_verify_ssl)
        for i in range(download_count):
            s3_object = s3_objects[i]
            output_filename = s3_object.fully_qualified_name.replace('/','.')
            output_filepath = os.path.join(output_dirpath, output_filename)
            try:
                s3_client.get_object_to_file(s3_object.bucket.name,  s3_object.name, output_filepath)
                logger.debug(f"{s3_object} downloaded to {output_filepath}")
                s3_downloads.append({
                    'filename': output_filename,
                    'metadata': s3_object.__str__()
                })
            except Exception:
                logger.exception(f"Failed downloading {s3_object.fully_qualified_name} to {output_filepath}")
            
        logger.info(f"downloaded {download_count}/{len(s3_objects)} objects to {output_dirpath}")
    except Exception:
        logger.exception(f"Failed downloading S3 objects in {args.input_filepath} to  {output_dirpath}")
    if 0 < len(s3_downloads):
        output_filename = os.path.splitext(os.path.basename(args.input_filepath))
        output_filename = f"{output_filename[0]}-downloads{output_filename[1]}"
        output_filepath = os.path.join(output_dirpath, output_filename)
        logger.debug(f"Writing {len(s3_downloads)} metadata for downloads to {output_filepath}")
        with open(output_filepath, 'w') as of:
            json_dump({
                'datetime': s3_download_datetime,
                'args': {
                    'top_count': args.top_count,
                    'input_filepath': args.input_filepath
                },
                'result': {
                    'input_count': len(s3_objects),
                    'output_count': len(s3_downloads),
                    's3_downloads': s3_downloads
                }
            }, of)
            logger.info(f"{len(s3_downloads)} metadata for downloads written to {output_filepath}")
    
