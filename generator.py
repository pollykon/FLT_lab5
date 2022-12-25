import re
import yaml
import random

def read_config(filepath):
	with open(filepath, 'rt') as f:
		config = yaml.full_load(f.read())
	return config


class Generator:
	def __init__(self, config):
		self.config = config
		self.nonterm_data = {}

		self._generate_random_params(self.config)

	def _generate_random_params(self, config):
		# TODO проверки при генерации рандомных параметров
		# например число правил должно быть >= числу нетерминалов если 
		# отключена генерация недостижимых 
		self.nonterminals_number = random.randint(*config['grammar']['nonterminals_range'])

	def generate_grammar(self):
		rules = []

		for i in range(self.nonterminals_number):
			rules.append(self.generate_rule())

		sep = self.config['grammar']['rule_separator']
		return sep.join(rules)+sep

	def generate_rule(self):
		# TODO учитывать nonterminals_number
		left = self.generate_nonterminal()
		arrow = self.config['grammar']['arrow']

		productions = []

		productions_number = random.randint(*config['grammar']['rules_for_nonterminal_range'])
		for i in range(productions_number):
			productions.append(self.generate_production())

		sep = ' '+self.config['grammar']['production_separator']+' '
		productions_str = sep.join(productions)
		return f"{left} {arrow} {productions_str}" 

	def generate_production(self):
		symbols_number = random.randint(1, self.config['production']['max_symbols'])
		production = ""
		for i in range(symbols_number):
			# 50% chance for nonterminal and 50% for terminal
			if random.randint(0, 1):
				production += self.generate_nonterminal()
			else:
				production += self.generate_terminal()
		return production

	def generate_terminal(self):
		# TODO add terminal generation from config
		return "a"
		
	def generate_nonterminal(self):
		# TODO add nonterminal generation from config
		return "["+"NT"+"]"


if __name__ == "__main__":
	config_path = "configs/default.yaml"
	config = read_config(config_path)
	print(config)

	gen = Generator(config)
	print(gen.generate_grammar())