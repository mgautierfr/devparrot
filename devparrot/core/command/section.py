
class Section(dict):
    def __getattr__(self, commandName):
        return self[commandName]

    def add_command(self, name, wrapper):
        self[name] = wrapper
