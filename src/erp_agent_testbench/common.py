"""Offline JSON contracts, canonical identities and exact arithmetic."""

import hashlib
import json
from datetime import datetime, timezone
from functools import lru_cache
from importlib.resources import files
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker
from referencing import Registry, Resource


class ContractError(ValueError):
    """Invalid or unsupported input; no external action has been taken."""


def canonical(value):
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False
    )


def digest(value):
    return hashlib.sha256(canonical(value).encode("utf-8")).hexdigest()


def timestamp(value):
    try:
        result = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if result.tzinfo is None or result.utcoffset() is None:
            raise ValueError("timezone required")
        return result.astimezone(timezone.utc)
    except (ValueError, TypeError, AttributeError) as exc:
        raise ContractError("invalid timezone-aware timestamp") from exc


def exact_integer(value, minimum=0, maximum=2**63 - 1):
    if type(value) is not int or not minimum <= value <= maximum:
        raise ContractError("integer outside supported bounds")
    return value


def unique(records, key):
    result = {}
    for record in records:
        identity = key(record)
        if identity in result:
            raise ContractError("duplicate identity")
        result[identity] = record
    return result


def _pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ContractError("duplicate JSON key")
        result[key] = value
    return result


def _reject_constant(value):
    raise ContractError("nonfinite JSON number")


def read_json(path):
    raw = Path(path).read_bytes()
    if len(raw) > 5_000_000:
        raise ContractError("input exceeds 5 MB limit")
    return json.loads(raw, object_pairs_hook=_pairs, parse_constant=_reject_constant)


@lru_cache
def validator(name):
    directory = files(__package__ + ".schemas")
    documents = {
        p.name: json.loads(p.read_text())
        for p in directory.iterdir()
        if p.name.endswith(".schema.json")
    }
    registry = Registry()
    for filename, schema in documents.items():
        resource = Resource.from_contents(schema)
        registry = registry.with_resource(filename, resource)
        if "$id" in schema:
            registry = registry.with_resource(schema["$id"], resource)
    return Draft202012Validator(
        documents[name + ".schema.json"], registry=registry, format_checker=FormatChecker()
    )


def validate_shape(value, name):
    errors = list(validator(name).iter_errors(value))
    if errors:
        # Report field paths, never raw payload values or foreign records.
        path = "/".join(str(part) for part in errors[0].absolute_path)
        raise ContractError("schema violation at /" + path)
