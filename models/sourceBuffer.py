#    This file is part of DevParrot.
#
#    Author: Matthieu Gautier <matthieu.gautier@mgautier.fr>
#
#    DevParrot is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    DevParrot is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with DevParrot.  If not, see <http://www.gnu.org/licenses/>.
#
#
#    Copyright 2011 Matthieu Gautier

import ttk

import core.config
import core.mainWindow
from time import time

import tkFont

import Tkinter

PREFIX = "tkController"

class Controller(object):
   def __init__(self, master=None):
      if master is None:
         master = Tkinter._default_root
      assert master is not None
      self.tag = PREFIX + str(id(self))
      def bind(event, handler):
         master.bind_class(self.tag, event, handler)
      self.create(bind)

   def install(self, widget):
      widgetclass = widget.winfo_class()
      # remove widget class bindings and other controllers
      tags = [self.tag]
      for tag in widget.bindtags():
         if tag != widgetclass and tag[:len(PREFIX)] != PREFIX:
            tags.append(tag)
      widget.bindtags(tuple(tags))

   def create(self, handle):
      # override if necessary
      # the default implementation looks for decorated methods
      for key in dir(self):
         method = getattr(self, key)
         if hasattr(method, "tkevent") and callable(method):
            for eventSequence in method.tkevent:
               handle(eventSequence, method)

def bind(*events):
   def decorator(func):
      func.tkevent = events
      return func
   return decorator

class KBController( Controller ):
	'''This class watches keypress events and records presses and releases of 
	keys used for key combinations (shift, alt, control, etc.).  When one of
	these keys is held down, this class's corresponding state variable is set
	to True.'''
	def __init__( self ):
		Controller.__init__( self )
		self._alt     = False
		self._control = False
		self._lock    = False
		self._meta    = False
		self._shift   = False
   
	@bind("<KeyPress>")      # type 2
	def KeyPress(self, event):
		if event.keysym in ('Alt_L', 'Alt_R'):
			self._alt = True
		elif event.keysym in ('Control_L', 'Control_R'):
			self._control = True
		elif event.keysym == 'Caps_Lock':
			self._lock = True
		elif event.keysym in ('Meta_L', 'Meta_R'):
			self._meta = True
		elif event.keysym in ( 'Shift_L', 'Shift_R'):
			self._shift = True
		elif (len(event.char) > 0) and (32 <= ord(event.char) < 127):
			self.onTypedCharacterKey( event )
		else:
			self.onTypedSpecialKey( event )

	@bind("<KeyRelease>")   # type 3
	def KeyRelease( self, event ):
		if event.keysym in ('Alt_L', 'Alt_R'):
			self._alt = False
		elif event.keysym in ('Control_L', 'Control_R'):
			self._control = False
		elif event.keysym == 'Caps_Lock':
			self._lock = False
		elif event.keysym in ('Meta_L', 'Meta_R'):
			self._meta = False
		elif event.keysym in ('Shift_L', 'Shift_R'):
			self._shift = False
   
	def onTypedCharacterKey( self, event ):
		'''Override to handle typing of any printable keyboard character,
		The typed character is in event.char (which accounts for shift).'''
		pass
   
	def onTypedSpecialKey( self, event ):
		'''Override to handle typing of any special characters (tab, \n, backspace,
		delete, home, prior, insert, etc.  And any key combinations involving
		Alt or Control.'''
		pass


class EnhancedTextController( KBController ):
   def __init__( self ):
      KBController.__init__( self )
      self._insert_x_pos    = None
   
   def onTypedCharacterKey( self, event ):
      try:
         event.widget.sel_delete( )
      except:
         pass
      
      event.widget.insert( 'insert', event.char )
      event.widget.sel_clear( )
      
      self._insert_x_pos = event.widget.bbox( 'insert' )[0]
   
   def moveCarrot( self, event ):
      widget = event.widget
      
      if self._shift:
         if not widget.sel_isAnchorSet():
            widget.sel_setAnchor( 'insert' )
      else:
         widget.sel_clear( )
      
      if event.keysym in ( 'Home', 'KP_Home' ):
         if self._control:
            # Move to beginning of text
            widget.mark_set( 'insert', '1.0' )
         else:
            # Move to front of line
            widget.mark_set( 'insert', 'insert linestart' )
      elif event.keysym in ( 'End', 'KP_End' ):
         if self._control:
            # Move to end of text
            widget.mark_set( 'insert', 'end' )
         else:
            # Move to end of line
            widget.mark_set( 'insert', 'insert lineend' )
      elif event.keysym == 'Right':
         if self._control:
            # Move by word
            currentPos = widget.index( 'insert' )
            maxPos     = widget.index( 'end wordstart' )
            
            if currentPos == maxPos:
               return
            
            offset = 1
            while widget.compare( currentPos, '==', widget.index('insert') ):
               widget.mark_set( 'insert', 'insert wordend +%dc wordstart' % offset )
               offset += 1
         else:
            # Move by character
            widget.mark_set( 'insert', 'insert +1 chars' )
      elif event.keysym == 'Left':
         if self._control:
            # Move by word
            currentPos = widget.index( 'insert' )
            minPos     = widget.index( '1.0 wordstart' )
            
            if currentPos == minPos:
               return
            
            offset = 2
            widget.mark_set( 'insert', 'insert wordstart' )
            while widget.compare( currentPos, '==', widget.index('insert') ):
               widget.mark_set( 'insert', 'insert -%dc wordstart' % offset )
               offset += 1
         else:
            # Move by character
            widget.mark_set( 'insert', 'insert -1 chars' )
      elif event.keysym == 'Down':
            widget.mark_set( 'insert', 'insert +1 lines' )
      elif event.keysym == 'Up':
            widget.mark_set( 'insert', 'insert -1 lines' )
      elif event.keysym == 'Prior':
         if self._control:
            pass
         else:
            # Move by page
            event.widget.yview_scroll( -1, 'pages' )
      elif event.keysym == 'Next':
         if self._control:
            pass
         else:
            # Move by page
            event.widget.yview_scroll( 1, 'pages' )
      
      widget.see( 'insert' )
      
      if event.keysym not in ('Up','Down'):
         self._insert_x_pos = event.widget.bbox( 'insert' )[0]

   def typeSpecial( self, event ):
      widget = event.widget
      
      if event.keysym in ( 'Return', 'Enter', 'KP_Enter' ):
         try:
            widget.sel_delete( )
         finally:
            widget.insert( 'insert', '\n' )
      elif event.keysym == 'Tab':
         widget.insert( 'insert', '\t' )
      elif event.keysym == 'BackSpace':
         try:
            widget.delete( 'sel.first', 'sel.last' )
         except:
            widget.delete( 'insert -1 chars', 'insert' )
      elif event.keysym in ( 'Delete', 'KP_Delete' ):
         try:
            widget.delete( 'sel.first', 'sel.last' )
         except:
            widget.delete( 'insert', 'insert +1 chars' )
      
      widget.sel_clear()
      self._insert_x_pos = event.widget.bbox( 'insert' )[0]

   def onTypedSpecialKey( self, event ):
      widget = event.widget
      
      if event.keysym in ( 'Return','Enter','KP_Enter','Tab','BackSpace','Delete','Insert' ):
         self.typeSpecial( event )
      
      elif event.keysym in ( 'Up', 'Down', 'Left', 'Right', 'Home', 'End', 'Prior', 'Next'
                             'KP_Up', 'KP_Down', 'KP_Left', 'KP_Right', 'KP_Home', 'KP_End', 'KP_Prior', 'KP_Next' ):
         self.moveCarrot( event )
      
      elif self._control:
         if event.keysym == 'a':
            # select all
            self._selectionAnchor = '1.0'
            widget.mark_set( 'insert', 'end' )
         elif event.keysym == 'c':
            # copy
            try:
               widget.clipboard_append( widget.get( 'sel.first', 'sel.last' ) )
            except:
               pass
         elif event.keysym == 'r':
            # Redo
            try:
               widget.edit_redo( )
            except:
               pass
            widget.sel_clear( )
         elif event.keysym == 'v':
            # paste
            try:
               widget.mark_set( 'insert', 'sel.first' )
               widget.delete( 'sel.first', 'sel.last' )
            except:
               pass
            
            widget.insert( 'insert', widget.clipboard_get( ) )
            self.sel_clear( )
         elif event.keysym == 'x':
            # cut
            try:
               widget.clipboard_append( widget.get( 'sel.first', 'sel.last' ) )
               widget.delete( 'sel.first', 'sel.last' )
               widget.ins_updateTags( )
            except:
               pass
            widget.sel_clear( )
         elif event.keysym == 'z':
            # Undo
            try:
               widget.edit_undo( )
            except:
               pass
            widget.sel_clear( )
         
         self._insert_x_pos = event.widget.bbox( 'insert' )[0]

   @bind( '<ButtonPress-1>' )
   def click( self, event ):
      event.widget.focus_set( )
      
      if not self._shift and not self._control:
         event.widget.sel_clear( )
         event.widget.sel_setAnchor( 'current' )
      
      self._insert_x_pos = event.x
   
   @bind( '<B1-Motion>', '<Shift-Button1-Motion>' )
   def dragSelection( self, event ):
      widget = event.widget
      
      if event.y < 0:
         widget.yview_scroll( -1, 'units' )
      elif event.y >= widget.winfo_height():
         widget.yview_scroll( 1, 'units' )
      
      if not widget.sel_isAnchorSet( ):
         widget.self_setAnchor( '@%d,%d' % (event.x+2, event.y) )
      
      widget.mark_set( 'insert', '@%d,%d' % (event.x+2, event.y) )
      self._insert_x_pos = event.x
   
   @bind( '<ButtonRelease-1>' )
   def moveCarrot_deselect( self, event ):
      widget = event.widget
      
      widget.grab_release()
      widget.mark_set( 'insert', 'current' )
      self._insert_x_pos = event.x
   
   @bind( '<Double-ButtonPress-1>' )
   def selectWord( self, event ):
      event.widget.sel_setAnchor( 'insert wordstart' )
      event.widget.mark_set( 'insert', 'insert wordend' )
      self._insert_x_pos = event.x
   
   @bind( '<Triple-ButtonPress-1>' )
   def selectLine( self, event ):
      event.widget.sel_setAnchor( 'insert linestart' )
      event.widget.mark_set( 'insert', 'insert lineend' )
      self._insert_x_pos = event.x
   
   @bind( '<Button1-Leave>' )
   def scrollView( self, event ):
      widget = event.widget
      
      if event.y < 0:
         widget.yview_scroll( -1, 'units' )
      elif event.y >= widget.winfo_height():
         widget.yview_scroll( 1, 'units' )
      
      widget.grab_set( )
   
   @bind( '<MouseWheel>' )
   def wheelScroll( self, event ):
      widget = event.widget
      
      if event.delta < 0:
         widget.yview_scroll( 1, 'units' )
      else:
         widget.yview_scroll( -1, 'units' )

def insert_char(event):
	if event.widget and event.char:
		event.widget.insert('insert',event.char)


class CodeText(ttk.Tkinter.Text):
	def __init__(self):
		ttk.Tkinter.Text.__init__(self, core.mainWindow.workspaceContainer)
		self.bind("<<Selection>>", self.on_selection_changed)
		self.bind_class("Text","<Key>",insert_char)
		bindtags = list(self.bindtags())
		bindtags.insert(1,"Action")
		bindtags = " ".join(bindtags)
		self.bindtags(bindtags)
		self.styles = {}
		self.fonts = {}
		self.lexer = None
		self.markNb=0
		self.colorizeContext = None
		self.last_stopToken = "1.0"
		controller = EnhancedTextController( )
		controller.install( self )
		
	
	# Selection Operations
	def sel_clear( self ):
		try:
			self.tag_remove( 'sel', '1.0', 'end' )
		except:
			pass
      
		try:
			self.mark_unset( 'sel.anchor', 'sel.first', 'sel.last' )
		except:
			pass
   
	def sel_setAnchor( self, index ):
		self.mark_set( 'sel.anchor', index )
   
	def sel_isAnchorSet( self ):
		try:
			self.index( 'sel.anchor' )
			return True
		except:
			return False

	def sel_isSelection( self ):
		try:
			self.index( 'sel.first' )
			return True
		except:
			return False

	def sel_update( self ):
		if widget.compare( 'sel.anchor', '<', 'insert' ):
			widget.mark_set( 'sel.first', 'sel.anchor' )
			widget.mark_set( 'sel.last', 'insert' )
		elif widget.compare( 'sel.anchor', '>', 'insert' ):
			widget.mark_set( 'sel.first', 'insert' )
			widget.mark_set( 'sel.last', 'sel.anchor' )
		else:
			return
      
		widget.tag_remove( 'sel', '1.0', 'end' )
		widget.tag_add( 'sel', 'sel.first', 'sel.last' )
   
	def sel_delete( self ):
		try:
			Tkinter.Text.delete( self, 'sel.first', 'sel.last' )
		except:
			pass
		
		self.sel_clear( )

	# Overloads
	def mark_set( self, name, index ):
		Tkinter.Text.mark_set( self, name, index )
      
		if name == 'insert':
			try:
				if self.compare( 'sel.anchor', '<', 'insert' ):
					self.mark_set( 'sel.first', 'sel.anchor' )
					self.mark_set( 'sel.last', 'insert' )
				elif self.compare( 'sel.anchor', '>', 'insert' ):
					self.mark_set( 'sel.first', 'insert' )
					self.mark_set( 'sel.last', 'sel.anchor' )
				else:
					return
            	
				self.tag_remove( 'sel', '1.0', 'end' )
				self.tag_add( 'sel', 'sel.first', 'sel.last' )
			except:
				pass
	
	def enable_highlight(self, mimetype=None, filename=None):
		from pygments.lexers import guess_lexer,get_lexer_for_mimetype,get_lexer_for_filename,guess_lexer_for_filename
		from pygments.styles import get_style_by_name
		def create_fonts():
			self.fonts[(False,False)] = tkFont.Font(font=self.cget('font'))
			self.fonts[(True,False)] = self.fonts[(False,False)].copy()
			self.fonts[(True,False)].configure(weight='bold')
			self.fonts[(False,True)] = self.fonts[(False,False)].copy()
			self.fonts[(False,True)].configure(slant='italic')
			self.fonts[(True,True)] = self.fonts[(False,False)].copy()
			self.fonts[(True,True)].configure(slant='italic',weight='bold')
		def create_style_table():
			self.style = get_style_by_name('default')
		
			for token,tStyle in self.style:
				token = "DP::SH::%s"%str(token).replace('.','_')
				if tStyle['color']:
					self.tag_configure(token,foreground="#%s"%tStyle['color'])
				if tStyle['bgcolor']:
					self.tag_configure(token,background="#%s"%tStyle['bgcolor'])

				self.tag_configure(token,underline=tStyle['underline'])
				self.tag_configure(token, font=self.fonts[(tStyle['bold'],tStyle['italic'])])
				#tStyle['border']

		if mimetype:
			try:
				self.lexer = get_lexer_for_mimetype(mimetype)
			except:
				if filename:
					try:
						self.lexer = get_lexer_for_filename(filename)
					except:
						try:
							self.lexer = guess_lexer_for_filename(filename)
						except:
							self.lexer = guess_lexer(self.get("1.0", "end"))
		if self.lexer:
			create_fonts()
			create_style_table() 
		
	def insert(self, index, *args, **kword):
		ttk.Tkinter.Text.insert(self, index, *args)
		if kword.get('forceUpdate', False):
			self.update()
		if self.lexer:
			self._update_highlight(index)
	
	def delete(self, index1, index2):
		ttk.Tkinter.Text.delete(self, index1, index2)
		if self.lexer:
			self._update_highlight(index1)
	
	def calcule_distance(self, first, second):
		return self.tk.call(self._w, "count", "-chars", first, second)

	def _update_highlight(self, insertPoint):

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
		self.colorizeContext = [tokens, start, start, time()]
		#self._update_a_token(realTime=True)
		self.after_idle(self._update_a_token)	

	def _update_a_token(self,realTime=False):
		prefix = "DP::SH::"
#		def markoff(name):
#			print "markoff", name
#			self.mark_unset(name)
		markoff = self.mark_unset
		
		def markon(pos):
			#print "markon", "DP::SH::_synctx_%d"%self.markNb, pos
			self.mark_set("DP::SH::_synctx_%d"%self.markNb, pos)
			self.markNb += 1
		
#		def tagdel(name, start, end):
#			print "tagdel",name, start, end
#			self.tag_remove(name, start, end)
		tagdel = self.tag_remove
		
#		def tagadd(name, start, end):
#			print "tagadd",name, start, end
#			self.tag_add(name, start, end)
		tagadd = self.tag_add
		
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
			print time()-self.colorizeContext[3]
		else:
			try :
				process_itvs(tokens.next())
				self.after_idle(self._update_a_token)

			except StopIteration:
				self.last_stopToken = "1.0"
				print time()-self.colorizeContext[3]
				pass


class SourceBuffer(CodeText):
	def __init__(self, document):
		CodeText.__init__(self)
		self.document = document
		self.highlight_tag_protected = False
		self.tag_configure("highlight_tag", background=core.config.get('color','highlight_tag_color'))
		self.tag_configure("search_tag", background=core.config.get('color','search_tag_color'))
		self.tag_lower("highlight_tag", "sel")
		self.tag_lower("search_tag", "sel")
		
	def get_document(self):
		return self.document
	
	def set_text(self, content):
		self.delete("0.1", "end")
		self.insert("end", content, forceUpdate=True)
		self.edit_reset()
		self.edit_modified(False)
	
	def get_text(self):
		return self.get("0.1", "end")

	def on_selection_changed(self, event):
		if self.highlight_tag_protected : return
		select = self.tag_ranges("sel")
		if select:
			start_select , stop_select = select 
			text = self.get(start_select , stop_select)
			if len(text)>1 :
				self.apply_tag_on_text("highlight_tag", text)
			else:
				self.apply_tag_on_text("highlight_tag", None)

	def apply_tag_on_text(self, tag, text):
		self.tag_remove(tag, "0.1","end")

		if text:
			count = ttk.Tkinter.IntVar()
			match_start = ttk.Tkinter.Text.search(self,text, "0.1", stopindex="end", forwards=True, exact=True, count=count)
			while match_start:
				match_end = "%s+%ic"%(match_start,count.get())
				self.tag_add(tag, match_start, match_end)
				match_start = ttk.Tkinter.Text.search(self,text, match_end, stopindex="end", forwards=True, exact=True, count=count)

	def search(self, backward, text):
		if not text : return
		self.apply_tag_on_text("search_tag",text)

		start_search = "insert"
		select = self.tag_ranges("sel")
		if select:
			if backward:
				start_search = select[0]
			else:
				start_search = select[1]

		count = ttk.Tkinter.IntVar()
		match_start = ttk.Tkinter.Text.search(self,text, start_search, forwards=(not backward), backwards=backward, exact=True, count=count) 
		if match_start:
			match_end = "%s+%ic"%(match_start,count.get())
			self.highlight_tag_protected = True
			self.tag_remove("sel", "0.1","end")
			self.tag_add("sel", match_start, match_end)
			self.highlight_tag_protected = False
			self.mark_set("insert", match_start if backward else match_end)
			return True
		return False
