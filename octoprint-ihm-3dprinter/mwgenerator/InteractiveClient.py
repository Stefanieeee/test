from PyInquirer import prompt
from hpg.Client import Client
from pyfiglet import Figlet
import logging

"""交互界面显示温度 功率等信息
"""

configure_network = [
    {'type': 'input', 'name': 'host', 'message': 'Device network host', 'default': '127.0.0.1'},
    {'type': 'input', 'name': 'port', 'message': 'Device network port', 'default': '5025'},
]

loglevel_choice = {
    'type': 'list', 'name': 'loglevel', 'message': 'Set the loglevel',
    'choices': ['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG']
}

preset_id_question = {'type': 'input', 'name': 'id', 'message': 'Preset ID'}
preset_name_question = {'type': 'input', 'name': 'name', 'message': 'Preset name'}


def root_menu_loop():

    while True:

        root_menu = {'type': 'list', 'name': 'root', 'message': 'What do you want to do?'}

        if client.is_available:

            root_menu['choices'] = ['Configure', 'Run', 'Status', 'Exit']

        else:

            root_menu['choices'] = ['Configure', 'Exit']

        choice = prompt([root_menu])['root']

        if choice == 'Exit':

            break

        elif choice == 'Configure':

            configure_menu_loop()

        elif choice == 'Run':

            run_menu_loop()

        elif choice == 'Status':

            show_device_status()


def show_device_status():

    print(f'Ontime: \t\t{client.ontime}ns')
    print(f'Offtime: \t\t{client.offtime}ns')
    print(f'Power: \t\t\t{client.power}10W')
    print(f'Frequency: \t\t{client.frequency}Hz')
    print(f'Connected to \t\t{client.host}:{client.port}')
    print(f'Serial number \t\t{client.serial}')
    print(f'Firmware \t\t{client.version}')
    print(f'ID \t\t\t{client.id}')
    print('---')
    print(f'Temperature \t\t{client.temperature}°C')
    print(f'Power reflected \t{client.power_reflected}W')
    print(f'Power forward \t\t{client.power_forward}W')


def preset_menu_loop():

    preset_menu = {'type': 'list', 'name': 'preset', 'message': 'Select action'}
    preset_menu_base = ['New', 'Return']

    while True:

        if len(client.preset_list()):

            preset_menu['choices'] = ['List', 'Load', 'Update', 'Delete'] + preset_menu_base

        else:

            preset_menu['choices'] = preset_menu_base

        choice = prompt([preset_menu])['preset']

        if choice == 'List':

            for preset in client.preset_list():

                id, name = preset.doc_id, preset['_preset_name']
                print(f'{id} - {name}')

        if choice in ['Load', 'Update', 'Delete']:

            selection = {'type': 'list', 'name': 'id', 'message': 'Preset ID', 'choices': []}

            for preset in client.preset_list():

                id, name = preset.doc_id, preset['_preset_name']
                selection['choices'] += [f'{id} - {name}']

            preset_id = int(prompt(selection)['id'].split(' ')[0])

            if choice == 'Load':

                client.preset_load(preset_id)

            if choice == 'Update':

                client.preset_save(preset_id)

            if choice == 'Delete':

                client.preset_delete(preset_id)

        if choice == 'New':

            name = prompt([preset_name_question])['name']
            client.preset_save(None, name)

        if choice == 'Return':

            break


def configure_menu_loop():

    configure_menu = {'type': 'list', 'name': 'configure', 'message': 'What do you want to do?'}
    configure_menu_base = ['Network', 'Loglevel', 'Return']

    while True:

        configure_menu['choices'] = []

        if client.is_available:

            configure_menu['choices'] += ['Unlock'] if client.locked else ['Lock']

            # if not client.locked:
            if True:

                configure_menu['choices'] += ['Limits', 'Presets']

        configure_menu['choices'] += configure_menu_base
        choice = prompt([configure_menu])['configure']
        # Configure the network connection

        if choice == 'Network':

            connection_settings = prompt(configure_network)
            client.update_settings({'connection': connection_settings})

        # Configure the log level
        if choice == 'Loglevel':

            loglevel = prompt([loglevel_choice])['loglevel']
            client.logger.setLevel(getattr(logging, loglevel))
        # Configure the presets

        if choice == 'Presets':

            preset_menu_loop()

        if choice == 'Lock':

            client.lock()

        if choice == 'Unlock':

            client.unlock()

        if choice == 'Return':

            break


def run_menu_loop():

    # run_menu = {'type': 'list', 'name': 'run', 'message': 'Choose action'}
    # run_params = ['Ontime', 'Offtime', 'Frequency', 'Power']
    pass


if __name__ == '__main__':

    figlet = Figlet(font='slant')
    print()
    print(figlet.renderText('HPG CLI'))
    client = Client()
    root_menu_loop()
