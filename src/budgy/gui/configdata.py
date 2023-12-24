import json
import os.path
from pathlib import Path

class BudgyConfig(object):
    def __init__(self, filepath:Path=None, configdir:Path=None):
        self._config_dict = None
        if configdir is None:
            configdir = Path('~/.config/budgy')
        else:
            configdir = Path(configdir)
        self._config_dir = configdir
        if filepath is None:
            filepath = Path(f'{self._config_dir}/budgyconfig.json')
        else:
            filepath = Path(filepath)
        self._filepath = filepath.expanduser()

        if not self._filepath.exists():
            self._create_default_file()

        self._load_config()

    @property
    def config_dict(self):
        return self._config_dict

    @property
    def import_data_path(self):
        return self.config_dict['import_data']['import_dir']

    @import_data_path.setter
    def import_data_path(self, new_path):
        print(f'Updating Import Data Path: {new_path}')
        if os.path.isfile(new_path):
            new_path = os.path.dirname(new_path)
        self.config_dict['import_data']['import_dir'] = new_path
        self.save_config()

    def save_config(self):
        self._filepath.parent.mkdir(exist_ok=True)
        with open(self._filepath, 'w') as configfile:
            configfile.write(json.dumps(self._config_dict, indent=4))
            configfile.write('\n')

    def _load_config(self):
        with open(self._filepath) as configfile:
            self._config_dict = json.loads(configfile.read())

    def _create_default_file(self):
        import_dir = Path('~/Downloads').expanduser()
        self._config_dict = {
            'database': {
                'path': f'{self._config_dir}/budgydata.db'
            },
            'import_data': {
                'import_dir': str(import_dir)
            }
        }
        self.save_config()

