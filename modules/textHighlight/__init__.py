

def activate():
	import core.controler
	core.controler.eventSystem.connect("newDocument",on_new_document)
	pass

def deactivate():
	pass


def on_new_document(document):
	document.models['text'].connect('insert', on_insert)
	document.models['text'].connect('delete', on_delete)
	pass

def on_insert(model, insertMark, text):
	update_highlight(model, insertMark)

def on_delete(model, fromMark, toMark):
	update_highlight(model, fromMark)


def update_highlight(self, insertPoint):

	def find_startPoint(self, index):
		def find_previous(self, index):
			previous = self.mark_previous(index)
			while previous and (not previous.startswith("DP::SH::_synctx_") or not self.compare(previous, "<", index)):
				previous = self.mark_previous(previous)
			return previous
		previous =  find_previous(self, index)
		if previous:
			return find_previous(self, previous) or "1.0"
		return "1.0"
		
	def find_next(self, index):
		next = self.mark_next(index)
		while next and (not next.startswith("DP::SH::_synctx_") or not self.compare(next, ">", index)):
			next = self.mark_next(next)
		return next or "end"
	
		
	def stop_at_syncPoint(self, tokens, startPoint, insertPoint):
		from pygments.token import _ContextToken
		syncPoint = self.index(find_next(self, insertPoint))
		distance = self.calcule_distance(startPoint, syncPoint)
		for i,t,v in tokens:
			if v:
				currentPos = "%s + %d c"%(startPoint, i)
				if isinstance(t,_ContextToken) and t[1]:
					while i > distance:
						next = find_next(self, syncPoint)
						distance += self.calcule_distance(syncPoint, next)
						syncPoint = self.index(next)
					if i == distance and self.compare(self.last_stopToken, "<=", currentPos) :
						raise StopIteration
					yield i,t,v,True
				else:
					yield i,t,v,False

	start = self.index(find_startPoint(self,insertPoint))
	content = self.get(start,"end")
	tokens = self.lexer.get_tokens_unprocessed(content)
	tokens = stop_at_syncPoint(self, tokens, start, insertPoint)
	self.colorizeContext = [tokens, start, start]
	#self._update_a_token(realTime=True)
	self.after_idle(lambda s=self: _update_a_token(s))
	
def _update_a_token(self,realTime=False):
	prefix = "DP::SH::"
	markoff = self.mark_unset
	tagdel = self.tag_remove
	tagadd = self.tag_add
	
	def markon(pos):
		self.mark_set("DP::SH::_synctx_%d"%self.markNb, pos)
		self.markNb += 1
	
	def process_itvs(elem):
		i,t,v,s = elem
		token_name = "DP::SH::%s"%str(t).replace('.','_')
		token = (self.colorizeContext[2],
			 self.index("%s+%dc"%(self.colorizeContext[2],len(v)))
			)

		self.colorizeContext[2] = token[1]
		context = {
			"tags" : set([token_name]) if token_name != "DP::SH::Token_Text" else set(),
			"mark" : None,
			"openedPos" : None
		}
		
		def process_dump(ctx, key, name, pos):
			if name[:8] == prefix:
				def first_mark():
					if pos==token[0]:
						ctx['mark'] = {'name':name, 'pos':pos}
					else:
						markoff(name)	
					markf = other_mark
				def other_mark():
					markoff(name)
				markf = first_mark if s else other_mark
							
				if key == 'mark':
					markf()
				if key == 'tagon':
					if name != token_name:
						ctx['tags'].add(name)
					else:
						ctx['openedPos'] = pos
				if key == 'tagoff' and pos != token[0]:
					if name != token_name:
						ctx['tags'].add(name)
					elif (ctx['openedPos'],pos) == token:
						ctx['tags'].remove(token_name)
						ctx['openedPos'] = None

		[process_dump(context,"tagon",n,token[0]) for n in self.tag_names(token[0])]
		map(lambda item : process_dump(context, *item), self.dump(*token, mark=True, tag=True))
		
		tags = context["tags"]
		mark = context["mark"]
		openedPos = context["openedPos"]

		if s and not mark:
			self.mark_set("DP::SH::_synctx_%d"%self.markNb, token[0])
			self.markNb += 1			
			#if token_name in tags and len(tags[token_name]) == 1 and \
		#	tags[token_name][0] ==  token:
		#		del tags[token_name]
		#else:
	
		def filter_(name, tl):
			return name == token_name and len(tl)==1 and tl[0]==token

		for name in tags:
			if name == token_name:
				tagadd(token_name, *token)
			else:
				tagdel(name, *token)

		if self.last_stopToken < token[1]:
			self.last_stopToken = token[1]
	
	if self.colorizeContext:
		tokens = self.colorizeContext[0]
		startPoint = self.colorizeContext[1]
	else:
		return

	if realTime:
		map(process_itvs, tokens)
		self.last_stopToken = "1.0"
	else:
		try :
			process_itvs(tokens.next())
			self.after_idle(lambda s=self: _update_a_token(s))

		except StopIteration:
			self.last_stopToken = "1.0"
			pass

