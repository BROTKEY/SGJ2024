class BaseController():
    
    def pollAxis(self) -> tuple[float, float]:
        """return the value of the analog axis in order of strength, direction"""
        return 0,0
    
    def start(self) -> None:
        """start arbitrary controller"""
        pass

    def stop(self) -> None:
        """stop arbitrary controller"""