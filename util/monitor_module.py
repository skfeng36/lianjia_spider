'''

'''

class Monitor:
    def __init__(self,signal_type):
        self.signal_type=signal_type
        

    def set_signal(self,signal_type):
        self.signal_tpye=signal_type
           

    def signal_handle(self):
        if self.signal_type==signal.SIGINT:
            exit(0)
    

