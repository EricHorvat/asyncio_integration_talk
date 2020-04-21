from .exceptions import JsonValidaitonError
import json


def json_payload(raw_payload: bytearray):
    payload = raw_payload.decode(encoding='UTF-8')
    try:
        return json.loads(payload)
    except ValueError as e:
        raise JsonValidaitonError('Payload is not json serialisable')