
from devparrot.core.command import MasterCommand, SubCommand
from devparrot.core import session

class completion(MasterCommand):
    @SubCommand()
    def start():
        """Start the completion engine

        Wich completion engine in started depends of the configuration.
        What is really done by completion engine depends of the engine...

        But most of the time, it will propose few text to complete what under the 'insert' cursor.
        """
        completionSystem = session.completionSystem
        completionSystem.set_model(session.get_currentDocument().model)
        completionSystem.update_completion(now=True)

session.bindings["<Control-space>"] = "completion start\n"
