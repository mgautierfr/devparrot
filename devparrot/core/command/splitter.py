
class Token(object):
    def __init__(self, startIndex, value="", endIndex=None, quote=None):
        self.value = value
        self.startIndex = startIndex
        self.quote = quote
        self.endIndex = endIndex

    def add(self, char):
        self.value += char

    def __str__(self):
        return self.value

class Splitter(object):
    whitespace = " "
    quotes = '\'"'
    escape = '\\'
    SPACE, NORMAL, QUOTE, TOKEN_END, END = xrange(5)
    def __init__(self, string, forCompletion=False):
        self.string = string
        self.currentChar = -1
        self.state = Splitter.SPACE
        self.token = None
        self.forCompletion = forCompletion
        pass

    def _get_next(self):
        self.currentChar += 1
        return self.string[self.currentChar]

    def _space_read(self):
        try:
            char = self._get_next()

            if char in Splitter.whitespace:
                return Splitter.SPACE

            self.token = Token(startIndex=self.currentChar)
            if char in Splitter.quotes:
                self.token.quote = char
                return Splitter.QUOTE

            if char in Splitter.escape:
                char = self._get_next()

            self.token.add(char)
            return Splitter.NORMAL
        except IndexError:
            if self.forCompletion:
                self.token = Token(startIndex=len(self.string), endIndex=len(self.string))
            return Splitter.END

    def _quote_read(self):
        try:
            char = self._get_next()

            if char == self.token.quote:
                return Splitter.NORMAL

            if char in Splitter.escape:
                char = self._get_next()

            self.token.add(char)
            return Splitter.QUOTE
        except IndexError:
            if self.forCompletion:
                return Splitter.END
            else:
                raise ValueError, "No closing quotation"

    def _normal_read(self):
        try:
            char = self._get_next()

            if char in Splitter.whitespace:
                self.endIndex = self.currentChar
                return Splitter.TOKEN_END

            if char in Splitter.quotes:
                self.token.quote = char
                return Splitter.QUOTE


            if char in Splitter.escape:
                char = self._get_next()

            self.token.add(char)
            return Splitter.NORMAL
        except IndexError:
            return Splitter.END

    def read_token(self):
        while True:
            if self.state == Splitter.SPACE:
                self.state = self._space_read()
            elif self.state == Splitter.QUOTE:
                self.state = self._quote_read()
            elif self.state == Splitter.NORMAL:
                self.state = self._normal_read()
            elif self.state in (Splitter.TOKEN_END, Splitter.END):
                result = self.token
                self.token = None
                if self.state == Splitter.TOKEN_END:
                    self.state = Splitter.SPACE
                return result

    def __iter__(self):
        return self

    def next(self):
        token = self.read_token()
        if token is None:
            raise StopIteration
        return token

