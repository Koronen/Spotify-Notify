try:
	from Xlib import X, display, error, Xatom
	import Xlib.protocol.event
except:
	print "You need the xlib-library. If you are using Ubuntu, try running\n\"sudo apt-get install python-xlib\""
	sys.exit(1)

class spotify(object):
    def __init__(self):
        self._dsp = display.Display()
        self._screen  = self._dsp.screen()
        self._root    = self._screen.root
    #   self.error   = error.CatchError()
        self._root.change_attributes(event_mask=(X.PropertyChangeMask))
        self._dsp.flush()
        
    
        self._spotify_task = None
        self._spotify_obj = None
        self._spotify_title = None # Spotify's window title
        
        
        self._init_spotify_data()
    
    def _init_spotify_data(self):
        """Search the spotify window and initialize the data"""
        tasks = self._root.get_full_property(
                        self._dsp.intern_atom("_NET_CLIENT_LIST"),
                        Xatom.WINDOW
                ).value
        
        is_running = False
        
        for task in tasks:
            obj  = self._dsp.create_resource_object("window", task)
            name = ( obj.get_full_property(self._dsp.intern_atom("_NET_WM_NAME"), 0) or
                     obj.get_full_property(Xatom.WM_NAME, 0) )
            title = getattr(name,'value','')
            if title is not '' and title.startswith('Spotify'):
                obj.change_attributes(event_mask=(
                    X.PropertyChangeMask|X.StructureNotifyMask))
                is_running = True
                self._spotify_task = task
                self._spotify_obj = obj
                self._spotify_title = title
                break
                
        if not is_running and self._spotify_task is not None:
            self._delete_spotify_data()
        
    
    def _update_spotify_title(self):
        """Update the song data"""
        name = ( self._spotify_obj.get_full_property(self._dsp.intern_atom("_NET_WM_NAME"), 0) or
                 self._spotify_obj.get_full_property(Xatom.WM_NAME, 0) )
        title = getattr(name,'value','')
        if title is not '' and title.startswith('Spotify'):
            self._spotify_title = title
    
    def _delete_spotify_data(self):
        self._spotify_task = None
        self._spotify_obj = None
        self._spotify_title = None
    
    
    def _update(self):
        while True:
            e = self._dsp.next_event()
            #print e
            
            if e.type == X.DestroyNotify:
                if e.window.id == self._spotify_task:
                    self._delete_spotify_data()
                    #print "Spotify has been closed"
            elif e.type == X.PropertyNotify:
                if e.atom == self._dsp.intern_atom("_NET_CLIENT_LIST"):
                    #print '_NET_CLIENT_LIST'
                    if self._spotify_task is not None:
                        #if hasattr(e, "window") and self._spotify_task == e.window.id:
                            #print 'Spotify seems to have changed'
                        pass
                    else:
                        # print 'Spotify has been started'
                        self._init_spotify_data()
                elif self._spotify_task is not None and e.window.id == self._spotify_task:
                    if e.atom in [Xatom.WM_NAME, self._dsp.intern_atom("_NET_WM_NAME")]:
                        try:
                            self._update_spotify_title()
                            #print 'Spotify has changed the name %s' % self._spotify_title
                        except Xlib.error.BadWindow:
                            #print "BADWINDOW!"
                            pass
            self.get_song()
            self.on_update()
    
    def get_song(self):
        # self._spotify_title -> "Spotify \xe2\x80\x93 Title - Artist"
        
        if self._spotify_title is None or self._spotify_title == 'Spotify':
            # Closed or stopped
            return None
        
        data = self._spotify_title[10:].split(' \xe2\x80\x93 ')
        
        if len(data) == 2:
            return {'artist': data[0], 'title': data[1]}
        else:
            #Unexpected format
            return {'title': self._spotify_title[10:]}
