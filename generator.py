import re
import random
import rstr

from cfg import CFG
from validator import Validator, LL1
from utils import read_config, input_config, Types


class Nonterminal:
	def __init__(self, config, name):
		self.name = name


class Generator:
	def __init__(self, config):
		self.config = config

	def _generate_random_params(self, config):
		self.nonterminals_number = random.randint(*config['grammar']['nonterminals_range'])

		# generate nonterminals
		self.nonterms = set()
		nterm_start = self.config['grammar']['start_nonterminal']
		self.nonterms.add(nterm_start)
		
		for i in range(self.nonterminals_number-1):
			self.nonterms.add(self.generate_nonterminal()['value'])

	def generate_grammar(self):
		self._generate_random_params(self.config)

		#
		rules = []
		for nterm in self.nonterms:
			rules.extend(self.generate_rules(nterm))

		return self.post_process(CFG(rules, config))

	def generate_rules(self, left_nterm):
		productions = []

		productions_number = random.randint(*config['grammar']['rules_for_nonterminal_range'])
		for i in range(productions_number):
			productions.append(self.generate_production())

		# chance for eps
		if random.random() < config['epsilon']['chance']:
			if len(productions) == config['grammar']['rules_for_nonterminal_range'][1]:
				productions[-1] = [self.generate_epsilon()]
			else:
				productions.append([self.generate_epsilon()])

		rules = [{"left": left_nterm, "right": production} for production in productions]
		return rules

	def generate_production(self, generate_nterms=True):
		symbols_number = random.randint(1, self.config['production']['max_symbols'])
		production = []
		for i in range(symbols_number):
			# 50% chance for nonterminal and 50% for terminal
			if generate_nterms and random.randint(0, 1):
				production.append(self.choose_nonterminal_from_existing())
			else:
				production.append(self.generate_terminal())
		return production

	def generate_random_generating_symbol(self, nterms_to_choose):
		if len(nterms_to_choose) == 0 or random.randint(0, 1):
			return self.generate_terminal()
		else:
			return {
				'type': Types.nterm,
				'value': random.choice(list(nterms_to_choose))
			}

	def choose_nonterminal_from_existing(self):
		return {
			'type': Types.nterm,
			'value': random.choice(list(self.nonterms))
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
		nterms_path = list(self.nonterms)
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
		return cfg, nterms_path

	def fix_generating(self, cfg, nterms_path=None):
		gen_nterms = cfg.find_generating_nterms()
		nterm2rules = cfg.get_nonterm_to_rule()

		# make last nterm in path generating
		if nterms_path is not None:
			last_nterm = nterms_path[-1]
			if last_nterm not in gen_nterms:
				# if we can add terminal production
				if len(nterm2rules[last_nterm]) < self.config['grammar']['rules_for_nonterminal_range'][1]:
					rule = {"left": last_nterm, "right": self.generate_production(generate_nterms=False)}
					cfg.add_rule(rule)
				else:
					rule_ind = random.choice(nterm2rules[last_nterm])
					for c in range(len(cfg.grammar[rule_ind]['right'])):
						elem = cfg.grammar[rule_ind]['right'][c]
						if elem['type'] == Types.nterm and elem['value'] not in gen_nterms:
							new_elem = self.generate_random_generating_symbol(gen_nterms)
							cfg.grammar[rule_ind]['right'][c] = new_elem


		gen_nterms = cfg.find_generating_nterms()
		nterm2rules = cfg.get_nonterm_to_rule()
		if nterms_path is not None:
			nterms_path_todo = nterms_path[-1][::-1]
		else:
			nterms_path_todo = list(cfg.nonterms)

		nterm_counter = 0
		while gen_nterms != cfg.nonterms and nterm_counter < len(nterms_path_todo):
			nterm = nterms_path_todo[nterm_counter]

			if nterm in gen_nterms:
				nterm_counter += 1
				continue

			rule_ind = random.choice(nterm2rules[nterm])
			for c in range(len(cfg.grammar[rule_ind]['right'])):
				elem = cfg.grammar[rule_ind]['right'][c]
				if elem['type'] == Types.nterm and elem['value'] not in gen_nterms:
					new_elem = self.generate_random_generating_symbol(gen_nterms)
					cfg.grammar[rule_ind]['right'][c] = new_elem

			gen_nterms = cfg.find_generating_nterms()
			nterm_counter += 1

		return cfg

	def post_process(self, cfg):
		# if all nterms should be reachable
		nterms_path = None
		if not self.config['grammar']['unreachable_nonterminals']:
			cfg, nterms_path = self.fix_reachable(cfg)

		if self.config['grammar']['only_generating_nonterminals']:
			cfg = self.fix_generating(cfg, nterms_path=nterms_path)

		return cfg


if __name__ == "__main__":
	config = input_config()

	val = Validator(config)
	val.validate_config()

	ll1 = LL1(config)
	ll1.check_ll1()

	gen = Generator(config)
	cfg = gen.generate_grammar()
	print(cfg)

	gen_nterms = cfg.find_generating_nterms()

	print('is generating:', gen_nterms==cfg.nonterms)
	print('all reachable:', cfg.is_all_rules_reachable()==cfg.nonterms)