#-------------------------------------------------------------------------------
# Name:        Object bounding box label tool
# Purpose:     Label object bboxes for ImageNet Detection data
# Author:      Qiushi
# Created:     06/06/2014

#modifyed by bwerler
#Purpose:     Label object bboxes for ImageNet Detection data for RetinaNet
#Created 06/11/2018
#-------------------------------------------------------------------------------
from __future__ import division
#from Tkinter import *
from tkinter import *
#for combobox
from tkinter import ttk
#import tkMessageBox
import tkinter.messagebox
from PIL import Image, ImageTk
import os
import glob
import random

# colors for the bboxes
COLORS = ['red', 'blue', 'green', 'pink', 'cyan', 'yellow', 'black']
# image sizes for the examples
SIZE = 256, 256

class LabelTool():
    def __init__(self, master):
        # set up the main frame
        self.parent = master
        self.parent.title("LabelTool")#window name の決定
        self.frame = Frame(self.parent)#全体のframeにwindowを追加
        self.frame.pack(fill=BOTH,expand=1)#packはwidgetを1次元に配置する
        self.parent.resizable(width = FALSE, height = FALSE)#サイズ変更を指定

        # initialize global state
        self.imageDir = ''
        self.imageList= []
        self.egDir = ''
        self.egList = []
        self.outDir = ''
        self.cur = 0
        self.total = 0
        self.category = 0
        self.imagename = ''
        self.labelfilename = ''
        self.tkimg = None
         #original
        self.classNames = ['copper','shilver','iron','gold','carbon','other']
            #任意のファイルパス
        #self.labelfilenameOpt = './data/'
        self.labelfilenameOpt = ''
        #self.classId = [0,1,2]
        #original
        self.folderVal = ['1','2','3']

        # initialize mouse state
        self.STATE = {}
        self.STATE['click'] = 0 #0で1回目のクリック前の状態　1で2回目のクリック前にの状態
        self.STATE['x'], self.STATE['y'] = 0, 0

        # reference to bbox
        self.bboxIdList = []
        self.bboxId = None
        self.bboxList = []
        self.hl = None
        self.vl = None

        # ----------------- GUI stuff ---------------------
        # dir entry & load
        self.dirPanel = Frame(self.frame)
        self.dirPanel.grid(row = 0, column = 0, columnspan = 2)
        self.label = Label(self.dirPanel, text = "Image Dir:")#frameにlabelを追加
        #self.label.grid(row = 0, column = 0)#stickyを伸縮の起点を指定
        self.label.pack()
        '''
        self.entry = Entry(self.frame)#frameにentryを追加
        self.entry.grid(row = 0, column = 1, sticky = W+E)#W+S　左右に伸ばせるように
        '''
        #pull down menu　でフォルダをセレクト]
        #v1にcomboboxの選択中の値が格納される。
        self.v1 = StringVar()
        self.comboBox = ttk.Combobox(self.dirPanel,textvariable=self.v1)
        self.comboBox['values'] = ('1','2','3')
        self.comboBox.set('1')
        #self.comboBox.grid(row = 0, column = 1,ipadx = 30)
        self.comboBox.pack()
        self.ldBtn = Button(self.frame, text = "Load", command = self.loadDir)#loadDir関数を呼び出し
        self.ldBtn.grid(row = 0, column = 2, sticky = W+E)

        # main panel for labeling
        self.mainPanel = Canvas(self.frame, cursor='tcross')#cursorはカーソルの種類を決める
        self.mainPanel.bind("<Button-1>", self.mouseClick)#イベントの設定 <Button-1>は左ボタン
        self.mainPanel.bind("<Motion>", self.mouseMove)#イベントの設定 <Motion>は左ボタンを押しながら動いたとき
        self.parent.bind("<Escape>", self.cancelBBox)  # press <Espace> to cancel current bbox
        #self.parent.bind("s", self.cancelBBox)
        #self.parent.bind("a", self.prevImage) # press 'a' to go backforward
        #self.parent.bind("d", self.nextImage) # press 'd' to go forward
        self.mainPanel.grid(row = 1, column = 1, rowspan = 4, sticky = W+N)#entryと同じ列

        # showing bbox info & delete bbox
        self.lb1 = Label(self.frame, text = 'Bounding boxes:')
        self.lb1.grid(row = 1, column = 2,  sticky = W+N)#loadボタンと同じ列
        self.listbox = Listbox(self.frame, width = 40, height = 12)
        self.listbox.grid(row = 2, column = 2, sticky = N)
        self.btnDel = Button(self.frame, text = 'Delete', command = self.delBBox)
        self.btnDel.grid(row = 3, column = 2, sticky = W+E+N)
        self.btnClear = Button(self.frame, text = 'ClearAll', command = self.clearBBox)
        self.btnClear.grid(row = 4, column = 2, sticky = W+E+N)

        # control panel for image navigation
        self.ctrPanel = Frame(self.frame)
        self.ctrPanel.grid(row = 5, column = 1, columnspan = 2, sticky = W+E)
        self.prevBtn = Button(self.ctrPanel, text='<< Prev', width = 10, command = self.prevImage)
        self.prevBtn.pack(side = LEFT, padx = 5, pady = 3)
        self.nextBtn = Button(self.ctrPanel, text='Next(Save) >>', width = 10, command = self.nextImage)
        self.nextBtn.pack(side = LEFT, padx = 5, pady = 3)
        self.progLabel = Label(self.ctrPanel, text = "Progress:     /    ")
        self.progLabel.pack(side = LEFT, padx = 5)
        self.tmpLabel = Label(self.ctrPanel, text = "Go to Image No.")
        self.tmpLabel.pack(side = LEFT, padx = 5)
        self.idxEntry = Entry(self.ctrPanel, width = 5)
        self.idxEntry.pack(side = LEFT)
        self.goBtn = Button(self.ctrPanel, text = 'Go', command = self.gotoImage)
        self.goBtn.pack(side = LEFT)

        # example pannel for illustration
        self.egPanel = Frame(self.frame, border = 10)
        self.egPanel.grid(row = 2, column = 0, rowspan = 5, sticky = N)
        self.tmpLabel2 = Label(self.egPanel, text = "Choose class")
        self.tmpLabel2.pack()
        self.egLabels = []

        for i in range(3):
            self.egLabels.append(Label(self.egPanel))
            #self.egLabels[-1].pack(side = TOP)

        # display mouse position
        self.disp = Label(self.ctrPanel, text='')
        self.disp.pack(side = RIGHT)

        self.frame.columnconfigure(1, weight = 1)
        self.frame.rowconfigure(4, weight = 1)

        #original class choice
        self.classListbox = Listbox(self.egPanel, width = 15, height = 10)
        for className in self.classNames:
            self.classListbox.insert(END,className)
        #初期選択
        self.classListbox.select_set(0)
        self.classListbox.pack()


        #self.pathLabel.grid(row = 3, column = 0, sticky = E)#stickyを伸縮の起点を指定
        #write filepath
        self.passPanel = Frame(self.frame)
        self.passPanel.grid(row = 3, column = 0,sticky = W+E)
        self.pathLabel = Label(self.passPanel, text = "Path")#frameにlabelを追加
        self.pathLabel.pack()
        self.filepathEntry = Entry(self.passPanel)
        self.filepathEntry.pack()

        
        
        # for debugging
##        self.setImage()
##        self.loadDir()

    def loadDir(self, dbg = False):
        if not dbg:
            #s = self.entry.get()
            s = self.v1.get()
            self.parent.focus()
            self.category = int(s)
        else:
            s = r'D:\workspace\python\labelGUI'
##        if not os.path.isdir(s):
##            tkMessageBox.showerror("Error!", message = "The specified dir doesn't exist!")
##            return
        # get image list
        self.imageDir = os.path.join(r'./Images', '%03d' %(self.category))
        self.imageList = glob.glob(os.path.join(self.imageDir, '*.jpg'))
        self.imageList.sort()  # By Tomonori12
        if len(self.imageList) == 0:
            print('No .JPEG images found in the specified dir!')  # By Tomonori12
            return
        # default to the 1st image in the collection
        self.cur = 1
        self.total = len(self.imageList)

         # set up output dir
        self.outDir = os.path.join(r'./Labels', '%03d' %(self.category))
        if not os.path.exists(self.outDir):
            os.mkdir(self.outDir)
        # load example bboxes
        self.egDir = os.path.join(r'./Examples', '%03d' %(self.category))
        if not os.path.exists(self.egDir):
            return
        filelist = glob.glob(os.path.join(self.egDir, '*.jpg'))
        self.tmp = []
        self.egList = []
        random.shuffle(filelist)
        for (i, f) in enumerate(filelist):
            if i == 3:
                break
            im = Image.open(f)
            r = min(SIZE[0] / im.size[0], SIZE[1] / im.size[1])
            new_size = int(r * im.size[0]), int(r * im.size[1])
            self.tmp.append(im.resize(new_size, Image.ANTIALIAS))
            self.egList.append(ImageTk.PhotoImage(self.tmp[-1]))
            self.egLabels[i].config(image = self.egList[-1], width = SIZE[0], height = SIZE[1])
        self.loadImage()
        print('%d images loaded from %s' %(self.total, s))  # By Tomonori12

    def loadImage(self):
        # load image
        imagepath = self.imageList[self.cur - 1]
        self.img = Image.open(imagepath)
        self.tkimg = ImageTk.PhotoImage(self.img)
        self.mainPanel.config(width = max(self.tkimg.width(), 400), height = max(self.tkimg.height(), 400))
        self.mainPanel.create_image(0, 0, image = self.tkimg, anchor=NW)
        self.progLabel.config(text = "%04d/%04d" %(self.cur, self.total))

        # load labels
        self.clearBBox()
        self.imagename = os.path.split(imagepath)[-1].split('.')[0] 
        '''
        print(os.path.split(imagepath)) #('./Images/001', 'test.jpg')
        print(os.path.split(imagepath)[-1]) # test.jpg
        print(os.path.split(imagepath)[-1].split('.')[0]) #test
        '''
        labelname = self.imagename + '.txt'
        self.labelfilename = os.path.join(self.outDir, labelname)
        #print(self.labelfilename) labelfilenquartzame ./Labels/001/test.txt
        bbox_cnt = 0
        if os.path.exists(self.labelfilename):
            with open(self.labelfilename) as f:
                for (i, line) in enumerate(f):#i:行数 line:内容
                    if i == 0:
                        bbox_cnt = int(line.strip())#strip()空白文字の削除してintにキャスト\
                        print(bbox_cnt)
                        continue

                    #original
                    tmp = [t.strip() for t in line.split(',')]#数値配列に変換
                    print(tmp)
                    tmpCoord =  list(map(int, tmp[1:5]))
                    tmpClass = tmp[5]
                    tmpColor = 0
                    #colorを決める
                    '''
                    if tmpClass == self.classNames[0]:
                        tmpColor = 0
                    elif tmpClass == self.classNames[1]:
                        tmpColor = 1
                    elif tmpClass == self.classNames[2]:
                        tmpColor = 2
                    elif tmpClass == self.classNames[3]:
                        tmpColor = 3
                    '''
                    tmpColor = self.classNames.index(tmpClass)
                   
##                    print(tmp)  # By Tomonori12
                    self.bboxList.append(tuple(tmp))
                    #一部original カラーをtmp[5]から決める
                    tmpId = self.mainPanel.create_rectangle(tmpCoord[0], tmpCoord[1], \
                                                            tmpCoord[2], tmpCoord[3], \
                                                            width = 2, \
                                                            outline = COLORS[tmpColor])
                    self.bboxIdList.append(tmpId)
                    self.listbox.insert(END, '(%d, %d) -> (%d, %d)--%s' %(tmpCoord[0],tmpCoord[1],tmpCoord[2],tmpCoord[3],tmpClass))
                    self.listbox.itemconfig(len(self.bboxIdList) - 1, fg = COLORS[tmpColor])

    def saveImage(self):
        with open(self.labelfilename, 'w') as f:
            f.write('%d\n' %len(self.bboxList))
            for bbox in self.bboxList:
                f.write(','.join(map(str, bbox)) + '\n')#文字列に変換してからjoin
        print('Image No. %d saved' %(self.cur))  # By Tomonori12


    def mouseClick(self, event):
        if self.filepathEntry.get() == '':
            tkinter.messagebox.showinfo("Alert", "Input file path , lower left")
            return 0
    
        if self.STATE['click'] == 0:
            self.STATE['x'], self.STATE['y'] = event.x, event.y#x座標,y座標を格納
        else:
            x1, x2 = min(self.STATE['x'], event.x), max(self.STATE['x'], event.x)
            y1, y2 = min(self.STATE['y'], event.y), max(self.STATE['y'], event.y)
            #選択中のクラスを取得
            index = self.classListbox.curselection()[0]
            #original bboxListに書き込むファイルパスを任意のものにする
            self.labelfilenameOpt = self.filepathEntry.get()
            #entryからファイル名を取得できていることを保証する
            self.bboxList.append((self.labelfilenameOpt+self.imagename+'.jpg',x1, y1, x2, y2,self.classNames[index]))
            self.bboxIdList.append(self.bboxId)
            self.bboxId = None
            self.listbox.insert(END, '(%d, %d) -> (%d, %d)--%s' %(x1, y1, x2, y2,self.classNames[index]))
            self.listbox.itemconfig(len(self.bboxIdList) - 1, fg = COLORS[self.classListbox.curselection()[0]])
        self.STATE['click'] = 1 - self.STATE['click']

    def mouseMove(self, event):
    
        self.disp.config(text = 'x: %d, y: %d' %(event.x, event.y))
        if self.tkimg:
            if self.hl:
                self.mainPanel.delete(self.hl)
            self.hl = self.mainPanel.create_line(0, event.y, self.tkimg.width(), event.y, width = 2)
            if self.vl:
                self.mainPanel.delete(self.vl)
            self.vl = self.mainPanel.create_line(event.x, 0, event.x, self.tkimg.height(), width = 2)
        if 1 == self.STATE['click']:
            if self.bboxId:
                self.mainPanel.delete(self.bboxId)
            #一部original
            self.bboxId = self.mainPanel.create_rectangle(self.STATE['x'], self.STATE['y'], \
                                                            event.x, event.y, \
                                                            width = 2, \
                                                            outline = COLORS[self.classListbox.curselection()[0]])

    def cancelBBox(self, event):
        if 1 == self.STATE['click']:
            if self.bboxId:
                self.mainPanel.delete(self.bboxId)
                self.bboxId = None
                self.STATE['click'] = 0

    def delBBox(self):
        sel = self.listbox.curselection()
        if len(sel) != 1 :
            return
        idx = int(sel[0])
        self.mainPanel.delete(self.bboxIdList[idx])
        self.bboxIdList.pop(idx)
        self.bboxList.pop(idx)
        self.listbox.delete(idx)

    def clearBBox(self):
        for idx in range(len(self.bboxIdList)):
            self.mainPanel.delete(self.bboxIdList[idx])
        self.listbox.delete(0, len(self.bboxList))
        self.bboxIdList = []
        self.bboxList = []

    def prevImage(self, event = None):
        self.saveImage()
        if self.cur > 1:
            self.cur -= 1
            self.loadImage()

    def nextImage(self, event = None):
        self.saveImage()
        if self.cur < self.total:
            self.cur += 1
            self.loadImage()

    def gotoImage(self):
        idx = int(self.idxEntry.get())
        if 1 <= idx and idx <= self.total:
            self.saveImage()
            self.cur = idx
            self.loadImage()



##    def setImage(self, imagepath = r'test2.png'):
##        self.img = Image.open(imagepath)
##        self.tkimg = ImageTk.PhotoImage(self.img)
##        self.mainPanel.config(width = self.tkimg.width())
##        self.mainPanel.config(height = self.tkimg.height())
##        self.mainPanel.create_image(0, 0, image = self.tkimg, anchor=NW)

if __name__ == '__main__':
    root = Tk()#メインウィンドウの作成
    root.geometry("2000x700")
    tool = LabelTool(root)#メインウィンドウを渡している
    root.resizable(width =  True, height = True)
    root.mainloop()
