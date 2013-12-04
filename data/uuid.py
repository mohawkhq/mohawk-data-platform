from __future__ import absolute_import

import uuid, base64


def generate():
    return unicode(base64.urlsafe_b64encode(uuid.uuid4().bytes).rstrip("="))