import pathlib

import jinja2.ext
import jinja2.nodes
import jinja2.parser
import jinja2.utils

from plugin_loader import J2Extension


def load_plugin(_j2_env: jinja2.Environment):
    return [
        J2Extension(extension=NewFileExt)
    ]


class NewFileExt(jinja2.ext.Extension):
    tags = {"infile"}

    def __init__(self, environment: jinja2.Environment):
        super().__init__(environment)

    def parse(self, parser: jinja2.parser.Parser):
        def parse_arguments():
            d = parser.parse_expression()
            if parser.stream.skip_if("comma"):
                return d, parser.parse_expression()
            return d, None

        lineno = next(parser.stream).lineno
        destination, template_name = parse_arguments()

        if template_name:
            node = self.call_method("_render_template", [destination, template_name], lineno=lineno)
            return jinja2.nodes.CallBlock(node, [], [], [], lineno=lineno)

        body = parser.parse_statements(("name:endinfile",), drop_needle=True)
        node = self.call_method("_render_body", [destination], lineno=lineno)
        return jinja2.nodes.CallBlock(node, [], [], body, lineno=lineno)

    @jinja2.utils.pass_context
    def _render_template(self, context, destination, template_name, caller):
        template = self.environment.get_template(template_name)
        result = template.render(context.get_all())
        self._save(context, destination, result)
        return caller()

    @jinja2.utils.pass_context
    def _render_body(self, context, destination, caller):
        content = caller()
        self._save(context, destination, content)
        return ""

    def _save(self, context, destination: str, content: str):
        path = pathlib.Path(context.get('root_directory', '.') + '/') / destination
        if not path.parent.exists():
            path.parent.mkdir(exist_ok=True, parents=True)
        with open(path, 'w') as file:
            file.write(content)
