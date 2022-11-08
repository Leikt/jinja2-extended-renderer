import logging
import sys

from jinja2 import Environment, FileSystemLoader

from plugin_loader import PluginManager

DATA = {
    'instances': [
        {
            'InstanceId': '1234567879',
            'Tags': [
                {
                    'Key': 'Name',
                    'Value': 'desvaws3012'
                },
                {
                    'Key': 'Function',
                    'Value': 'Sandbox'
                }
            ]
        },
        {
            'InstanceId': '48965165133',
            'Tags': [
                {
                    'Key': 'Name',
                    'Value': 'desvaws3018'
                },
                {
                    'Key': 'Function',
                    'Value': 'Powerful!'
                }
            ]
        }
    ]
}


def main():
    logging.basicConfig(level=logging.CRITICAL, filename='logs/tests.log')
    logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))

    environment = Environment(loader=FileSystemLoader('templates/'))

    plugin_manager = PluginManager(logger=logging.getLogger(), j2_env=environment)
    plugin_manager.load_plugin('plugins.aws')
    plugin_manager.load_plugin('plugins.infile')

    template = environment.get_template('main.j2')
    logging.getLogger().debug('\n' + template.render(DATA))


if __name__ == "__main__":
    main()
