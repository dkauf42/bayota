from datetime import datetime
import os
import shutil
import configparser

user_config_dir = os.path.expanduser("~") + "/.config/" + os.environ['USER']
user_config = user_config_dir + "/bayota_user_config.ini"

print('user_config is %s' % user_config)

default_output_dir = os.path.join(os.path.expanduser("~"), 'output')
default_graphics_dir = os.path.join(default_output_dir, 'graphics')
default_logging_dir = os.path.join(default_output_dir, 'logs')


def write_default_config():
    config = configparser.ConfigParser()

    config.add_section('output_directories')
    config['output_directories']['general'] = default_output_dir
    config['output_directories']['graphics'] = default_graphics_dir
    config['output_directories']['logs'] = default_logging_dir

    # config.add_section('settings')
    # config['settings']['logging'] = default_logging_dir

    with open("default_config.ini", 'w') as f:
        config.write(f)


def parse_config():
    if not os.path.isfile(user_config):
        os.makedirs(user_config_dir, exist_ok=True)
        shutil.copyfile("default_config.ini", user_config)

    config = configparser.ConfigParser()
    config.read(user_config)
    return config


def get_output_dir():
    outputdir_top_level = parse_config()['output_directories']['general']
    print('outputdir_top_level is %s' % user_config)

    # # Output Path
    # today = datetime.now()
    # if today.hour < 12:
    #     h = "00"
    # else:
    #     h = "12"
    # dirname = os.path.join(outputdir_top_level, 'temp_bayota_out_' + today.strftime('%Y%m%d') + h)
    os.makedirs(outputdir_top_level, exist_ok=True)
    return outputdir_top_level


def get_graphics_dir():
    graphics_dir = parse_config()['output_directories']['graphics']

    # dirname = os.path.join(graphics_dir, 'temp_bayota_out_' + today.strftime('%Y%m%d') + h)
    os.makedirs(graphics_dir, exist_ok=True)
    return graphics_dir


def get_logging_dir():
    logging_dir = parse_config()['output_directories']['logs']

    # dirname = os.path.join(logging_dir, 'temp_bayota_out_' + today.strftime('%Y%m%d') + h)
    os.makedirs(logging_dir, exist_ok=True)
    return logging_dir
