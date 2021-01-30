import os
from tkinter.filedialog import askdirectory 
import pygame
from mutagen.id3 import ID3
from mutagen.mp3 import MP3
from tkinter import *

pygame.init()
pygame.mixer.init()


class App:
    def __init__(self, root):

        self.root = root
        self.root.title("MP3 Player")
        self.root.configure(bg='grey14')
        self.root.wm_iconbitmap('icon.ico')
        self.root.minsize(650, 550)

        self.songs_list = []
        self.names = []
        self.index = 0
        self.v = StringVar()
        self.duration = 0
        self.paused = False
        self.nextt = pygame.USEREVENT + 1

        self.playlisticon = PhotoImage(file="Playlist.png")
        self.playicon = PhotoImage(file="Play.png")
        self.pauseicon = PhotoImage(file='Pause.png')
        self.nexticon = PhotoImage(file="Next.png")
        self.previcon = PhotoImage(file="Previous.png")

        self.label = Label(self.root, bg='grey14', fg='SkyBlue3', font=("Arial", 10), text='Playlist')
        self.label.pack()

        self.listbox = Listbox(self.root, bg='grey14', fg='SkyBlue3', highlightbackground='SkyBlue3',
                               highlightthickness=1, font=("Arial", 10), width=80, height=15, selectbackground='grey14',
                               selectmode='SINGLE')
        self.listbox.pack(pady=4)

        self.buttonframe = Frame(self.root, bg='grey14')
        self.buttonframe.pack()

        self.playlistbutton = Button(self.buttonframe, text='Add to Playlist', activebackground='grey14',
                                     image=self.playlisticon, border=0, bg='grey14', fg='white',
                                     command=self.directorychooser)
        self.playlistbutton.pack(pady=2)

        self.prevbutton = Button(self.buttonframe, text='Previous', activebackground='grey14', image=self.previcon,
                                 border=0, bg='grey14', fg='white', command=self.prevsong)
        self.prevbutton.pack(pady=2, padx=2, side=LEFT)

        self.togglebutton = Button(self.buttonframe, text='Pause/Play', activebackground='grey14', image=self.pauseicon,
                                   border=0, bg='grey14', width=40, height=46, fg='white', command=self.toggle)
        self.togglebutton.pack(pady=2, padx=2, side=LEFT)

        self.nextbutton = Button(self.buttonframe, text='Next', activebackground='grey14', image=self.nexticon,
                                 border=0, bg='grey14', fg='white', command=self.nextsong)
        self.nextbutton.pack(pady=2, padx=2, side=LEFT)

        self.durationscale = Scale(self.root, bg='grey14', fg='SkyBlue3', length=400, highlightbackground='grey14',
                                   activebackground='black', highlightthickness=1, sliderrelief=FLAT,
                                   troughcolor='SkyBlue3', bd=0, orient=HORIZONTAL, from_=0, to=100, sliderlength=10,
                                   width=5)
        self.durationscale.pack(padx=4, pady=4)

        self.bottomframe = Frame(self.root, bg='grey14')
        self.bottomframe.pack(side=BOTTOM)

        self.playinglabel = Label(self.bottomframe, bg='grey14', fg='SkyBlue3', font=("Arial", 10), text="Now Playing: ")
        self.playinglabel.pack(side=LEFT, pady=2)

        self.songlabel = Label(self.bottomframe, bg='grey14', font=("Arial", 10), fg='SkyBlue3', width=45,
                               textvariable=self.v)
        self.songlabel.pack(side=LEFT, pady=2)

        self.volumescale = Scale(self.bottomframe, bg='grey14', fg='SkyBlue3', length=100, resolution=2,
                                 activebackground='grey14', font=("Arial", 10), label='Volume', highlightthickness=0,
                                 troughcolor='SkyBlue3', bd=0, orient=HORIZONTAL, from_=0, to=100, width=10,
                                 sliderlength=20, sliderrelief=GROOVE, command=self.volume)
        self.volumescale.pack(side=LEFT, pady=4)
        self.volumescale.set(80)

        self.root.bind("<p>", self.prevsong)
        self.root.bind("<n>", self.nextsong)
        self.root.bind("<Right>", self.forward)
        self.root.bind("<Left>", self.backward)
        self.root.bind("<Control-Right>", self.forward2)
        self.root.bind("<Control-Left>", self.backward2)
        self.root.bind("<space>", self.toggle)
        self.root.bind("<Up>", self.incvol)
        self.root.bind("<Down>", self.decvol)
        self.durationscale.bind("<ButtonRelease-1>", self.forback)

    def directorychooser(self, _=None):
        directory = askdirectory()
        os.chdir(directory)
        for files in os.listdir(directory):
            if files.endswith(".mp3"):
                realdir = os.path.realpath(files)
                audio = ID3(realdir)
                self.names.append(audio['TIT2'].text[0])
                self.songs_list.append(files)

        self.names.reverse()
        for items in self.names:
            self.listbox.insert(0, items)

        self.names.reverse()
        self.play()
        return 'break'

    def updatelabel(self):
        self.v.set(self.names[self.index])

    def nextsong(self, _=None):
        length = len(self.songs_list)
        if self.index < length - 1:
            self.index += 1
            self.play()

        elif self.index == length - 1:
            self.index = 0
            self.play()

    def prevsong(self, _=None):
        if self.index > 0:
            self.index -= 1
            self.play()

        elif self.index == 0:
            self.index = len(self.songs_list) - 1
            self.play()

    def toggle(self, _=None):
        if self.paused:
            pygame.mixer.music.unpause()
            self.togglebutton.configure(image=self.pauseicon)
            self.paused = False
            self.progress()
        elif not self.paused:
            pygame.mixer.music.pause()
            self.togglebutton.configure(image=self.playicon)
            self.paused = True

    def play(self):
        audio = MP3(self.songs_list[self.index])
        self.duration = int(audio.info.length)
        pygame.mixer.music.load(self.songs_list[self.index])
        self.updatelabel()
        pygame.mixer.music.play()
        pygame.mixer.music.set_endevent(self.nextt)
        self.durationscale.configure(to=self.duration)
        self.duration *= 100
        self.durationscale.set(0)
        self.progress()

    def check(self):
        for event in pygame.event.get():
            if self.paused:
                break
            if event.type == self.nextt:
                self.nextsong()

    def volume(self, _=None):
        vol = self.volumescale.get()
        vol = vol / 100
        pygame.mixer.music.set_volume(vol)

    def incvol(self, _=None):
        vol = self.volumescale.get()
        vol += 10
        self.volumescale.set(vol)
        vol = vol / 100
        pygame.mixer.music.set_volume(vol)

    def decvol(self, _=None):
        vol = self.volumescale.get()
        vol -= 10
        self.volumescale.set(vol)
        vol = vol / 100
        pygame.mixer.music.set_volume(vol)

    def progress(self):
        import time
        d = self.durationscale.get()
        d *= 100
        for i in range(d, self.duration + 1):
            time.sleep(0.01)
            if i % 100 == 0:
                self.durationscale.set(i / 100)
            if self.paused:
                break
            self.check()
            root.update()

    def forward(self, _=None):
        f = self.durationscale.get()
        if f + 10 <= self.duration / 100:
            f += 10
            self.durationscale.set(f)
            pygame.mixer.music.rewind()
            pygame.mixer.music.set_pos(f)
            self.progress()

    def forward2(self, _=None):
        f = self.durationscale.get()
        if f + 60 <= self.duration / 100:
            f += 60
            self.durationscale.set(f)
            pygame.mixer.music.rewind()
            pygame.mixer.music.set_pos(f)
            self.progress()

    def backward(self, _=None):
        f = self.durationscale.get()
        if f - 10 >= 0:
            f -= 10
            self.durationscale.set(f)
            pygame.mixer.music.rewind()
            pygame.mixer.music.set_pos(f)
            self.progress()

    def backward2(self, _=None):
        f = self.durationscale.get()
        if f - 60 >= 0:
            f -= 60
            self.durationscale.set(f)
            pygame.mixer.music.rewind()
            pygame.mixer.music.set_pos(f)
            self.progress()

    def forback(self, _=None):
        f = self.durationscale.get()
        pygame.mixer.music.rewind()
        pygame.mixer.music.set_pos(f)
        self.progress()


root = Tk()
app = App(root)
root.mainloop()
