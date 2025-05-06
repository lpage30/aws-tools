import argparse
import sys
from util.aws_login import aws_sso_login
from util.logging import get_default_logger, initialize_logging

logger = get_default_logger()



def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=f"aws sso login --profile")
    parser.add_argument(
        "--aws-profile-name",
        type=str.lower,
        required=True,
        help="AWS profile name"
    )
    args = parser.parse_args()
    return args


def main() -> None:
    args = parse_args()
    initialize_logging("info")

    logger.info(f"aws sso login --profile {args.aws_profile_name}. browser will popup to confirm your token for access.")
    if not aws_sso_login(args.aws_profile_name):
        sys.exit(1)

    logger.info(f"logged-in")