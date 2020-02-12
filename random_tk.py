import tkinter as tk
import random

word_cnt = 24
with open('words.txt', 'r') as infile:
    words = infile.readlines()


class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.pack()
        self.create_widgets()

    def create_widgets(self):
        self.new_word = tk.Button(self)
        self.new_word['text'] = 'New Words'
        self.new_word['command'] = self.random_word
        self.new_word.pack(side='left')
        
        self.display = tk.Text(self)
        random.seed()
        for i in range(word_cnt):
            word = random.choice(words)
            self.display.insert(tk.END, word)
        self.display.pack(side='left')
        

    def random_word(self):
        random.seed()
        self.display.delete(1.0, tk.END)
        for i in range(word_cnt):
            word = random.choice(words)
            self.display.insert(tk.END, word)
        

root = tk.Tk()
app = Application(master=root)
app.mainloop()