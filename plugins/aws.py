import jinja2

from plugin_loader import J2Filter, J2Global


def load_plugin(_j2_env: jinja2.Environment) -> list:
    return [
        J2Filter(function=aws_tag, name='aws_tag'),
        J2Global(function=aws_tag, name='aws_tag')
    ]


class TagsKeyNotFoundError(Exception):
    """Exception raised when the "Tags" key is not found in the AWS object."""

    def __init__(self, message, obj):
        self.obj = obj
        self.message = message
        super().__init__(message)


def aws_tag(aws_object: dict, tag_key: str, default='', no_tags_ok: bool = False) -> str:
    """Retrieve the tag from the given AWS object."""
    if 'Tags' not in aws_object:
        if no_tags_ok: return default
        raise TagsKeyNotFoundError(f'Unable to find "Tags" in the object: {aws_object}', aws_object)

    for tag in aws_object['Tags']:
        if tag['Key'] == tag_key:
            return tag['Value']
    return default
