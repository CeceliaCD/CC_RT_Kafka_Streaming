import yaml

def yaml_kafka_host_loader(file_path):
    with open(file_path, 'r') as file:
        yf_config = yaml.load(file, Loader=yaml.FullLoader)

    kafka_envs = yf_config['services']['kafka']['environment']
    for env in kafka_envs:
        if env.startswith('KAFKA_CFG_ADVERTISED_LISTENERS='):
            list_of_hosts = env.split('=', 1)[1]
            host = list_of_hosts.split('/')[-1]
            return host
    return None
