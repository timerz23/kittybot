# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
# Theid file is stolen from https://github.com/udf/uniborg/blob/kate/stdplugins/info.py
"""Get Detailed info about any message
Syntax: .json"""
from telethon import events
from telethon.utils import add_surrogate
from telethon.tl.types import MessageEntityPre, DocumentAttributeFilename
from telethon.tl.tlobject import TLObject
from telethon.errors import MessageTooLongError
import datetime
import io
from uniborg.util import admin_cmd


def parse_pre(text):
    text = text.strip()
    return (
        text,
        [MessageEntityPre(offset=0, length=len(add_surrogate(text)), language='')]
    )


def yaml_format(obj, indent=0, max_str_len=256, max_byte_len=64):
    """
    Pretty formats the given object as a YAML string which is returned.
    (based on TLObject.pretty_format)
    """
    result = []
    if isinstance(obj, TLObject):
        obj = obj.to_dict()

    if isinstance(obj, dict):
        if not obj:
            return 'dict:'
        items = obj.items()
        has_items = len(items) > 1
        has_multiple_items = len(items) > 2
        result.append(obj.get('_', 'dict') + (':' if has_items else ''))
        if has_multiple_items:
            result.append('\n')
            indent += 2
        for k, v in items:
            if k == '_' or v is None:
                continue
            formatted = yaml_format(v, indent)
            if not formatted.strip():
                continue
            result.append(' ' * (indent if has_multiple_items else 1))
            result.append(f'{k}:')
            if not formatted[0].isspace():
                result.append(' ')
            result.append(f'{formatted}')
            result.append('\n')
        if has_items:
            result.pop()
        if has_multiple_items:
            indent -= 2
    elif isinstance(obj, str):
        # truncate long strings and display elipsis
        result = repr(obj[:max_str_len])
        if len(obj) > max_str_len:
            result += '…'
        return result
    elif isinstance(obj, bytes):
        # repr() bytes if it's printable, hex like "FF EE BB" otherwise
        if all(0x20 <= c < 0x7f for c in obj):
            return repr(obj)
        else:
            return ('<…>' if len(obj) > max_byte_len else
                    ' '.join(f'{b:02X}' for b in obj))
    elif isinstance(obj, datetime.datetime):
        # ISO-8601 without timezone offset (telethon dates are always UTC)
        return obj.strftime('%Y-%m-%d %H:%M:%S')
    elif hasattr(obj, '__iter__'):
        # display iterables one after another at the base indentation level
        result.append('\n')
        indent += 2
        for x in obj:
            result.append(f"{' ' * indent}- {yaml_format(x, indent + 2)}")
            result.append('\n')
        result.pop()
        indent -= 2
    else:
        return repr(obj)

    return ''.join(result)


@borg.on(admin_cmd(pattern="yaml"))
async def _(event):
    if event.fwd_from:
        return
    the_real_message = None
    reply_to_id = None
    if event.reply_to_msg_id:
        event = await event.get_reply_message()
    # await event.delete()
    the_real_message = yaml_format(event)
    if len(the_real_message) > Config.MAX_MESSAGE_SIZE_LIMIT:
        with io.BytesIO(str.encode(the_real_message)) as out_file:
            out_file.name = "yaml.html"
            await event.reply(
                file=out_file,
                force_document=True,
            )
            # await event.delete()
    else:
        await event.reply(
            the_real_message,
            parse_mode=parse_pre
        )
