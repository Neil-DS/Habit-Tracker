import tkinter as tk
from ctypes import windll
import calendar
from threading import Timer

GWL_EXSTYLE=-20
GWL_STYLE=-16

WS_EX_APPWINDOW=0x00040000
WS_EX_TOOLWINDOW=0x00000080
WS_EX_LAYERED=0x00080000

WS_BORDER=0x00800000
WS_CAPTION=0x00C00000
WS_MINIMIZEBOX=0x00020000
WS_MAXIMIZEBOX=0x00010000
WS_SYSMENU=0x00080000
WS_DLGFRAME=0x00400000
WS_TABSTOP=0x00010000

#pywin32 is something to look at, it's the win32 api in python which you'll need to minimize to system tray or other fancy windows stuff
def set_appwindow(root):
    hwnd = windll.user32.GetParent(root.winfo_id())
    style = windll.user32.GetWindowLongPtrW(hwnd, GWL_STYLE)
    #print(bin(style), type(style))
    #style = style | WS_EX_APPWINDOW
    #style = style & ~(WS_CAPTION | WS_MINIMIZEBOX | WS_MAXIMIZEBOX | WS_SYSMENU)
    #style = style | WS_DLGFRAME
    #print(bin(style), type(style))
    #style = style | WS_TABSTOP
    #style = style & ~WS_EX_TOOLWINDOW
    #style = style | WS_EX_APPWINDOW
   
    #res = windll.user32.SetWindowLongPtrW(hwnd, GWL_EXSTYLE, style)
    #res = windll.user32.SetWindowLongPtrW(hwnd, GWL_STYLE, style)
    # re-assert the new window style
    root.wm_withdraw()
    root.after(10, lambda: root.wm_deiconify())

class App():
    
    def __init__(self):
        self.root = tk.Tk()
      
        self.root.configure(bg='gray75', borderwidth=0)
        self.frame = tk.Frame(self.root, borderwidth=0, relief=tk.RAISED, bg='gray75')
        self.frame.pack_propagate(False)
        self.root.geometry('1240x960+100+100')
        self.root.attributes("-transparentcolor", 'gray75')
        self.frame.pack()
        self.canvas = tk.Canvas(self.frame, height=240, width=960, borderwidth=0, bg='gray75', highlightbackground='gray75')
        self.canvas.grid(column=0, row=0, sticky=(tk.N, tk.W, tk.E, tk.S))

        self.root.overrideredirect(True)
        self.root.after(10, lambda: set_appwindow(self.root))

        #change these to on select
        self.root.bind("<FocusIn>", self.showBorder)
        self.root.bind("<FocusOut>", self.hideBorder)
        self.root.bind("<Button-1>", self.leftMouse)
        self.root.bind("<B1-Motion>", self.leftDrag)
        self.root.bind('<Escape>', self.exitApp)

        self.canvas.bind("<Enter>", self.on_enter)
        self.canvas.bind("<Leave>", self.on_leave)
        
        #will want a class that contains a rectangle, so you can have specific days
        
        self.readFile()
        print(self.dateMap)
        self.getDays()

    #want to display the info of the box hovered over after sitting still-ish within a box.
    def popupthing(self):
        print('hey')

    #need to get the info of a specific box
    def on_enter(self, event):
        self.t = Timer(1.0, self.popupthing)
        self.t.start()
        xOff = self.canvas.winfo_pointerx() - (self.root.winfo_x() + self.frame.winfo_x())
        yOff = self.canvas.winfo_pointery() - (self.root.winfo_y() + self.frame.winfo_y()) 
        
        self.popupHandle = self.canvas.create_rectangle(xOff, yOff,
                                                        xOff+50, yOff+50,
                                                        fill='pink', outline='yellow')

        rectSize = 22

        #how are boxes related to the info in the file?
        #relate the box on screen to a date
        
        
        #between 0-17 rectsize(15)+2(spacing) is the first column
        #between 0-17 is the first row
        #row 2 column 3 is where the first value i currently have something
        print(self.root.winfo_x(), self.root.winfo_y(), self.frame.winfo_x(), self.frame.winfo_y(), self.canvas.winfo_x(), self.canvas.winfo_y())
        
        #now you know how each row is related to a box on screen.
        column = int((self.canvas.winfo_pointerx() - self.root.winfo_x() - self.frame.winfo_x())/rectSize)
        row = int((self.canvas.winfo_pointery() - self.root.winfo_y() - self.frame.winfo_y())/rectSize)
        
        #how do i know which month I'm in? also weeks overlap in months. there's a 6th week in jan which is the same as first week in feb.
        month = int(column/6)
        
        print('Column: ', column,
              'Row: ', row)

        #now I need how each box is related to the date
        #01/01/21 should be c:0r:5
        #should be able to access it from the cal?
        datesCal = calendar.Calendar(6).yeardatescalendar(2021, width=12)

        print(datesCal[0][month][column%6][row])
        
        self.popupHandleText = self.canvas.create_text(xOff+15, yOff+15, text=self.dateMap['13/01/21'] )   
        

    def on_leave(self, event):
        self.canvas.delete(self.popupHandle)
        self.canvas.delete(self.popupHandleText)
        try:
            self.t.start()
        except:
            self.t.cancel()

    #gets the year from the calander and draws some rects on the canvas.
    #drawing currently just puts all the months into a straight line and kinda of seperates the months/days/week with some spacing
    def getDays(self):
         c = calendar.Calendar(6) #6=sunday first day of week
         datesCal = c.yeardatescalendar(2021, width=12)
         cal = c.yeardayscalendar(2021, width=12)

         rectSize = 20
         rectSpacing = rectSize + 2
         monthSpacing = 0 #base month spacing determined by how many days and size of rects etc(this will always start at 0) unless you want to offset
         #the drawing from the canvas(from the left) by some amount of pixels for some reason.
         spaceBetweenMonths = 2 #additional spacing between each month

         self.fillColor = '#AAFFAA' #will want to change the fillcolor by day depending on how much activity was done
         outlineColor = 'black'

         #make a bunch of objects to represent the day
         
         #right now you create a structure based on what's in the file, then lookup if the date every frame and change the color.
         #you want a structure with all the days in it, and info about that dates, then loop over that structure.

         #create a map for the year, searched by dates?
         #check the file once for info relating to the dates and add it to the structure.
         #draw the structure based on that info, keeping in mind being able to find each block efficiently with the mouse.

         print('--------------START OF MAP STRUCTURE-------------\n')
         #datescal has the date info you need. need to relate it to a draw box + add info
         #print(datesCal[0][0], len(datesCal[0][0]))

         
         



         print('\n--------------END OF MAP STRUCTURE-------------')

         

         for month in range(len(cal[0])):
             #print(month)            
             #print(len(cal[0][month])-1, monthSpacing)             
             for week in range(len(cal[0][month])):
                 #print('week')
                 for day in range(len(cal[0][month][week])):                     
                     dateString = "{:02d}".format(cal[0][month][week][day]) + '/' + "{:02d}".format(month+1) + '/21'
                     self.determineColor(dateString)
                         
                     if(cal[0][month][week][day] != 0):
                         self.canvas.create_rectangle(week*rectSpacing+(monthSpacing), day*rectSpacing,
                                                      (monthSpacing)+(week*rectSpacing+rectSize), day*rectSpacing+rectSize,
                                                      fill=self.fillColor, outline=outlineColor)
                         
             monthSpacing = monthSpacing + ((len(cal[0][month])-1) * rectSpacing) + spaceBetweenMonths
             #if the last day of the month is a saturday add some more spacing to keep those months 2 from overlapping
             if(cal[0][month][-1][-1] != 0):
                 monthSpacing = monthSpacing + rectSpacing

    #
    def determineColor(self, date):
        if(self.findDate(date)):
            values = self.dateMap[date].values()
            n = 0
            for v in values:
                n += int(v[0:2])
            #print(n, 16-n)
            n = 16-n #makes higher value lower for the color to be deeper
            #TODO: if the total hours per day is larger than 16 it'll give an error.        
            #n = int(n/16 * 10)
            #self.fillColor = '#' + '{:x}'.format(n) + '0' + 'FF' + '{:x}'.format(n) + '0'
            #print(n)
            self.fillColor = '#' + '00' + '{:x}'.format(n)*2 + '00'
            print(self.fillColor)
            
        else:
            self.fillColor = '#FFFFFF'
        


    def findDate(self, date):
        return date in self.dateMap

    #for creating the object in memory for drawing the squares
    #do this only once on startup so don't have to read file each draw call
    def readFile(self):
        
        startDateFound = False #when you find a date save the line untill you find the corresponding </date for closing
        idDateName = 0

        habitList = []

        yearInfo = {}
        self.dateMap = {}
        
        with open('teststorage.xml', 'r') as f:
            for line in f:
                dateStart = line.find('<date')
                dateEnd = line.find('</date>')

                habitIDStart = line.find('<IDs>')

                #get the list of habits in the file
                if(habitIDStart > -1):
                    habitIDStart = habitIDStart + 5
                    comma = line.find(',')                    
                    while(comma > -1):                       
                        firstHabitID = line[habitIDStart:comma]
                        habitList.append(firstHabitID)
                        #finds next comma and sets it as place to start
                        habitIDStart = comma +1
                        comma = line.find(',', comma+1)

                    #after no more commas, go to end of ID                    
                    IDend = line.find('</IDs>')
                    lastHabitID = line[habitIDStart:IDend]
                    habitList.append(lastHabitID)
                        
                    print('names of habits: ', habitList)
               

                #find the dates in the file and create a map with habits
                if(dateStart > -1):
                    startDateFound = True #for determining if the line im on is inbetween <date></date> tags, and if so to check for habit keypharase
                    
                    dateID = line.find('id="', dateStart)
                    dateEnd = line.find('"', dateID+4)
                    
                    idDateName = line[dateID+4:dateEnd]
                    
                    firstHabitIndex = line.find('>') + 1
                    lastHabitIndex = line.find('<', firstHabitIndex)
                    
                    habitNameList = line[firstHabitIndex:lastHabitIndex].split(',')

                    continue #skips the rest of the loop (to not append unnecessary info)

                #clear the map for the date
                elif(dateEnd > -1):
                    startDateFound = False
                    self.dateMap[idDateName] = yearInfo
                    yearInfo = {} #clear it after

                
                if(startDateFound == True):
                    for each in habitList:
                        oneoftheIDs = line.find(each)
                        if(oneoftheIDs > -1):
                            #print(oneoftheIDs, each)
                            habitTime = oneoftheIDs+len(each)+1
                            yearInfo[each] = line[habitTime:line.find('</')]
                            #print(yearInfo)
               
            f.close()

                 
    #get the offset on screen for the widget to allow for draging from any point of clicking
    def leftMouse(self, event):
        firstXIndex = self.root.geometry().rfind('+')
        firstYIndex = self.root.geometry().rfind('+', 0, firstXIndex)

        self.firstXOffset = self.root.geometry()[firstYIndex:firstXIndex]
        self.firstYOffset = self.root.geometry()[firstXIndex:]

        #print(self.firstXOffset, self.firstYOffset)
        #print(event.x_root, event.y_root)

        self.prevMouseX = event.x_root
        self.prevMouseY = event.y_root

        #print(self.root.winfo_width(), self.root.winfo_height())
                 
    def leftDrag(self, event):      
        #newX = int(self.firstXOffset) - event.x_root
        #newY = int(self.firstYOffset) - event.y_root

        newX2 = event.x_root - self.prevMouseX + int(self.firstXOffset)
        newY2 = event.y_root - self.prevMouseY + int(self.firstYOffset)
        
        #print(newX2, newY2)
        
        self.root.geometry('%dx%d+%d+%d' % (1240, 960, newX2, newY2))
     
                 
    def showBorder(self, event):
        self.canvas.configure(highlightbackground='pink')
        #self.frame.configure(borderwidth=5)

    def hideBorder(self, event):
        self.canvas.configure(highlightbackground='gray75')  

    def exitApp(self, event):
        self.root.destroy()

   
app = App() 

app.root.mainloop()
