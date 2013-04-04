
class Section(dict):
    def __init__(self, name, parentSection=None):
        self.name = name
        self.parentSection = parentSection
        
    def __getattr__(self, commandName):
        return self[commandName]

    def add_command(self, name, wrapper):
        self[name] = wrapper

    def get_name(self):
        if self.parentSection:
            return "%s.%s"%(self.parentSection.get_name(), self.name)
        return self.name
    
