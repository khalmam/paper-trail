"""Chooses the parser and the answerer. Offline unless PAPER_TRAIL_PARSER=bedrock."""
import os

from .answer import BedrockAnswerer, FakeAnswerer, FallbackAnswerer
from .bedrock import BedrockParser, FallbackParser
from .converse import BedrockConverser
from .fake import FakeParser

DEFAULT_MODEL = "us.anthropic.claude-haiku-4-5-20251001-v1:0"


def _bedrock():
    import boto3
    from botocore.config import Config

    client = boto3.client(
        "bedrock-runtime", region_name=os.environ.get("AWS_REGION", "us-east-1"),
        config=Config(read_timeout=15, retries={"max_attempts": 1}),
    )
    return client, os.environ.get("BEDROCK_MODEL_ID", DEFAULT_MODEL)


def _enabled() -> bool:
    return os.environ.get("PAPER_TRAIL_PARSER", "fake") == "bedrock"


def make_parser():
    if not _enabled():
        return FakeParser()
    client, model = _bedrock()
    return FallbackParser(BedrockParser(client, model), FakeParser())


def make_converser():
    if not _enabled():
        return None
    client, model = _bedrock()
    return BedrockConverser(client, model)


def make_answerer():
    if not _enabled():
        return FakeAnswerer()
    client, model = _bedrock()
    return FallbackAnswerer(BedrockAnswerer(client, model), FakeAnswerer())
