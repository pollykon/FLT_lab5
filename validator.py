class InvalidConfigData(Exception):
    pass


def validate_config(config):
    grammar = config['grammar']
    production = config['production']

    check_config_list(grammar, 'nonterminals_range')
    check_config_list(grammar, 'rules_for_nonterminal_range')

    check_config_bool(grammar, 'only_non_empty_nonterminals')
    check_config_bool(grammar, 'unreachable_nonterminals')
    check_config_bool(grammar, 'only_generating_nonterminals')

    if production['max_symbols'] <= 0:
        raise InvalidConfigData('max_symbols should be a positive number')


def check_config_bool(grammar, config_item):
    if not isinstance(grammar[config_item], bool):
        raise InvalidConfigData(config_item + ' should be boolean')


def check_config_list(grammar, config_item):
    if not isinstance(grammar[config_item], list):
        raise InvalidConfigData(config_item + ' should be list')
    if len(grammar[config_item]) != 2:
        raise InvalidConfigData('Length of ' + config_item + ' should be 2')
    if grammar[config_item][0] >= grammar[config_item][1]:
        raise InvalidConfigData('First number in ' + config_item + ' should be less than the second one')
