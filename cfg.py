import copy
import itertools
import time

from utils import Types

class CFG:
	def __init__(self, parsed_grammar, config):
		self.grammar = parsed_grammar
		self.config = config
		#
		self.update_terms_and_nonterms()

	def fill_elements_from_rule(self, rule):
		left = rule['left']
		self.nonterms.add(left)
		for item in rule['right']:
			if item['type'] == Types.nterm:
				self.nonterms.add(item['value'])
			else:
				self.terms.add(item['value'])

	def update_terms_and_nonterms(self):
		self.nonterms = set()
		self.terms = set()
		for rule in self.grammar:
			self.fill_elements_from_rule(rule)

	def get_left_nonterminals(self):
		nonterms = set()
		for rule in self.grammar:
			nonterms.add(rule['left'])
		return nonterms

	def add_rule(self, rule):
		self.fill_elements_from_rule(rule)
		self.grammar.append(rule)

	def remove_rules(self, idx_to_remove):
		for idx in sorted(idx_to_remove, reverse=True):
			self.grammar.pop(idx)

	def rename_nonterminal(self, old_name, new_name):
		self.nonterms.remove(old_name)
		self.nonterms.add(new_name)
		for rule in self.grammar:
			if rule['left'] == old_name:
				rule['left'] = new_name
			for item in rule['right']:
				if item['type'] == Types.nterm and item['value'] == old_name:
					item['value'] = new_name

	def get_nonterm_to_rule(self):
		nonterm_to_rule = {}
		for c, rule in enumerate(self.grammar):
			left = rule['left']
			#
			if left in nonterm_to_rule:
				nonterm_to_rule[left].append(c)
			else:
				nonterm_to_rule[left] = [c]
		return nonterm_to_rule

	def is_generating_rule(self, rule, generating_nterms=set()):
		is_generating = True
		for item in rule['right']:
			if item['type'] == Types.nterm and item['value'] not in generating_nterms:
				is_generating = False
				break
		return is_generating

	def find_generating_nterms(self):
		generating_nterms = set()
		rules_to_skip = set()

		for c, rule in enumerate(self.grammar):
			left = rule['left']
			if self.is_generating_rule(rule):
				generating_nterms.add(left)
				rules_to_skip.add(c)

		changed = True
		while changed:
			changed = False
			for c, rule in enumerate(self.grammar):
				left = rule['left']
				if left not in generating_nterms:
					if c not in rules_to_skip and self.is_generating_rule(rule, generating_nterms):
						generating_nterms.add(left)
						rules_to_skip.add(c)
						changed = True

		return generating_nterms

	def is_all_rules_reachable(self):
		nterm2rules = self.get_nonterm_to_rule()
		stack = [self.config['grammar']['start_nonterminal']]
		visited = set()

		while len(stack)>0:
			nterm = stack.pop(0)
			visited.add(nterm)

			rules = nterm2rules[nterm]
			for i in rules:
				rule = self.grammar[i]
				for elem in rule['right']:
					if elem['type'] == Types.nterm and elem['value'] not in visited:
						visited.add(elem['value'])
						stack.append(elem['value'])
		return visited


	def __str__(self):
		nonterminal_start = self.config['nonterminals']['nonterminal_start']
		nonterminal_end = self.config['nonterminals']['nonterminal_end']
		arrow = self.config['grammar']['arrow']
		prod_sep = ' '+self.config['grammar']['production_separator']+' '
		rule_sep = self.config['grammar']['rule_separator'] + '\n'

		rules = []
		nonterm_to_rule = self.get_nonterm_to_rule()
		for nonterminal, rules_indexes in nonterm_to_rule.items():
			left = nonterminal_start + nonterminal + nonterminal_end
			productions = []
			for rule_ind in rules_indexes:
				production = ""
				for item in self.grammar[rule_ind]['right']:
					if item['type'] == Types.nterm:
						production += nonterminal_start + item['value'] + nonterminal_end
					else:
						if len(item['value']) == 0:
							production += str(self.config['epsilon']['value'])
						else:
							production += item['value']
				productions.append(production)
			rule_right = prod_sep.join(productions)
			rules.append(f"{left} {arrow} {rule_right}")
		return rule_sep.join(rules)+rule_sep