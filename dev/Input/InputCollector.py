import inputs, tkinter, os, threading, time

# Looking for the gamepad:
events = inputs.get_gamepad()
ms_time = lambda: int(round(time.time() * 1000))


class InputEvent:
    def __init__( self, data ):
        self.data      = data
        self.timestamp = ms_time()


    def __str__( self ):
        return "< {} @ {} >".format( self.button, self.timestamp )

    

class InputWatcher:
    def __init__( self, flushfile = None ):
        if flushfile != None:
            self.flushfile = flushfile
        else:
            self.flushfile = os.path.join( os.getcwd(), "InputLog.txt" )
        
        self.inputs = []
        self.lock = threading.Lock()
        self.worker = None
        self.working = False


    def start_watching( self ):
        self.working = True
        self.worker = threading.Thread(target=self.worker_thread)
        self.worker.start()

    def cease_watching( self ):
        self.working = False
        self.worker.join()
           

    def flush_to_disk( self ):
        try:
            open( self.flush_file, 'r' )
        except IOError:
            open( self.flush_file, 'w' )

            
        with open( self.flush_file, 'a' ) as f:
            while True:
                try:
                    f.write( self.inputs.pop(0) )
                except IndexError:
                    break

    
    def worker_thread( self ):
        while self.working:
            events = inputs.get_gamepad()
            for e in events:
                s = "Type: {}\nCode: {}\nState: {}\n\n".format( e.ev_type, e.code, e.state )
                self.inputs.append( InputEvent( s ) )
        
if __name__ == "__main__":
    watcher = InputWatcher()
    watcher.start_watching()
    time.sleep( 20 )
    watcher.cease_watching()
