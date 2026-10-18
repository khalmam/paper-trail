"""Chooses the parser. Offline keyword parser unless PAPER_TRAIL_PARSER=bedrock."""
import os

from .bedrock import BedrockParser, FallbackParser
from .fake import FakeParser

DEFAULT_MODEL = "us.anthropic.claude-haiku-4-5-20251001-v1:0"


def make_parser():
    if os.environ.get("PAPER_TRAIL_PARSER", "fake") != "bedrock":
        return FakeParser()
    import boto3
    from botocore.config import Config

    client = boto3.client(
        "bedrock-runtime", region_name=os.environ.get("AWS_REGION", "us-east-1"),
        config=Config(read_timeout=15, retries={"max_attempts": 1}),
    )
    return FallbackParser(BedrockParser(client, os.environ.get("BEDROCK_MODEL_ID", DEFAULT_MODEL)), FakeParser())
