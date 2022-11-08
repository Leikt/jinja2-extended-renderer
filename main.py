from jinja2 import Environment, FileSystemLoader

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

other_files = {}
environment: Environment


def separate_file(filename: str, template: str, context: dict) -> str:
    global environment
    template = environment.get_template(template)
    other_files[filename] = template.render(**context)
    return ""


def get_tag(aws_object: dict, tag_key: str, default='') -> str:
    for tag in aws_object['Tags']:
        if tag['Key'] == tag_key:
            return tag['Value']
    return default


def main():
    global environment
    environment = Environment(loader=FileSystemLoader('templates/'))
    environment.filters['get_tag'] = get_tag

    environment.globals['get_tag'] = get_tag
    environment.globals['separate_file'] = separate_file

    template = environment.get_template('main.j2')
    other_files['main.tf'] = template.render(**DATA)
    for fn, content in other_files.items():
        print(fn)
        print(content)
        print('---')


if __name__ == "__main__":
    main()
