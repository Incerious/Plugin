from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory
from nltk.tokenize import word_tokenize
import nltk
from tkinter import *
from tkinter.filedialog import askopenfilename
import sys
import numpy
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
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
        ref = nltk.tokenize.word_tokenize(stop)
        
        print(ref)
        self.txt.insert(END, "Ref : {}".format(' '.join(ref))+"\n")

        #fileName = askopenfilename(filetypes = ( ("Notepad", "*.txt"),("All files", "*.*") ))
        f = open("hypo.txt", 'r')
        #f2 = open(fileName, "r")
        f1 = f.read().lower()
        factory = StopWordRemoverFactory()
        stopword = factory.create_stop_word_remover()
        kalimat = f1
        stop = stopword.remove(kalimat)
        hyp = nltk.tokenize.word_tokenize(stop)
        print(hyp)
        # Mencetak direktori file yang dimasukan kedalam label
        self.txt.insert(END, "Hyp : {}".format(''.join(hyp)),"\n")

        def wer(r, h, debug=False):
            #costs will holds the costs, like in the Levenshtein distance algorithm
            costs = [[0 for inner in range(len(h)+1)] for outer in range(len(r)+1)]
            # backtrace will hold the operations we've done.
            # so we could later backtrace, like the WER algorithm requires us to.
            backtrace = [[0 for inner in range(len(h)+1)] for outer in range(len(r)+1)]

            OP_OK = 0
            OP_SUB = 1
            OP_INS = 2
            OP_DEL = 3
            DEL_PENALTY=1 # Tact
            INS_PENALTY=1 # Tact
            SUB_PENALTY=1 # Tact
            # First column represents the case where we achieve zero
            # hypothesis words by deleting all reference words.
            for i in range(1, len(r)+1):
                costs[i][0] = DEL_PENALTY*i
                backtrace[i][0] = OP_DEL

            # First row represents the case where we achieve the hypothesis
            # by inserting all hypothesis words into a zero-length reference.
            for j in range(1, len(h) + 1):
                costs[0][j] = INS_PENALTY * j
                backtrace[0][j] = OP_INS

            # computation
            for i in range(1, len(r)+1):
                for j in range(1, len(h)+1):
                    if r[i-1] == h[j-1]:
                        costs[i][j] = costs[i-1][j-1]
                        backtrace[i][j] = OP_OK
                    else:
                        substitutionCost = costs[i-1][j-1] + SUB_PENALTY # penalty is always 1
                        insertionCost    = costs[i][j-1] + INS_PENALTY   # penalty is always 1
                        deletionCost     = costs[i-1][j] + DEL_PENALTY   # penalty is always 1

                        costs[i][j] = min(substitutionCost, insertionCost, deletionCost)
                        if costs[i][j] == substitutionCost:
                            backtrace[i][j] = OP_SUB
                        elif costs[i][j] == insertionCost:
                            backtrace[i][j] = OP_INS
                        else:
                            backtrace[i][j] = OP_DEL

            # back trace though the best route:
            i = len(r)
            j = len(h)
            numSub = 0
            numDel = 0
            numIns = 0
            numCor = 0
            if debug:
                print("OP\tREF\tHYP")
                lines = []
            while i > 0 or j > 0:
                if backtrace[i][j] == OP_OK:
                    numCor += 1
                    i-=1
                    j-=1
                    if debug:
                        lines.append("OK\t" + r[i]+"\t"+h[j])
                elif backtrace[i][j] == OP_SUB:
                    numSub +=1
                    i-=1
                    j-=1
                    if debug:
                        lines.append("SUB\t" + r[i]+"\t"+h[j])
                elif backtrace[i][j] == OP_INS:
                    numIns += 1
                    j-=1
                    if debug:
                        lines.append("INS\t" + "****" + "\t" + h[j])
                elif backtrace[i][j] == OP_DEL:
                    numDel += 1
                    i-=1
                    if debug:
                        lines.append("DEL\t" + r[i]+"\t"+"****")
            if debug:
                lines = reversed(lines)
                for line in lines:
                    print(line)
                print("Ncor " + str(numCor))
                print("Nsub " + str(numSub))
                print("Ndel " + str(numDel))
                print("Nins " + str(numIns))
            return (numSub + numDel + numIns) / (float) (len(r))
            wer_result = round( (numSub + numDel + numIns) / (float) (len(r)), 3)
            return {'WER':wer_result, 'Cor':numCor, 'Sub':numSub, 'Ins':numIns, 'Del':numDel}

        #proses pemanggilan def wer
        z= wer(ref,hyp, debug=True)

def main():

    root = Tk()
    ex = Example(root)
    root.geometry("300x250+300+300")
    root.mainloop()  

if __name__ == '__main__':
    main()
    import doctest

    doctest.testmod()
