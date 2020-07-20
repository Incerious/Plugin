from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory
from nltk.tokenize import word_tokenize
import nltk
from tkinter import *
from tkinter.filedialog import askopenfilename
import sys
import numpy
import speech_recognition as sr

class Example(Frame):

    def __init__(self, parent):
        Frame.__init__(self, parent)   

        self.parent = parent        
        self.initUI()

    def initUI(self):

        self.parent.title("File dialog")
        self.pack(fill=BOTH, expand=1)

        menubar = Menu(self.parent)
        self.parent.config(menu=menubar)

        fileMenu = Menu(menubar)
        fileMenu.add_command(label="Insert audio", command=self.stt)
        fileMenu.add_command(label="Word Error Rate", command=self.a)
        fileMenu.add_command(label="Clear", command=self.cl)
        menubar.add_cascade(label="File", menu=fileMenu)        

        self.txt = Text(self)
        self.txt.pack(fill=BOTH, expand=1)


    def cl(self):
        self.txt.delete('1.0', END)

    def stt(self):
        AUDIO_FILE = askopenfilename(filetypes = ( ("Music", "*.wav"),("All files", "*.*") ))
        # use the audio file as the audio source
        r = sr.Recognizer()
        with sr.AudioFile(AUDIO_FILE) as source:
            audio = r.record(source)  # read the entire audio file
            # recognize speech using Google Speech Recognition
            try:
                # for testing purposes, we're just using the default API key
                # to use another API key, use `r.recognize_google(audio, key="GOOGLE_SPEECH_RECOGNITION_API_KEY")`
                # instead of `r.recognize_google(audio)`
                hyp = r.recognize_google(audio, language = 'id-id')
                file1 = open("hypo.txt", "w")
                file1.write(hyp)
                file1.close()
            except sr.UnknownValueError:
                print("Google Speech Recognition could not understand audio")
            except sr.RequestError as e:
                print("Could not request results from Google Speech Recognition service; {0}".format(e))
            self.txt.insert(END, "Berhasil Mengubah audio menjadi text"+"\n"+"\n")

    #wer

    def a(self):
        fileName = askopenfilename(filetypes = ( ("Notepad", "*.txt"),("All files", "*.*") ))
        ref = open(fileName, "r")
        r1 = ref.read().lower()
        #tambahkan stopword
        factory = StopWordRemoverFactory()
        stopword = factory.create_stop_word_remover()
        kalimat = r1
        stop = stopword.remove(kalimat)
        r = nltk.tokenize.word_tokenize(stop)
        print(r)
        self.txt.insert(END, "Ref : {}".format(' '.join(r))+"\n")

        #fileName = askopenfilename(filetypes = ( ("Notepad", "*.txt"),("All files", "*.*") ))
        f = open("hypo.txt", 'r')
        #f2 = open(fileName, "r")
        f1 = f.read().lower()
        #tambahkanstopword
        factory = StopWordRemoverFactory()
        stopword = factory.create_stop_word_remover()
        kalimat1 = f1
        stop = stopword.remove(kalimat1)
        h = nltk.tokenize.word_tokenize(stop)
        print(h)
        # Mencetak direktori file yang dimasukan kedalam label
        self.txt.insert(END, "Hyp : {}".format(' '.join(h)),"\n")

        def editDistance(r, h):
            '''
            This function is to calculate the edit distance of reference sentence and the hypothesis sentence.
            Main algorithm used is dynamic programming.
            Attributes: 
                r -> the list of words produced by splitting reference sentence.
                h -> the list of words produced by splitting hypothesis sentence.
            '''
            d = numpy.zeros((len(r)+1)*(len(h)+1), dtype=numpy.uint8).reshape((len(r)+1, len(h)+1))
            for i in range(len(r)+1):
                d[i][0] = i
            for j in range(len(h)+1):
                d[0][j] = j
            for i in range(1, len(r)+1):
                for j in range(1, len(h)+1):
                    if r[i-1] == h[j-1]:
                        d[i][j] = d[i-1][j-1]
                    else:
                        substitute = d[i-1][j-1] + 1
                        insert = d[i][j-1] + 1
                        delete = d[i-1][j] + 1
                        d[i][j] = min(substitute, insert, delete)
            return d

        def getStepList(r, h, d):
            '''
            This function is to get the list of steps in the process of dynamic programming.
            Attributes: 
                r -> the list of words produced by splitting reference sentence.
                h -> the list of words produced by splitting hypothesis sentence.
                d -> the matrix built when calulating the editting distance of h and r.
            '''
            x = len(r)
            y = len(h)
            list = []
            while True:
                if x == 0 and y == 0: 
                    break
                elif x >= 1 and y >= 1 and d[x][y] == d[x-1][y-1] and r[x-1] == h[y-1]: 
                    list.append("e")
                    x = x - 1
                    y = y - 1
                elif y >= 1 and d[x][y] == d[x][y-1]+1:
                    list.append("i")
                    x = x
                    y = y - 1
                elif x >= 1 and y >= 1 and d[x][y] == d[x-1][y-1]+1:
                    list.append("s")
                    x = x - 1
                    y = y - 1
                else:
                    list.append("d")
                    x = x - 1
                    y = y
            return list[::-1]

        def alignedPrint(list, r, h, result):
            '''
            This funcition is to print the result of comparing reference and hypothesis sentences in an aligned way.
    
            Attributes:
                list   -> the list of steps.
                r      -> the list of words produced by splitting reference sentence.
                h      -> the list of words produced by splitting hypothesis sentence.
                result -> the rate calculated based on edit distance.
            '''
            print("REF:", end=" ")
            for i in range(len(list)):
                if list[i] == "i":
                    count = 0
                    for j in range(i):
                        if list[j] == "d":
                            count += 1
                    index = i - count
                    print(" "*(len(h[index])), end=" ")
                elif list[i] == "s":
                    count1 = 0
                    for j in range(i):
                        if list[j] == "i":
                            count1 += 1
                    index1 = i - count1
                    count2 = 0
                    for j in range(i):
                        if list[j] == "d":
                            count2 += 1
                    index2 = i - count2
                    if len(r[index1]) < len(h[index2]):
                        print(r[index1] + " " * (len(h[index2])-len(r[index1])), end=" ")
                    else:
                        print(r[index1], end=" "),
                else:
                    count = 0
                    for j in range(i):
                        if list[j] == "i":
                            count += 1
                    index = i - count
                    print(r[index], end=" "),
            print("\nHYP:", end=" ")
            for i in range(len(list)):
                if list[i] == "d":
                    count = 0
                    for j in range(i):
                        if list[j] == "i":
                            count += 1
                    index = i - count
                    print(" " * (len(r[index])), end=" ")
                elif list[i] == "s":
                    count1 = 0
                    for j in range(i):
                        if list[j] == "i":
                            count1 += 1
                    index1 = i - count1
                    count2 = 0
                    for j in range(i):
                        if list[j] == "d":
                            count2 += 1
                    index2 = i - count2
                    if len(r[index1]) > len(h[index2]):
                        print(h[index2] + " " * (len(r[index1])-len(h[index2])), end=" ")
                    else:
                        print(h[index2], end=" ")
                else:
                    count = 0
                    for j in range(i):
                        if list[j] == "d":
                            count += 1
                    index = i - count
                    print(h[index], end=" ")
            print("\nEVA:", end=" ")
            for i in range(len(list)):
                if list[i] == "d":
                    count = 0
                    for j in range(i):
                        if list[j] == "i":
                            count += 1
                    index = i - count
                    print("D" + " " * (len(r[index])-1), end=" ")
                elif list[i] == "i":
                    count = 0
                    for j in range(i):
                        if list[j] == "d":
                            count += 1
                    index = i - count
                    print("I" + " " * (len(h[index])-1), end=" ")
                elif list[i] == "s":
                    count1 = 0
                    for j in range(i):
                        if list[j] == "i":
                            count1 += 1
                    index1 = i - count1
                    count2 = 0
                    for j in range(i):
                        if list[j] == "d":
                            count2 += 1
                    index2 = i - count2
                    if len(r[index1]) > len(h[index2]):
                        print("S" + " " * (len(r[index1])-1), end=" ")
                    else:
                        print("S" + " " * (len(h[index2])-1), end=" ")
                else:
                    count = 0
                    for j in range(i):
                        if list[j] == "i":
                            count += 1
                    index = i - count
                    print(" " * (len(r[index])), end=" ")
            print("\nWER: " + result)
            self.txt.insert(END, "\nWER: " + result)

        def wer(r, h):
            """
            This is a function that calculate the word error rate in ASR.
            You can use it like this: wer("what is it".split(), "what is".split()) 
            """
            # build the matrix
            d = editDistance(r, h)

            # find out the manipulation steps
            list = getStepList(r, h, d)

            # print the result in aligned way
            result = float(d[len(r)][len(h)]) / len(r) * 100
            result = str("%.2f" % result) + "%"
            alignedPrint(list, r, h, result)

        #proses pemanggilan def wer
        z= wer(r,h)

def main():

    root = Tk()
    ex = Example(root)
    root.geometry("300x250+300+300")
    root.mainloop()  

if __name__ == '__main__':
    main()
    
