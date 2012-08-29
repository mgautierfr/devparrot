class InvalidToken(Exception):
	def __init__(self, token):
		Exception.__init__(self)
		self.token = token	
	
	def __str__(self):
		return "token %s is invalid"%self.token


class MissingToken(Exception):
	def __init__(self, constraint):
		Exception.__init__(self)
		self.constraint = constraint
	
	def __str__(self):
		return "missing a token for constraint %s"%self.constraint

class TokenParser(object):
	def __init__(self, constraints, askUser=False):
		self.constraints = list(constraints)
		self.status = 0
		self.askUser = askUser
	
	def init(self):
		self.currentConstraint = 0
		for constraint in self.constraints:
			constraint.init()
	
	def get_constraint(self):
		try:
			return self.constraints[self.currentConstraint]
		except IndexError:
			return None
	
	def all_constraints_validated(self):
		for constraint in self.constraints:
			if not constraint.is_consume():
				return False
		return True
	
	def get_tokens_from_constraints(self):
		for constraint in self.constraints:
			yield constraint.token
	
	def advance_constraints(self):
		constraint = self.constraints[self.currentConstraint]
		if constraint.close():
			self.currentConstraint += 1
		else:
			raise MissingToken(constraint)
	
	def close_remaining(self):
		for constraint in self.constraints[self.currentConstraint:]:
			constraint.close(self.askUser)
		
	def check_a_token(self, token):
		constraint = self.get_constraint()
		if constraint is None:
			raise InvalidToken(token)
		if not constraint.check_token(token):
			self.advance_constraints()
			self.check_a_token(token)
	
	def _parse(self, tokens):
		self.init()
		
		for token in tokens:
			self.check_a_token(token)
		
		self.close_remaining()
	
	def check(self, tokens):
		try:
			self._parse(tokens)
		except InvalidToken:
			return False
		except MissingToken:
			return False
		return self.all_constraints_validated()
		

	def parse(self, tokens):
		self._parse(tokens)
		return list(self.get_tokens_from_constraints())
