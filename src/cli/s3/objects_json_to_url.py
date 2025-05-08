import argparse
from util.json_helpers import json_load
from util.logging import get_default_logger, initialize_logging
from s3.s3_client import S3Bucket, S3Object

logger = get_default_logger()

class ValidateBucketUrlTemplate(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        if S3Bucket.is_valid_url_template(values):
            parser.error(f"Invalid url template. Got: {values}")
        setattr(namespace, self.dest, values)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=f"Convert JSON file array of S3 Objects to array of S3 urls")

    parser.add_argument(
        "--log-level",
        type=str.lower,
        choices=["debug", "info", "warning", "error", "critical"],
        default="info",
        help="The level of logging output by this program",
    )
    parser.add_argument(
        "--input-filepath",
        type=str,
        required=True,
        help="full path of file containing bucket/object JSON",
    )
    parser.add_argument(
        "--bucket-url-template",
        action=ValidateBucketUrlTemplate,
        default=S3Bucket.default_bucket_url_template(),
        help=S3Bucket.bucket_url_template_help()
    )
    parser.add_argument(
        "--output-filepath",
        type=str,
        required=True,
        help="full path of file where s3://bucket/object names will be written",
    )

    args = parser.parse_args()
    return args


def main() -> None:
    args = parse_args()
    initialize_logging(args.log_level)
    
    s3_objects = []
    logger.info(f"Converting S3 Object definitions in {args.input_filepath} to S3 urls in {args.output_filepath}")
    try:
        with open(args.input_filepath, 'r') as inF:
            data = json_load(inF)
            if 'result' in data:
                data = data['result']
            if 's3_objects' in data:
                data = data['s3_objects']
            if isinstance(data, list):
                s3_objects = [S3Object.from_dict(o) for o in data]

        if 0 < len(s3_objects):
            with open(args.output_filepath, 'a+') as outF:
                for s3_object in s3_objects:
                    outF.write(f"{s3_object.to_url(args.bucket_url_template)}\n")
            
            logger.info(f"{len(s3_objects)} S3 urls written to {args.output_filepath}")
        else:
            logger.warning(f"No S3 objects found to write as urls.")
    except Exception:
        logger.exception(f"Failed converting S3 objects in {args.input_filepath} to S3 urls in {args.output_filepath}")