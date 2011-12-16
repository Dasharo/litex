from .structure import *

class Namespace:
	def __init__(self):
		self.counts = {}
		self.sigs = {}
	
	def get_name(self, sig):
		try:
			n = self.sigs[sig]
			if n:
				return sig.name + "_" + str(n)
			else:
				return sig.name
		except KeyError:
			try:
				n = self.counts[sig.name]
			except KeyError:
				n = 0
			self.sigs[sig] = n
			self.counts[sig.name] = n + 1
			if n:
				return sig.name + "_" + str(n)
			else:
				return sig.name

def list_signals(node):
	if isinstance(node, Constant):
		return set()
	elif isinstance(node, Signal):
		return {node}
	elif isinstance(node, Operator):
		l = list(map(list_signals, node.operands))
		return set().union(*l)
	elif isinstance(node, Slice):
		return list_signals(node.value)
	elif isinstance(node, Cat):
		l = list(map(list_signals, node.l))
		return set().union(*l)
	elif isinstance(node, Replicate):
		return list_signals(node.v)
	elif isinstance(node, Assign):
		return list_signals(node.l) | list_signals(node.r)
	elif isinstance(node, StatementList):
		l = list(map(list_signals, node.l))
		return set().union(*l)
	elif isinstance(node, If):
		return list_signals(node.cond) | list_signals(node.t) | list_signals(node.f)
	elif isinstance(node, Case):
		l = list(map(lambda x: list_signals(x[1]), node.cases))
		return list_signals(node.test).union(*l).union(list_signals(node.default))
	elif isinstance(node, Fragment):
		return list_signals(node.comb) | list_signals(node.sync)
	else:
		raise TypeError

def list_targets(node):
	if isinstance(node, Signal):
		return {node}
	elif isinstance(node, Slice):
		return list_targets(node.value)
	elif isinstance(node, Cat):
		l = list(map(list_targets, node.l))
		return set().union(*l)
	elif isinstance(node, Replicate):
		return list_targets(node.v)
	elif isinstance(node, Assign):
		return list_targets(node.l)
	elif isinstance(node, StatementList):
		l = list(map(list_targets, node.l))
		return set().union(*l)
	elif isinstance(node, If):
		return list_targets(node.t) | list_targets(node.f)
	elif isinstance(node, Case):
		l = list(map(lambda x: list_targets(x[1]), node.cases))
		return list_targets(node.default).union(*l)
	elif isinstance(node, Fragment):
		return list_targets(node.comb) | list_targets(node.sync)
	else:
		raise TypeError

def list_inst_outs(i):
	if isinstance(i, Fragment):
		return list_inst_outs(i.instances)
	else:
		l = []
		for x in i:
			l += list(map(lambda x: x[1], list(x.outs.items())))
		return set(l)

def is_variable(node):
	if isinstance(node, Signal):
		return node.variable
	elif isinstance(node, Slice):
		return is_variable(node.value)
	elif isinstance(node, Cat):
		arevars = list(map(is_variable, node.l))
		r = arevars[0]
		for x in arevars:
			if x != r:
				raise TypeError
		return r
	else:
		raise TypeError

def insert_reset(rst, sl):
	targets = list_targets(sl)
	resetcode = []
	for t in targets:
		resetcode.append(Assign(t, t.reset))
	return If(rst, resetcode, sl)
