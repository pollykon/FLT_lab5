from utils import read_config


class InvalidConfigData(Exception):
    pass

class Validate:
    def __init__(self, config):
        self.config = config

    def validate_config(self):
        self.check_is_user_config_full()

        grammar = self.config['grammar']
        production = self.config['production']

        self.check_config_list(grammar, 'nonterminals_range')
        self.check_config_list(grammar, 'rules_for_nonterminal_range')

        self.check_config_bool(grammar, 'only_non_empty_nonterminals')
        self.check_config_bool(grammar, 'unreachable_nonterminals')
        self.check_config_bool(grammar, 'only_generating_nonterminals')

        if production['max_symbols'] <= 0:
            raise InvalidConfigData('max_symbols should be a positive number')

    def check_config_bool(self, grammar, config_item):
        if not isinstance(grammar[config_item], bool):
            raise InvalidConfigData(config_item + ' should be boolean')

    def check_config_list(self, grammar, config_item):
        if not isinstance(grammar[config_item], list):
            raise InvalidConfigData(config_item + ' should be list')
        if len(grammar[config_item]) != 2:
            raise InvalidConfigData('Length of ' + config_item + ' should be 2')
        if grammar[config_item][0] >= grammar[config_item][1]:
            raise InvalidConfigData('First number in ' + config_item + ' should be less than the second one')

    def check_is_user_config_full(self):
        # нам нужно, чтобы ключи из дефолтного конфига совпадали с пользовательским
        default_config = read_config('configs/default.yaml')

        # дефолтные ключи
        default_params = list(default_config.keys())
        default_grammar = list(default_config['grammar'].keys())
        default_production = list(default_config['production'].keys())
        default_terms = list(default_config['terminals'].keys())
        default_nterms = list(default_config['nonterminals'].keys())

        # "первый уровень" конфига
        defined_params = list(self.config.keys())

        # добавляем ключи при необходимости
        self.add_config(defined_params, default_params, default_config, '')

        # идем дальше по конфигу
        defined_grammar = list(self.config['grammar'].keys())
        defined_production = list(self.config['production'].keys())
        defined_terms = list(self.config['terminals'].keys())
        defined_nterms = list(self.config['nonterminals'].keys())

        self.add_config(defined_grammar, default_grammar, default_config, 'grammar')
        self.add_config(defined_production, default_production, default_config, 'production')
        self.add_config(defined_terms, default_terms, default_config, 'terminals')
        self.add_config(defined_nterms, default_nterms, default_config, 'nonterminals')

    def add_config(self, defined_params, default_params, default_config, key):
        sorted_defined_params = sorted(defined_params)
        sorted_default_params = sorted(default_params)
        if sorted_defined_params != sorted_default_params:
            lacking_params = set(default_params) - set(defined_params)
            for lacking_param in lacking_params:
                if key == '':
                    self.config[lacking_param] = default_config[lacking_param]
                else:
                    self.config[key][lacking_param] = default_config[key][lacking_param]
