import re #regular expressions
import matplotlib.pyplot as plt
import time
import math
import pandas as pd
import random
import configparser
import numpy as np

pd.set_option('expand_frame_repr', False)
pd.set_option('display.max_rows', 500)

config=configparser.ConfigParser(comment_prefixes='#', allow_no_value=True, strict=False)

icat = {'DatronKL1': 'I_CAT_KL1.ini', 'DatronKL4_V': 'I_CAT_KL4_V.ini', 'DatronKL4_K': 'I_CAT_KL_4_KL.ini',
        'DatronKL3': 'I_CAT_KL3.ini', 'DatronKL2': 'I_CAT_KL2.ini'}

'''
Read I_Cat.ini for the configured global positions
Notable global variables (example):

[CsMCoord]
MCoordCount=10
MCoordTabAx_00_0=0
MCoordTabAx_00_1=1
MCoordTabAx_00_2=2
MCoordTabPos_00_0=251232
MCoordTabPos_00_1=-21648
MCoordTabPos_00_2=0
MCoordTabWT_00=1
MCoordTabCom_00=Nadelversatz IVD links
MCoordTabAx_01_0=0
MCoordTabAx_01_1=1
MCoordTabAx_01_2=2
MCoordTabPos_01_0=-11610510
MCoordTabPos_01_1=-126830
MCoordTabPos_01_2=4028890
MCoordTabWT_01=1
MCoordTabCom_01=Nadelversatz IVD rechts
MCoordTabAx_02_0=0
MCoordTabAx_02_1=1
MCoordTabAx_02_2=2
MCoordTabPos_02_0=120200
MCoordTabPos_02_1=-528400
MCoordTabPos_02_2=3904200
MCoordTabWT_02=0
MCoordTabCom_02=Lichttaster
MCoordTabAx_03_0=0
MCoordTabAx_03_1=1
MCoordTabAx_03_2=2
MCoordTabPos_03_0=5531745
MCoordTabPos_03_1=-1894532
MCoordTabPos_03_2=3942627
MCoordTabWT_03=0
MCoordTabCom_03=Lasersensor OADM

[CsPos]
Checksum=49208
D_Park_0=0
D_Park_1=0
D_Park_2=0
D_Park_3=0
D_Park_4=0
D_Park_5=0
D_Position_01_0=26286351
D_Position_01_1=-8138713
D_Position_01_2=-11121303
D_Position_01_3=0
D_Position_01_4=0
D_Position_01_5=0
D_Kennung_01=2
D_Position_02_0=41286351
D_Position_02_1=-8138713
D_Position_02_2=-9242545
D_Position_02_3=0
D_Position_02_4=0
D_Position_02_5=0
D_Kennung_02=2
D_Position_03_0=27050600
D_Position_03_1=-8966791
D_Position_03_2=-11103319
D_Position_03_3=0
D_Position_03_4=0
D_Position_03_5=0
D_Kennung_03=2
D_Position_04_0=42050600
D_Position_04_1=-8966791
D_Position_04_2=-11103319
D_Position_04_3=0
D_Position_04_4=0
D_Position_04_5=0
D_Kennung_04=2
'''   

import numpy as np

def cart2pol(x, y):
    rho = np.sqrt(x**2 + y**2)
    phi = np.arctan2(y, x)
    return(rho, phi)

def pol2cart(rho, phi):
    x = rho * np.cos(phi)
    y = rho * np.sin(phi)
    return(x, y)

def heav(number):
    if number>=0:
        return 1
    else:
        return 0
       
def cos(number):
    return math.cos(2*3.14*number/360)

def sin(number):
    return math.sin(2*3.14*number/360)

def zero(number):
    if number==0:
        return 0
    else:
        return 1

def floor (number):
    return math.floor(number)

def ceil (number):
    return math.ceil(number)

def Floor (number):
    return math.floor(number)

def Ceil (number):
    return math.ceil(number)

def is_number(s):
    try:
        float(s)
        return(True)
    except ValueError:
        return(False)

class Datprog:
    def __init__(self,mcrfilecontent,datron='DatronKL2'):
        try:
            config.read(icat[datron],encoding= "cp858")#encoding='ansi' funguje na win?
        except UnicodeDecodeError as er:
            print("icat_parse_error "+str(er))
            pass
        self.name="test"
        self.mcrfilecontent=mcrfilecontent
        self.prog = []
        self.read_file()
        self.get_markierungen()
        self.get_submakros()
        self.stack=[0]
        self.position={"x":[],"y":[],"z":[],"makro":[],"coordinate_system":[]}
        self.gl_position={"x":[],"y":[],"z":[]}
        self.actual_position={"x":[],"y":[],"z":[]}
        self.variables={"Zp":0,"Xp":0,"Yp":0,"Araupe":0,"Time":0,"Pi":math.pi}#was ist *p - aktuelle Koordinate (Axyz kann so manche Koordinaten als relativ akzeptieren)
        self.nullpunktnr=0
        self.nullpunkt={"x":[0,0,0,0,0,0,0,0],"y":[0,0,0,0,0,0,0,0],"z":[0,0,0,0,0,0,0,0]}
        self.akt_makro=["main"]
        self.coordsys="0"

    def get_path(self):
        return(progs[self.name])

    def read_file(self):

        for line in self.mcrfilecontent.split("\n"):
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
        #print(self.stack)

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
                print("Syntax Error: Zeile übersprungen "+str(e))
                print(line)
            except NameError as e:
                print("Name Error: Zeile übersprungen "+str(e))
            
            self.variables[lhs]=rhs

        elif not(re.findall(r'Axyz',line))==[]:
            elems=line.lstrip().lstrip("Axyz").replace(" ","").split(",")                

            for i,elem in enumerate(elems):
                for key in sorted(self.variables,reverse=True):
                    elem=elem.replace(key,str(self.variables[key]))
                elems[i]=eval(elem)

            self.position["x"].append(elems[1]+self.nullpunkt["x"][self.nullpunktnr])
            self.position["y"].append(elems[2]+self.nullpunkt["y"][self.nullpunktnr])
            self.position["z"].append(elems[3]+self.nullpunkt["z"][self.nullpunktnr])
            self.position["makro"].append(self.akt_makro[-1])
            self.position["coordinate_system"].append(self.coordsys)
            
            self.update_XYZp()
               
        elif not(re.findall(r'Ixyz',line))==[]:
            elems=line.lstrip().lstrip("Ixyz").replace(" ","").split(",")
            
            for i,elem in enumerate(elems):
                for key in sorted(self.variables,reverse=True):
                    elem=elem.replace(key,str(self.variables[key]))
                elems[i]=eval(elem)
                
            self.position["x"].append(self.position["x"][-1]+elems[1])
            self.position["y"].append(self.position["y"][-1]+elems[2])
            self.position["z"].append(self.position["z"][-1]+elems[3])
            self.position["makro"].append(self.akt_makro[-1])
            self.position["coordinate_system"].append(self.coordsys)
            
            self.update_XYZp()

        elif not(re.findall(r'Position',line))==[]:
            elems=line.lstrip().lstrip("Position").replace(" ","").split(",")
            
            for i,elem in enumerate(elems):
                for key in sorted(self.variables,reverse=True):
                    elem=elem.replace(key,str(self.variables[key]))
                elems[i]=eval(elem)

            pos_number=str(100+int(elems[0]))[-2:]

            if elems[1]==0:
                self.position["x"].append(float(config["CsPos"]["d_position_"+pos_number+"_0"])/100000)
                self.position["y"].append(float(config["CsPos"]["d_position_"+pos_number+"_1"])/100000)
                self.position["z"].append(float(config["CsPos"]["d_position_"+pos_number+"_2"])/100000)
                self.position["makro"].append(self.akt_makro[-1])
                self.position["coordinate_system"].append(self.coordsys)
                self.update_XYZp()
                
            if elems[1]==2:
                self.nullpunkt["x"][self.nullpunktnr]=float(config["CsPos"]["d_position_"+pos_number+"_0"])/100000
                self.nullpunkt["y"][self.nullpunktnr]=float(config["CsPos"]["d_position_"+pos_number+"_1"])/100000
                self.nullpunkt["z"][self.nullpunktnr]=float(config["CsPos"]["d_position_"+pos_number+"_2"])/100000
                
                self.update_XYZp()

        elif not(re.findall(r'Mkoord',line))==[]:
            elems=line.lstrip().lstrip("Mkoord").replace(" ","").split(",")
            self.coordsys=str(int(elems[0])-1)
            #coordsys wird in der cat.ini von 0 indexiert, deshalb -1

        elif not(re.findall(r'Dispon',line))==[]:
            elems=line.lstrip().lstrip("Dispon").lstrip("_links").lstrip("_rechts").replace(" ","").split(",")
            
            for i,elem in enumerate(elems):
                for key in sorted(self.variables,reverse=True):
                    elem=elem.replace(key,str(self.variables[key]))
                try:
                    elems[i]=eval(elem)
                except NameError as e:
                    print("Name Error: "+str(e)+"\n"+line)
                
            self.position["x"].append(self.position["x"][-1])
            self.position["y"].append(self.position["y"][-1])
            self.position["z"].append(elems[10]+self.nullpunkt["z"][self.nullpunktnr])
            self.position["makro"].append(self.akt_makro[-1])
            self.position["coordinate_system"].append(self.coordsys)

            self.position["x"].append(self.position["x"][-1]+pol2cart(elems[2],math.radians(elems[1]+180))[0])
            self.position["y"].append(self.position["y"][-1]+pol2cart(elems[2],math.radians(elems[1]+180))[1])
            self.position["z"].append(self.position["z"][-1]-elems[3])
            self.position["makro"].append(self.akt_makro[-1])
            self.position["coordinate_system"].append(self.coordsys)

            self.position["x"].append(self.position["x"][-1]-pol2cart(elems[2],math.radians(elems[1]+180))[0])
            self.position["y"].append(self.position["y"][-1]-pol2cart(elems[2],math.radians(elems[1]+180))[1])
            self.position["z"].append(self.position["z"][-1]+elems[3])
            self.position["makro"].append(self.akt_makro[-1])
            self.position["coordinate_system"].append(self.coordsys)
            
            self.update_XYZp()

        elif not(re.findall(r'Dispoff',line))==[]:
            #Dispoff - Andockbewegungen nicht miteinbegriffen!
            elems=line.lstrip().lstrip("Dispoff").replace(" ","").split(",")
            
            for i,elem in enumerate(elems):
                for key in sorted(self.variables,reverse=True):
                    elem=elem.replace(key,str(self.variables[key]))
                elems[i]=eval(elem)

            self.position["x"].append(self.position["x"][-1]+pol2cart(elems[5],math.radians(elems[1]+180))[0])
            self.position["y"].append(self.position["y"][-1]+pol2cart(elems[5],math.radians(elems[1]+180))[1])
            self.position["z"].append(self.position["z"][-1]+elems[6])
            self.position["makro"].append(self.akt_makro[-1])
            self.position["coordinate_system"].append(self.coordsys)
            
            self.position["x"].append(self.position["x"][-1])
            self.position["y"].append(self.position["y"][-1])
            self.position["z"].append(elems[8]+self.nullpunkt["z"][self.nullpunktnr])
            self.position["makro"].append(self.akt_makro[-1])
            self.position["coordinate_system"].append(self.coordsys)
            self.update_XYZp()
            
        elif not(re.findall(r'Kreis',line))==[]:
            elems=line.lstrip().lstrip("Kreis").replace(" ","").split(",")
            
            for i,elem in enumerate(elems):
                for key in sorted(self.variables,reverse=True):
                    elem=elem.replace(key,str(self.variables[key]))
                try:
                    elems[i]=eval(elem)
                except NameError as e:
                    print("Name Error: Zeile übersprungen "+str(e))
                    return(nextline)

            aw=int(elems[4]) #Anfangswinkel
            ew=int(elems[5]) #Endwinkel
            d=float(elems[0]) #Durchmesser
            zb=float(elems[10]) #Steigung pro Umdrehung
            r=d/2 #Radius
            ws=int(elems[3]) #Richtung: 0: anti-clockwise, -360: clockwise

            posx0=self.position["x"][-1]
            posy0=self.position["y"][-1]
            posz0=self.position["z"][-1]

            anglestep=5
            
            if ws==-360:
                if aw<ew:
                    aw=aw+360
                    
                for angle in range(aw,ew-anglestep,-anglestep):
                    self.position["x"].append(posx0-r*math.cos(math.radians(aw))+pol2cart(r,math.radians(angle))[0])                
                    self.position["y"].append(posy0-r*math.sin(math.radians(aw))+pol2cart(r,math.radians(angle))[1]) 
                    self.position["z"].append(posz0+(angle-aw)*zb/360)
                    self.position["makro"].append("kreis")
                    self.position["coordinate_system"].append(self.coordsys)

            elif ws==0:
                if ew<aw:
                  ew=ew+360
                for angle in range(aw,ew+anglestep,anglestep):
                    self.position["x"].append(posx0-r*math.cos(math.radians(aw))+pol2cart(r,math.radians(angle))[0])                
                    self.position["y"].append(posy0-r*math.sin(math.radians(aw))+pol2cart(r,math.radians(angle))[1]) 
                    self.position["z"].append(posz0+(angle-aw)*zb/360) 
                    self.position["makro"].append("kreis")
                    self.position["coordinate_system"].append(self.coordsys)
            else:
                raise(ValueError("andere angaben als ws=0/-360 nicht unterstützt"))            
            self.update_XYZp()

        elif not(re.findall(r'Setrel',line))==[]:
            elems=line.lstrip().lstrip("Setrel").replace(" ","").split(",")

            self.nullpunkt["x"][self.nullpunktnr]=self.position["x"][-1]-float(elems[0])
            self.nullpunkt["y"][self.nullpunktnr]=self.position["y"][-1]-float(elems[1])
            self.nullpunkt["z"][self.nullpunktnr]=self.position["z"][-1]-float(elems[2])

        elif not(re.findall(r'Relsp',line))==[]:
            self.nullpunktnr=int(line[-1])

        elif not(re.findall(r'Mal',line))==[]:
            #print(line)
            #print(self.variables)
            times=self.variables[line.lstrip().lstrip("Mal").replace(" ","").split(",")[0]]
            #print(times)
            makroline=self.prog[line_number+1]
            for i in range(times-1):
                #print(makroline)
                self.prog.insert(line_number+1,makroline)

            if times<=0:
                return(nextline+1)

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

    def calculate_global(self):        
        for pos,sys in zip(self.position["x"],self.position["coordinate_system"]):
            self.gl_position["x"].append(pos+float(config["CsMCoord"]["MCoordTabPos_0"+sys+"_0"])/100000)

        for pos,sys in zip(self.position["y"],self.position["coordinate_system"]):
            self.gl_position["y"].append(pos+float(config["CsMCoord"]["MCoordTabPos_0"+sys+"_1"])/100000)

        for pos,sys in zip(self.position["z"],self.position["coordinate_system"]):
            self.gl_position["z"].append(pos+float(config["CsMCoord"]["MCoordTabPos_0"+sys+"_2"])/100000)

    def calculate_coord(self,coordsys):
        self.actual_position["x"]=[]
        self.actual_position["y"]=[]
        self.actual_position["z"]=[]

        for x,y,z in zip(self.gl_position["x"],self.gl_position["y"],self.gl_position["z"]):
            self.actual_position["x"].append(x-float(config["CsMCoord"]["MCoordTabPos_0"+coordsys+"_0"])/100000)
            self.actual_position["y"].append(y-float(config["CsMCoord"]["MCoordTabPos_0"+coordsys+"_1"])/100000)
            self.actual_position["z"].append(z-float(config["CsMCoord"]["MCoordTabPos_0"+coordsys+"_2"])/100000)


def anim(datronObjekt):
    import numpy as np
    import matplotlib.pyplot as plt
    from matplotlib.animation import FuncAnimation

    fig, ax = plt.subplots()
    xdata, ydata = [], []
    ln, = plt.plot([], [], 'bo',markersize=1, animated=True)#go

    def init():
        ax.set_xlim(min(datronObjekt.position["x"])-10, max(datronObjekt.position["x"])+10)
        ax.set_ylim(min(datronObjekt.position["z"])-10, max(datronObjekt.position["z"])+10)
        ln.set_data([], [])
        return ln,

    def update(frame):
        #print(frame)
        #print(datronObjekt.position["x"][frame])
        xdata.append(datronObjekt.position["x"][frame]+0.5*random.random())
        ydata.append(datronObjekt.position["z"][frame]+0.5*random.random())
        #xdata=datronObjekt.position["x"][frame]
        #ydata=datronObjekt.position["y"][frame]
        ln.set_data(xdata, ydata)
        return ln,

    ani = FuncAnimation(fig, update, frames=np.arange(1,len(datronObjekt.position["x"])),
                        init_func=init, blit=True,interval=10)
    plt.show()    


pd.set_option('expand_frame_repr', False)
pd.set_option('display.max_rows', 1000)
  
def run_prog(prog,yaxis="y",xaxis="x",datron="DatronKL3"):
    dat=Datprog(prog,datron)
    dat.go_through()
    dat.calculate_global()
    
    print(len(dat.position["x"]))

    df=pd.DataFrame(dat.position)
    df = df[df['makro'] != "kreis"].reset_index()
    print(df)

    dat.calculate_coord("2")#lasersensor?
    plt.scatter(dat.actual_position[xaxis],dat.actual_position[yaxis],s=2,zorder=1,c='C1')
    plt.plot(dat.actual_position[xaxis],dat.actual_position[yaxis], 'C1', lw=1,zorder=2)

    dat.calculate_coord("3")#lasersensor
    plt.scatter(dat.actual_position[xaxis],dat.actual_position[yaxis],s=2,zorder=1,c='C2')
    plt.plot(dat.actual_position[xaxis],dat.actual_position[yaxis], 'C2', lw=1,zorder=2)

    dat.calculate_coord("0")#nadel links
    plt.scatter(dat.actual_position[xaxis],dat.actual_position[yaxis],s=2,zorder=3,c='C3')
    plt.plot(dat.actual_position[xaxis],dat.actual_position[yaxis], 'C3', lw=1,zorder=4)

    dat.calculate_coord("1")#nadel rechts
    plt.scatter(dat.actual_position[xaxis],dat.actual_position[yaxis],s=2,zorder=5,c='C4')
    plt.plot(dat.actual_position[xaxis],dat.actual_position[yaxis], 'C4', lw=1,zorder=6)

    #plt.plot(dat.gl_position[xaxis],dat.gl_position[yaxis], 'C4', lw=1,zorder=1)
    #plt.scatter(dat.position[xaxis],dat.position[yaxis],s=7,zorder=5,c=dat.position["coordinate_system"])
    
    plt.title(prog+ " Verfahrwege Koordinatensysteme 1, 2 kombiniert")
    plt.grid(b=True, which='major', color='r', linestyle='--')
    plt.grid(b=True, which='minor', color='g', linestyle='--')
    plt.minorticks_on()
    plt.show()

    ###############################
    plt.plot(dat.position[xaxis],dat.position[yaxis], 'C4', lw=1,zorder=1)
    plt.scatter(dat.position[xaxis],dat.position[yaxis],s=7,zorder=5,c=dat.position["coordinate_system"])
    plt.title(prog+ " Verfahrweg aktiver Koordinatensystem")
    plt.grid(b=True, which='major', color='r', linestyle='--')
    plt.grid(b=True, which='minor', color='g', linestyle='--')
    plt.minorticks_on()
    plt.show()

    #################global
    plt.plot(dat.gl_position[xaxis],dat.gl_position[yaxis], 'C4', lw=1,zorder=1)
    plt.scatter(dat.gl_position[xaxis],dat.gl_position[yaxis],s=7,zorder=5,c=dat.position["coordinate_system"])
    plt.title(prog+ " Verfahrweg globaler Koordinatensystem")
    plt.grid(b=True, which='major', color='r', linestyle='--')
    plt.grid(b=True, which='minor', color='g', linestyle='--')
    plt.minorticks_on()
    plt.show()
    
    anim(dat)
    x_0=0
    y_0=0
    length=0
    
    for x,y in zip(dat.position[xaxis],dat.position[yaxis]):
        length+=math.sqrt((x-x_0)*(x-x_0)+(y-y_0)*(y-y_0))
        x_0=x
        y_0=y

    print("länge: "+str(length))
    return(dat)

def plot_path(dat, yaxis="y", xaxis="x"):

    plt.plot(dat.position[xaxis], dat.position[yaxis], "b-")

    k = 0
    for i, ii in enumerate(dat.position["makro"]):
        if dat.position["makro"][i] != "kreis":
            plt.annotate(k, xy=(dat.position[xaxis][i], dat.position[yaxis][i]), fontsize=8)
            k = k + 1

    plt.ylabel(yaxis)
    plt.xlabel(xaxis)
    plt.title(dat.name)
    plt.grid(b=True, which='major', color='r', linestyle='--')
    plt.grid(b=True, which='minor', color='g', linestyle='--')
    plt.minorticks_on()

    plt.show()

    x_0 = 0
    y_0 = 0
    length = 0

    for x, y in zip(dat.position[xaxis], dat.position[yaxis]):
        length += math.sqrt((x - x_0) * (x - x_0) + (y - y_0) * (y - y_0))
        x_0 = x
        y_0 = y

    print("länge: " + str(length))

#a=run_prog("example","y","x","DatronKL3")
#print(len(a.position["x"]))

     
