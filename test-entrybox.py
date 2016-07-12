#!/usr/bin/env python3

"""NOT WORKING!"""

from Tkinter import *

def assignresult():
    result = entryWidget.get().strip()
    return result


root = Tk()
root.title("Tkinter Entry Widget")
root["padx"] = 40
root["pady"] = 20
# Create a text frame to hold the text Label and the Entry widget
textFrame = Frame(root)
#Create a Label in textFrame
entryLabel = Label(textFrame)
entryLabel["text"] = "Enter the text:"
entryLabel.pack(side=LEFT)
# Create an Entry Widget in textFrame
entryWidget = Entry(textFrame)
entryWidget["width"] = 50
entryWidget.pack(side=LEFT)
textFrame.pack()
button = Button(root, text="Submit", command=assignresult)
button.pack()
root.mainloop()

print(result)
