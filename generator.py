import re
import random
import rstr
from validator import Validator, LL1
from utils import read_config


class Nonterminal:
	def __init__(self, config, value=None, name=None):
		if value is not None:
			self.name = self._get_name(value, config)
		else:
			self.name = name
		self.config = config

	def _get_name(self, value, config):
		return value[len(config['nonterminals']['nonterminal_start']):-len(config['nonterminals']['nonterminal_end'])]

	def value(self):
		nonterminal_start = self.config['nonterminals']['nonterminal_start']
		nonterminal_end = self.config['nonterminals']['nonterminal_end']
		return nonterminal_start + self.name + nonterminal_end

	def __str__(self):
		return self.value()


class Generator:
	def __init__(self, config):
		self.config = config

	def _generate_random_params(self, config):
		self.nonterminals_number = random.randint(*config['grammar']['nonterminals_range'])

		# generate nonterminals
		self.nonterm_data = {}
		nterm_start = Nonterminal(config, name=self.config['grammar']['start_nonterminal'])
		self.nonterm_data[nterm_start.name] = nterm_start
		
		for i in range(self.nonterminals_number-1):
			nterm = Nonterminal(config, value=self.generate_nonterminal())
			self.nonterm_data[nterm.name] = nterm

	def generate_grammar(self):
		self._generate_random_params(self.config)

		#
		rules = []
		for nterm in self.nonterm_data.values():
			rules.append(self.generate_rule(nterm))

		sep = self.config['grammar']['rule_separator'] + '\n'
		return sep.join(rules)+sep

	def generate_rule(self, left_nterm):
		# TODO учитывать nonterminals_number
		arrow = self.config['grammar']['arrow']

		productions = []

		productions_number = random.randint(*config['grammar']['rules_for_nonterminal_range'])
		for i in range(productions_number):
			productions.append(self.generate_production())

		if random.randint(0, 1):
			productions.append(self.generate_epsilon())

		sep = ' '+self.config['grammar']['production_separator']+' '
		productions_str = sep.join(productions)
		return f"{left_nterm.value()} {arrow} {productions_str}" 

	def generate_production(self):
		symbols_number = random.randint(1, self.config['production']['max_symbols'])
		production = ""
		for i in range(symbols_number):
			# 50% chance for nonterminal and 50% for terminal
			if random.randint(0, 1):
				production += self.choose_nonterminal_from_existing()
			else:
				production += self.generate_terminal()
		return production

	def choose_nonterminal_from_existing(self):
		return random.choice(list(self.nonterm_data.values())).value()

	def generate_epsilon(self):
		return config['grammar']['epsilon']

	def generate_terminal(self):
		term = rstr.xeger(self.config['terminals']['regex'])[:config['terminals']['max_length']]
		if term == config['grammar']['epsilon']:
			self.generate_terminal()
		return term
		
	def generate_nonterminal(self):
		nonterminal_start = self.config['nonterminals']['nonterminal_start']
		nonterminal_end = self.config['nonterminals']['nonterminal_end']

		nonterminal = rstr.xeger(self.config['nonterminals']['regex'])[:config['nonterminals']['max_length']]
		if nonterminal == config['grammar']['epsilon']:
			self.generate_nonterminal()
		return nonterminal_start + nonterminal + nonterminal_end


if __name__ == "__main__":
	config_path = "configs/test.yaml"
	config = read_config(config_path)

	val = Validator(config)
	val.validate_config()

	ll1 = LL1(config)
	ll1.check_ll1()

	gen = Generator(config)
	print(gen.generate_grammar())