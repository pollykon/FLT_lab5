from utils import read_config
import re


class InvalidConfigData(Exception):
    pass

class NotLL1Grammar(Exception):
    pass


class Validator:
    def __init__(self, config):
        self.config = config

    def validate_config(self):
        self.check_is_user_config_full()

        grammar = self.config['grammar']
        production = self.config['production']
        epsilon = self.config['epsilon']

        self.check_config_list(grammar, 'nonterminals_range')
        self.check_config_list(grammar, 'rules_for_nonterminal_range')

        self.check_config_bool(grammar, 'only_non_empty_nonterminals')
        self.check_config_bool(grammar, 'unreachable_nonterminals')
        self.check_config_bool(grammar, 'only_generating_nonterminals')

        if production['max_symbols'] <= 0:
            raise InvalidConfigData('max_symbols should be a positive number')
        if epsilon['chance'] > 1:
            raise InvalidConfigData('chance should be less than 1')

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
        default_epsilon = list(default_config['epsilon'].keys())

        # "первый уровень" конфига
        defined_params = list(self.config.keys())

        # добавляем ключи при необходимости
        self.add_config(defined_params, default_params, default_config, '')

        # идем дальше по конфигу
        defined_grammar = list(self.config['grammar'].keys())
        defined_production = list(self.config['production'].keys())
        defined_terms = list(self.config['terminals'].keys())
        defined_nterms = list(self.config['nonterminals'].keys())
        defined_epsilon = list(self.config['epsilon'].keys())

        self.add_config(defined_grammar, default_grammar, default_config, 'grammar')
        self.add_config(defined_production, default_production, default_config, 'production')
        self.add_config(defined_terms, default_terms, default_config, 'terminals')
        self.add_config(defined_nterms, default_nterms, default_config, 'nonterminals')
        self.add_config(defined_epsilon, default_epsilon, default_config, 'value')

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


class LL1:
    def __init__(self, config):
        self.config = config

    def check_ll1(self):
        config = self.config
        nonterminal_end = config['nonterminals']['nonterminal_end']
        nonterminal_start = config['nonterminals']['nonterminal_start']

        if nonterminal_start == '' or nonterminal_end == '':
            raise NotLL1Grammar("For LL1 Grammar add nonempty nonterminal_start and nonterminal_end")
        if config['terminals']['regex'] == '':
            raise NotLL1Grammar("For LL1 Grammar add nonempty regex for terminals")
        if config['nonterminals']['regex'] == '':
            raise NotLL1Grammar("For LL1 Grammar add nonempty regex for nonterminals")

        term = re.compile(config['terminals']['regex'])
        nterm = re.compile(config['nonterminals']['regex'])
        if term.match(nonterminal_end) or term.match(nonterminal_start):
            raise NotLL1Grammar(
                "For LL1 Grammar nonterminal_start and nonterminal_end should be different from terminals")
        if nterm.match(nonterminal_end) or nterm.match(nonterminal_start):
            raise NotLL1Grammar(
                "For LL1 Grammar nonterminal_start and nonterminal_end should be different from nonterminals")

        epsilon = config['epsilon']['value']
        if epsilon == nonterminal_end or epsilon == nonterminal_start:
            raise NotLL1Grammar("For LL1 Grammar epsilon should be different from nonterminal_end and nonterminal_start")

        production_sep = config['grammar']['production_separator']
        if production_sep == '':
            raise NotLL1Grammar("For LL1 Grammar production_separator should be nonempty")
        if term.match(production_sep):
            raise NotLL1Grammar("For LL1 Grammar production_separator should be different from terminals")
        if production_sep == nonterminal_start:
            raise NotLL1Grammar("For LL1 Grammar production_separator should be different from nonterminal_start")

        rule_sep = config['grammar']['rule_separator']
        if rule_sep == '':
            raise NotLL1Grammar("For LL1 Grammar rule_separator should be nonempty")
        if production_sep == rule_sep:
            raise NotLL1Grammar("For LL1 Grammar rule_separator should be different from production_separator")
        if rule_sep == nonterminal_start or rule_sep == nonterminal_end:
            raise NotLL1Grammar(
                "For LL1 Grammar rule_separator should be different from nonterminal_end and nonterminal_start")
        if term.match(rule_sep):
            raise NotLL1Grammar("For LL1 Grammar rule_separator should be different from terminals")
