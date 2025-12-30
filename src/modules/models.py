from dataclasses import dataclass


# Makes readeble more than init function
@dataclass(frozen=True) # Immutability
class City:
    id:int
    x:float
    y:float

    def __repr__(self):
        return f"City(id={self.id}, x={self.x}, y={self.y})"
    


