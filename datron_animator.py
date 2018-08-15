import re #regular expressions
import matplotlib.pyplot as plt
import time
import math

#Datron animator
progs={"MKSV4K":"N:/Datron 5/Sicherung_2018-05-24/Disp/MKSV4_K.MCR",
       "EB7_V":"C:/Users/m.svoboda/Desktop/EB7_V.MCR",
       "EB7_V_obdelnik":"C:/Users/m.svoboda/Desktop/EB7_V_rechteck.MCR",
       #"CBU":"C:/Users/m.svoboda/Desktop/bsp.mcr",
       }

def is_number(s):
    try:
        float(s)
        return(True)
    except ValueError:
        return(False)

class Datprog:
    def __init__(self,fname):
        self.name=fname
        self.read_file()
        self.get_markierungen()
        self.get_submakros()
        self.stack=[0]
        self.position={"x":[0],"y":[0],"z":[0],"makro":["main"]}
        self.variables={"Zp":0,"Xp":0,"Yp":0,"Araupe":0,"Time":0}#was ist Xp, Yp, Zp?
        self.nullpunktnr=0
        self.nullpunkt={"x":[0,0,0,0,0,0,0,0],"y":[0,0,0,0,0,0,0,0],"z":[0,0,0,0,0,0,0,0]}
        self.akt_makro=["main"]

    def get_path(self):
        return(progs[self.name])

    def read_file(self):
        self.prog=[]

        with open(self.get_path(),"r") as f:
            for line in f:
                self.prog.append(line)
        

    def get_markierungen(self):
        markierungen={}
        for linenum, line in enumerate(self.prog):
            if line.startswith("Markierung"):
                marknr=re.findall(r'\b\d+\b',line)[0] #Markierung Nr
                markline=linenum #Markierung Line
                markierungen[marknr]=markline 
        self.markierungen=markierungen

    def get_submakros(self):
        #returns dictionary {makroname:[startline,endline]}
        submakros={}
        for linenum, line in enumerate(self.prog):
            if line.startswith("("):
                #Submakro start
                startline=linenum
                #Markierung Line
            if line.startswith(")"):
                #Matching submakro end
                endline=linenum
                makroname=re.findall(r'\) (.*);',line)[0] #Submakro name
                submakros[makroname]=[startline,endline]
        self.submakros=submakros

    def step(self,line_number):
        #for line in self.prog:
        nextline=line_number+1 # default

        #identifizierung von main procedure - wenn der stack leer ist 
        submakro_starts=[val[0] for val in list(self.submakros.values())]
        submakro_ends=[val[1] for val in list(self.submakros.values())]
        if len(self.stack)==1 and (line_number in submakro_starts):
            nextline=submakro_ends[submakro_starts.index(line_number)]+1
            return(nextline)        
        
        line=re.findall(r'[^;]*',self.prog[line_number])[0] #remove comments
        #print(line)
        
        if not(re.findall(r'=',line))==[]:
            lhs=re.findall(r'[^=]*',line)[0].strip()
            rhs=re.findall(r'=(.*)',line)[0].strip()
            #print(line)                

            for key in sorted(self.variables,reverse=True):
                rhs=rhs.replace(key,str(self.variables[key]))

            try:
                rhs=eval(rhs)

            except SyntaxError as e:
                print("Zeile übersprungen "+str(e))
            self.variables[lhs]=rhs
            #print(self.variables)

        elif not(re.findall(r'Axyz',line))==[]:
            #print(line)
            elems=line.lstrip().lstrip("Axyz").replace(" ","").split(",")                

            for i,elem in enumerate(elems):
                for key in sorted(self.variables,reverse=True):
                    elem=elem.replace(key,str(self.variables[key]))
                elems[i]=eval(elem)

            self.position["x"].append(elems[1]+self.nullpunkt["x"][self.nullpunktnr])
            self.position["y"].append(elems[2]+self.nullpunkt["y"][self.nullpunktnr])
            self.position["z"].append(elems[3]+self.nullpunkt["z"][self.nullpunktnr])
            self.position["makro"].append(self.akt_makro[-1])
            #print(str(len(self.position["x"]))+" abs x:"+str(self.position["x"][-1])+" y:"+str(self.position["y"][-1]))
            self.update_XYZp()
            
                
        elif not(re.findall(r'Ixyz',line))==[]:
            #print(line)
            elems=line.lstrip().lstrip("Ixyz").replace(" ","").split(",")
            
            for i,elem in enumerate(elems):
                for key in sorted(self.variables,reverse=True):
                    elem=elem.replace(key,str(self.variables[key]))
                elems[i]=eval(elem)
                
            self.position["x"].append(self.position["x"][-1]+elems[1])
            self.position["y"].append(self.position["y"][-1]+elems[2])
            self.position["z"].append(self.position["z"][-1]+elems[3])
            self.position["makro"].append(self.akt_makro[-1])
            #print(str(len(self.position["x"]))+" rel x:"+str(self.position["x"][-1])+" y:"+str(self.position["y"][-1]))
            self.update_XYZp()

        elif not(re.findall(r'Dispoff',line))==[]:
            #print(line)
            elems=line.lstrip().lstrip("Dispoff").replace(" ","").split(",")
            
            for i,elem in enumerate(elems):
                for key in sorted(self.variables,reverse=True):
                    elem=elem.replace(key,str(self.variables[key]))
                elems[i]=eval(elem)

            if elems[1]==180 or elems[5]==0:
                self.position["x"].append(self.position["x"][-1]+elems[5])
                self.position["y"].append(self.position["y"][-1])
                self.position["z"].append(self.position["z"][-1])

            else:
                raise ValueError("Nicht implementiert für diese Angaben von Dispoff" + line)

            self.position["makro"].append(self.akt_makro[-1])
            #print(str(len(self.position["x"]))+" dispoff x:"+str(self.position["x"][-1])+" y:"+str(self.position["y"][-1]))
            self.update_XYZp()
            
        elif not(re.findall(r'Kreis',line))==[]:
            #print(line)
            elems=line.lstrip().lstrip("Kreis").replace(" ","").split(",")
            
            for i,elem in enumerate(elems):
                for key in sorted(self.variables,reverse=True):
                    elem=elem.replace(key,str(self.variables[key]))
                elems[i]=eval(elem)

            aw=float(elems[4])
            ew=float(elems[5])
            d=float(elems[0])
            ws=float(elems[3])

            if aw==270 and ws==-360 and ew==90:                
                self.position["x"].append(self.position["x"][-1]-d/2)                
                self.position["y"].append(self.position["y"][-1]+d/2) 
                self.position["z"].append(self.position["z"][-1])
                self.position["makro"].append(self.akt_makro[-1])

                self.position["x"].append(self.position["x"][-1]+d/2)
                self.position["y"].append(self.position["y"][-1]+d/2)
                self.position["z"].append(self.position["z"][-1])
                self.position["makro"].append(self.akt_makro[-1])

            elif aw==270 and ws==0 and ew==90:                
                self.position["x"].append(self.position["x"][-1]+d/2)
                self.position["y"].append(self.position["y"][-1]+d/2)
                self.position["z"].append(self.position["z"][-1])
                self.position["makro"].append(self.akt_makro[-1])

                self.position["x"].append(self.position["x"][-1]-d/2)
                self.position["y"].append(self.position["y"][-1]+d/2)
                self.position["z"].append(self.position["z"][-1])
                self.position["makro"].append(self.akt_makro[-1])

            elif aw==180 and ws==0 and ew==0:                
                self.position["x"].append(self.position["x"][-1]-d/2)
                self.position["y"].append(self.position["y"][-1]+d/2)
                self.position["z"].append(self.position["z"][-1])
                self.position["makro"].append(self.akt_makro[-1])

                self.position["x"].append(self.position["x"][-1]-d/2)
                self.position["y"].append(self.position["y"][-1]-d/2)
                self.position["z"].append(self.position["z"][-1])
                self.position["makro"].append(self.akt_makro[-1])

            elif aw==0 and ws==0 and ew==180:                
                self.position["x"].append(self.position["x"][-1]+d/2)
                self.position["y"].append(self.position["y"][-1]-d/2)
                self.position["z"].append(self.position["z"][-1])
                self.position["makro"].append(self.akt_makro[-1])

                self.position["x"].append(self.position["x"][-1]+d/2)
                self.position["y"].append(self.position["y"][-1]-d/2)
                self.position["z"].append(self.position["z"][-1])
                self.position["makro"].append(self.akt_makro[-1])

            else:
                raise(ValueError("andere angaben als aw=270, ws=0/-360, ew=90 nicht unterstützt"))            
            #print(str(len(self.position["x"]))+" kreis x:"+str(self.position["x"][-1])+" y:"+str(self.position["y"][-1]))
            self.update_XYZp()

        elif not(re.findall(r'Setrel',line))==[]:
            elems=line.lstrip().lstrip("Setrel").replace(" ","").split(",")

            self.nullpunkt["x"][self.nullpunktnr]=self.position["x"][-1]-float(elems[0])
            self.nullpunkt["y"][self.nullpunktnr]=self.position["y"][-1]-float(elems[1])
            self.nullpunkt["z"][self.nullpunktnr]=self.position["z"][-1]-float(elems[2])

        elif not(re.findall(r'Relsp',line))==[]:
            self.nullpunktnr=int(line[-1])            

        elif not(re.findall(r'^Submakro',line.lstrip()))==[]:
            #run submacro
            
            for key in sorted(self.submakros,reverse=True):
                if key in line:
                    nextline=self.submakros[key][0]
                    self.stack.append(line_number+1)
                    self.akt_makro.append(key)
                    break

        elif not(re.findall(r'^\)',line))==[]:
            #return control
            nextline=self.stack.pop()
            self.akt_makro.pop()

        return(nextline)

    def update_XYZp(self):
        self.variables["Xp"]=self.position["x"][-1]-self.nullpunkt["x"][self.nullpunktnr]
        self.variables["Yp"]=self.position["y"][-1]-self.nullpunkt["y"][self.nullpunktnr]
        self.variables["Zp"]=self.position["z"][-1]-self.nullpunkt["z"][self.nullpunktnr]

    def go_through(self):
        nextline=self.step(0)

        while len(self.stack)>0:
            if nextline==len(self.prog) and len(self.stack)==1:
                break

            nextline=self.step(nextline)

            if len(self.stack)>20:
                break

def anim(datronObjekt):
    import numpy as np
    import matplotlib.pyplot as plt
    from matplotlib.animation import FuncAnimation

    fig, ax = plt.subplots()
    xdata, ydata = [], []
    ln, = plt.plot([], [], 'bo', animated=True)#go

    def init():
        ax.set_xlim(min(datronObjekt.position["x"])-10, max(datronObjekt.position["x"])+10)
        ax.set_ylim(min(datronObjekt.position["y"])-10, max(datronObjekt.position["y"])+10)
        ln.set_data([], [])
        return ln,

    def update(frame):
        #print(frame)
        #print(datronObjekt.position["x"][frame])
        #xdata.append(datronObjekt.position["z"][frame])
        #ydata.append(datronObjekt.position["y"][frame])
        xdata=datronObjekt.position["x"][frame]
        ydata=datronObjekt.position["y"][frame]
        ln.set_data(xdata, ydata)
        return ln,

    ani = FuncAnimation(fig, update, frames=np.arange(1,len(datronObjekt.position["x"])),
                        init_func=init, blit=True,interval=100)
    plt.show()    


def anim2(datronObjekt):
    import numpy as np
    import matplotlib.pyplot as plt
    from matplotlib.animation import FuncAnimation

    fig = plt.figure()
    ax=fig.add_subplot(1,1,1)
    ax.set_xlim(min(datronObjekt.position["x"])-10, max(datronObjekt.position["x"])+10)
    ax.set_ylim(min(datronObjekt.position["y"])-10, max(datronObjekt.position["y"])+10)

    xdata, ydata = [], []
    global line

    line=None
    

    def update(frame):
        global line
        
        xdata=datronObjekt.position["x"][frame]
        ydata=datronObjekt.position["y"][frame]

        if line is not None:
            line.set_color("gray")
        
        line,=ax.plot(xdata, ydata,color="red")

    ani = FuncAnimation(fig, update, frames=np.arange(1,len(datronObjekt.position["x"])),blit=True,interval=100)
    plt.show()


  
def run_prog(prog):
    dat=Datprog(prog)
    dat.go_through()
    plt.subplot(111)
    plt.plot(dat.position["x"],dat.position["y"],"b-")
    for i,xy in enumerate(zip(dat.position["x"],dat.position["y"])):
        plt.annotate(str(i+1),xy=xy,fontsize=8)    

    plt.ylabel("Y")
    plt.xlabel("X")
    plt.show()
    
    anim(dat)
    x_0=0
    y_0=0
    length=0
    
    for x,y in zip(dat.position["x"],dat.position["y"]):
        length+=math.sqrt((x-x_0)*(x-x_0)+(y-y_0)*(y-y_0))
        x_0=x
        y_0=y

    print("länge: "+str(length))

    
run_prog("EB7_V_obdelnik")
#run_prog("EB7_V")
#run_prog("MKSV4K")



    


