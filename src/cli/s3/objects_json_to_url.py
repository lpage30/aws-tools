import argparse
from util.json_helpers import json_load, json_dump
from util.logging import get_default_logger, initialize_logging
from s3.s3_client import  S3Object, S3URL

logger = get_default_logger()

class ValidateS3UrlTemplate(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        if S3URL.is_valid_url_template(values):
            parser.error(f"Invalid url template. Got: {values}")
        setattr(namespace, self.dest, values)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=f"Convert JSON file array of S3 Objects to array of S3 urls",
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
        "--input-filepath",
        type=str,
        required=True,
        help="full path of file containing bucket/object JSON",
    )
    parser.add_argument(
        "--s3-url-template",
        action=ValidateS3UrlTemplate,
        default=S3URL.default_template(),
        help=S3URL.template_help()
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
    
    url_formatter = S3URL(args.s3_url_template)
    s3_objects = []
    s3_url_datetime = None
    logger.info(f"Loading S3 Object definitions from {args.input_filepath}")
    try:
        with open(args.input_filepath, 'r') as inF:
            data = json_load(inF)
            if 'datetime' in data:
                s3_url_datetime = data['datetime']
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
        
        logger.info(f"Converting {len(s3_objects)} S3 Objects to {len(s3_objects)} urls of form {args.s3_url_template}")
        s3_urls = [
            { 
                'url': url_formatter.to_url(o),
                'date': o.modified.isoformat(),
                'size': o.size
            } for o in s3_objects
        ]
        logger.debug(f"Writing {len(s3_urls)} urls to {args.output_filepath}")
        with open(args.output_filepath, 'w') as of:
            json_dump({
                'datetime': s3_url_datetime,
                'args': {
                    'input_filepath': args.input_filepath,
                    's3_url_template': args.s3_url_template
                },
                'result': {
                    's3_urls': s3_urls
                }
            }, of)
            logger.info(f"{len(s3_urls)} S3 urls written to {args.output_filepath}")
    except Exception:
        logger.exception(f"Failed converting S3 objects in {args.input_filepath} to S3 urls in {args.output_filepath}")