import re
import random
import rstr

from cfg import CFG
from validator import Validator, LL1
from utils import read_config, Types


class Nonterminal:
	def __init__(self, config, name):
		self.name = name


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
			nterm = Nonterminal(config, self.generate_nonterminal()['value'])
			self.nonterm_data[nterm.name] = nterm

	def generate_grammar(self):
		self._generate_random_params(self.config)

		#
		rules = []
		for nterm in self.nonterm_data.values():
			rules.extend(self.generate_rules(nterm))

		return self.post_process(CFG(rules, config))

	def generate_rules(self, left_nterm):
		productions = []

		productions_number = random.randint(*config['grammar']['rules_for_nonterminal_range'])
		for i in range(productions_number):
			productions.append(self.generate_production())

		# chance for eps
		if random.randint(0, 1):
			if len(productions) == config['grammar']['rules_for_nonterminal_range'][1]:
				productions[-1] = [self.generate_epsilon()]
			else:
				productions.append([self.generate_epsilon()])

		rules = [{"left": left_nterm.name, "right": production} for production in productions]
		return rules

	def generate_production(self):
		symbols_number = random.randint(1, self.config['production']['max_symbols'])
		production = []
		for i in range(symbols_number):
			# 50% chance for nonterminal and 50% for terminal
			if random.randint(0, 1):
				production.append(self.choose_nonterminal_from_existing())
			else:
				production.append(self.generate_terminal())
		return production

	def choose_nonterminal_from_existing(self):
		return {
			'type': Types.nterm,
			'value': random.choice(list(self.nonterm_data.values())).name
		}

	def generate_epsilon(self):
		return {
			'type': Types.term,
			'value': ''
		}

	def generate_terminal(self):
		return {
			'type': Types.term,
			'value': rstr.xeger(self.config['terminals']['regex'])[:self.config['terminals']['max_length']]
		}
		
	def generate_nonterminal(self):
		return {
			'type': Types.nterm,
			'value': rstr.xeger(self.config['nonterminals']['regex'])[:self.config['nonterminals']['max_length']]
		}

	def fix_reachable(self, cfg):
		nterms_path = list(self.nonterm_data.keys())
		nterms_path.remove(self.config['grammar']['start_nonterminal'])
		random.shuffle(nterms_path)
		nterms_path = [self.config['grammar']['start_nonterminal']] + nterms_path

		nterm2rule = cfg.get_nonterm_to_rule()
		# rename random nterm into next nterm in path
		for c in range(len(nterms_path)-1):
			rule_id = random.choice(nterm2rule[nterms_path[c]])
			# change random symbol
			rule = cfg.grammar[rule_id]
			random_symbol_ind = random.randint(0, len(rule['right'])-1)
			rule['right'][random_symbol_ind] = {
				'type': Types.nterm,
				'value': nterms_path[c+1]
			}
		return cfg

	def post_process(self, cfg):
		# if all nterms must be reachable
		if not self.config['grammar']['unreachable_nonterminals']:
			cfg = self.fix_reachable(cfg)

		return cfg



if __name__ == "__main__":
	config_path = "configs/test.yaml"
	config = read_config(config_path)

	val = Validator(config)
	val.validate_config()

	ll1 = LL1(config)
	ll1.check_ll1()

	gen = Generator(config)
	print(gen.generate_grammar())