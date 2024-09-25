class Led:
    def __init__(self, state: int, id: int, name: str):
        self.state = state
        self.id = id
        self.name = name
        
    def showInfo(self):
        print(f"State: {self.state}")
        print(f"ID: {self.id}")
        print(f"Name: {self.name}")
        
        
class Switch:
    def __init__(self, state: int, id: int, name: str):
        self.state = state
        self.id = id
        self.name = name
        
    def showInfo(self):
        print(f"State: {self.state}")
        print(f"ID: {self.id}")
        print(f"Name: {self.name}")
        
class Command:
    def __init__(self, action: str, sender: str, receiver: str, switches: list, lights: list):
        self.action = action
        self.sender = sender
        self.receiver = receiver
        self.switches = switches
        self.lights = lights
        
    def __init__(self, action: str = "", sender: str = "", receiver: str = "", switches: list = None, lights: list = None):
        self.action = action
        self.sender = sender
        self.receiver = receiver
        self.switches = switches if switches is not None else []
        self.lights = lights if lights is not None else []
            
    def serialized(self):
        return {
            "action": self.action,
            "sender": self.sender,
            "receiver": self.receiver,
            "switches": [{"state": sw.state, "id": sw.id, "name": sw.name} for sw in self.switches],
            "lights": [{"state": light.state, "id": light.id, "name": light.name} for light in self.lights]
        }
        
        