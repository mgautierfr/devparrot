
from devparrot.core.command import MasterCommand, SubCommand
from devparrot.core import session

class completion(MasterCommand):
    @SubCommand()
    def start():
        completionSystem = session.completionSystem
        completionSystem.set_model(session.get_currentDocument().model)
        completionSystem.update_completion(now=True)

session.bindings["<Control-space>"] = "completion start\n"
