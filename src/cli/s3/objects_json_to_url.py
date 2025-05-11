import argparse
import os
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
        description=f"Convert top x S3 Objects s3 urls",
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
        "--top-count",
        default=1,
        type=int,
        help="convert the most recent this many objects."
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

    args = parser.parse_args()
    return args


def main() -> None:
    args = parse_args()
    initialize_logging(args.log_level)
    
    url_formatter = S3URL(args.s3_url_template)
    s3_objects = []
    s3_url_datetime = None
    output_dirpath = os.path.dirname(args.input_filepath)
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
        url_count = min(len(s3_objects), args.top_count)
        logger.info(f"converting top {url_count}/{len(s3_objects)} S3 Objects to url-form: {args.s3_url_template}")
        s3_urls = []
        for i in range(url_count):
            s3_object = s3_objects[i]
            s3_urls.append({
                'url': url_formatter.to_url(s3_object),
                'metadata': s3_object.__str__()
            })
        output_filename = os.path.splitext(os.path.basename(args.input_filepath))
        output_filename = f"{output_filename[0]}-urls{output_filename[1]}"
        output_filepath = os.path.join(output_dirpath, output_filename)

        logger.debug(f"Writing {len(s3_urls)} urls to {output_filepath}")
        with open(output_filepath, 'w') as of:
            json_dump({
                'datetime': s3_url_datetime,
                'args': {
                    'top_count': args.top_count,
                    'input_filepath': args.input_filepath,
                    's3_url_template': args.s3_url_template
                },
                'result': {
                    'input_count': len(s3_objects),
                    'output_count': len(s3_urls),
                    's3_urls': s3_urls
                }
            }, of)
            logger.info(f"{len(s3_urls)} S3 urls written to {output_filepath}")
    except Exception:
        logger.exception(f"Failed converting S3 objects in {args.input_filepath} to S3 urls in {output_filepath}")