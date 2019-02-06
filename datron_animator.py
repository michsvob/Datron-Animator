import re  # regular expressions
import matplotlib.pyplot as plt
import math
import pandas as pd
import numpy as np


def cart2pol(x, y):
    rho = np.sqrt(x ** 2 + y ** 2)
    phi = np.arctan2(y, x)
    return (rho, phi)


def pol2cart(rho, phi):
    x = rho * np.cos(phi)
    y = rho * np.sin(phi)
    return (x, y)


def heav(number):
    if number >= 0:
        return 1
    else:
        return 0


def zero(number):
    if number == 0:
        return 0
    else:
        return 1


def floor(number):
    return math.floor(number)


def ceil(number):
    return math.ceil(number)


def is_number(s):
    try:
        float(s)
        return (True)
    except ValueError:
        return (False)


class Datprog:
    """ Read the MCR file and compute dispensing path
     fname: full path to the mcr file

    """
    def __init__(self, fname):
        self.name = fname
        self.read_file()
        self.get_markierungen()
        self.get_submakros()
        self.stack = [0]
        self.position = {"x": [0], "y": [0], "z": [0], "makro": ["main"]}
        self.variables = {"Zp": 0, "Xp": 0, "Yp": 0, "Araupe": 0,
                          "Time": 0}  # was ist *p - aktuelle Koordinate (Axyz kann so manche Koordinaten als relativ akzeptieren)
        self.nullpunktnr = 0
        self.nullpunkt = {"x": [0, 0, 0, 0, 0, 0, 0, 0], "y": [0, 0, 0, 0, 0, 0, 0, 0], "z": [0, 0, 0, 0, 0, 0, 0, 0]}
        self.akt_makro = ["main"]
        self.go_through()

    def read_file(self):
        self.prog = []

        with open(self.name, "r",encoding="cp1252") as f:
            for line in f:
                self.prog.append(line)

    def get_markierungen(self):
        markierungen = {}
        for linenum, line in enumerate(self.prog):
            if line.startswith("Markierung"):
                marknr = re.findall(r'\b\d+\b', line)[0]  # Markierung Nr
                markline = linenum  # Markierung Line
                markierungen[marknr] = markline
        self.markierungen = markierungen

    def get_submakros(self):
        # returns dictionary {makroname:[startline,endline]}
        submakros = {}
        for linenum, line in enumerate(self.prog):
            if line.startswith("("):
                # Submakro start
                startline = linenum
                # Markierung Line
            if line.startswith(")"):
                # Matching submakro end
                endline = linenum
                makroname = re.findall(r'\) (.*);', line)[0]  # Submakro name
                submakros[makroname] = [startline, endline]
        self.submakros = submakros

    def step(self, line_number):
        # for line in self.prog:
        nextline = line_number + 1  # default
        # print(self.stack)

        # identifizierung von main procedure - wenn der stack leer ist
        submakro_starts = [val[0] for val in list(self.submakros.values())]
        submakro_ends = [val[1] for val in list(self.submakros.values())]
        if len(self.stack) == 1 and (line_number in submakro_starts):
            nextline = submakro_ends[submakro_starts.index(line_number)] + 1
            return (nextline)

        line = re.findall(r'[^;]*', self.prog[line_number])[0]  # remove comments
        # print(line)

        if not (re.findall(r'=', line)) == []:
            lhs = re.findall(r'[^=]*', line)[0].strip()
            rhs = re.findall(r'=(.*)', line)[0].strip()
            # print(line)

            for key in sorted(self.variables, reverse=True):
                rhs = rhs.replace(key, str(self.variables[key]))

            try:
                rhs = eval(rhs)

            except SyntaxError as e:
                print("Syntax Error: Zeile übersprungen " + str(e))
            except NameError as e:
                print("Name Error: Zeile übersprungen " + str(e))

            self.variables[lhs] = rhs

        elif not (re.findall(r'Axyz', line)) == []:
            elems = line.lstrip().lstrip("Axyz").replace(" ", "").split(",")

            for i, elem in enumerate(elems):
                for key in sorted(self.variables, reverse=True):
                    elem = elem.replace(key, str(self.variables[key]))
                elems[i] = eval(elem)

            self.position["x"].append(elems[1] + self.nullpunkt["x"][self.nullpunktnr])
            self.position["y"].append(elems[2] + self.nullpunkt["y"][self.nullpunktnr])
            self.position["z"].append(elems[3] + self.nullpunkt["z"][self.nullpunktnr])
            self.position["makro"].append(self.akt_makro[-1])

            self.update_XYZp()

        elif not (re.findall(r'Ixyz', line)) == []:
            elems = line.lstrip().lstrip("Ixyz").replace(" ", "").split(",")

            for i, elem in enumerate(elems):
                for key in sorted(self.variables, reverse=True):
                    elem = elem.replace(key, str(self.variables[key]))
                elems[i] = eval(elem)

            self.position["x"].append(self.position["x"][-1] + elems[1])
            self.position["y"].append(self.position["y"][-1] + elems[2])
            self.position["z"].append(self.position["z"][-1] + elems[3])
            self.position["makro"].append(self.akt_makro[-1])

            self.update_XYZp()

        elif not (re.findall(r'Dispon', line)) == []:
            elems = line.lstrip().lstrip("Dispon").lstrip("_links").replace(" ", "").split(",")

            for i, elem in enumerate(elems):
                for key in sorted(self.variables, reverse=True):
                    elem = elem.replace(key, str(self.variables[key]))
                elems[i] = eval(elem)

            self.position["x"].append(self.position["x"][-1])
            self.position["y"].append(self.position["y"][-1])
            self.position["z"].append(elems[10] + self.nullpunkt["z"][self.nullpunktnr])
            self.position["makro"].append(self.akt_makro[-1])

            self.position["x"].append(self.position["x"][-1] + pol2cart(elems[2], math.radians(elems[1] + 180))[0])
            self.position["y"].append(self.position["y"][-1] + pol2cart(elems[2], math.radians(elems[1] + 180))[1])
            self.position["z"].append(self.position["z"][-1] - elems[3])
            self.position["makro"].append(self.akt_makro[-1])

            self.position["x"].append(self.position["x"][-1] - pol2cart(elems[2], math.radians(elems[1] + 180))[0])
            self.position["y"].append(self.position["y"][-1] - pol2cart(elems[2], math.radians(elems[1] + 180))[1])
            self.position["z"].append(self.position["z"][-1] + elems[3])
            self.position["makro"].append(self.akt_makro[-1])

            self.update_XYZp()

        elif not (re.findall(r'Dispoff', line)) == []:
            elems = line.lstrip().lstrip("Dispoff").replace(" ", "").split(",")

            for i, elem in enumerate(elems):
                for key in sorted(self.variables, reverse=True):
                    elem = elem.replace(key, str(self.variables[key]))
                elems[i] = eval(elem)

            self.position["x"].append(self.position["x"][-1] + pol2cart(elems[5], math.radians(elems[1] + 180))[0])
            self.position["y"].append(self.position["y"][-1] + pol2cart(elems[5], math.radians(elems[1] + 180))[1])
            self.position["z"].append(self.position["z"][-1] + elems[6])
            self.position["makro"].append(self.akt_makro[-1])

            self.position["x"].append(self.position["x"][-1])
            self.position["y"].append(self.position["y"][-1])
            self.position["z"].append(elems[8] + self.nullpunkt["z"][self.nullpunktnr])
            self.position["makro"].append(self.akt_makro[-1])
            self.update_XYZp()

        elif not (re.findall(r'Kreis', line)) == []:
            elems = line.lstrip().lstrip("Kreis").replace(" ", "").split(",")

            for i, elem in enumerate(elems):
                for key in sorted(self.variables, reverse=True):
                    elem = elem.replace(key, str(self.variables[key]))
                try:
                    elems[i] = eval(elem)
                except NameError as e:
                    print("Name Error: Zeile übersprungen " + str(e))
                    return (nextline)

            aw = int(elems[4])  # Anfangswinkel
            ew = int(elems[5])  # Endwinkel
            d = float(elems[0])  # Durchmesser
            zb = float(elems[10])  # Steigung pro Umdrehung
            r = d / 2  # Radius
            ws = int(elems[3])  # Richtung: 0: anti-clockwise, -360: clockwise

            posx0 = self.position["x"][-1]
            posy0 = self.position["y"][-1]
            posz0 = self.position["z"][-1]

            anglestep = 5

            if ws == -360:
                if aw < ew:
                    aw = aw + 360

                for angle in range(aw, ew - anglestep, -anglestep):
                    self.position["x"].append(
                        posx0 - r * math.cos(math.radians(aw)) + pol2cart(r, math.radians(angle))[0])
                    self.position["y"].append(
                        posy0 - r * math.sin(math.radians(aw)) + pol2cart(r, math.radians(angle))[1])
                    self.position["z"].append(posz0 + (angle - aw) * zb / 360)
                    self.position["makro"].append("kreis")

            elif ws == 0:
                if ew < aw:
                    ew = ew + 360
                for angle in range(aw, ew + anglestep, anglestep):
                    self.position["x"].append(
                        posx0 - r * math.cos(math.radians(aw)) + pol2cart(r, math.radians(angle))[0])
                    self.position["y"].append(
                        posy0 - r * math.sin(math.radians(aw)) + pol2cart(r, math.radians(angle))[1])
                    self.position["z"].append(posz0 + (angle - aw) * zb / 360)
                    self.position["makro"].append("kreis")
            else:
                print(line)
                raise (ValueError("andere angaben als ws=0/-360 nicht unterstützt"))
            self.update_XYZp()

        elif not (re.findall(r'Setrel', line)) == []:
            elems = line.lstrip().lstrip("Setrel").replace(" ", "").split(",")

            self.nullpunkt["x"][self.nullpunktnr] = self.position["x"][-1] - float(elems[0])
            self.nullpunkt["y"][self.nullpunktnr] = self.position["y"][-1] - float(elems[1])
            self.nullpunkt["z"][self.nullpunktnr] = self.position["z"][-1] - float(elems[2])

        elif not (re.findall(r'Relsp', line)) == []:
            self.nullpunktnr = int(line[-1])

        elif not (re.findall(r'Mal', line)) == []:
            # print(line)
            # print(self.variables)
            times = self.variables[line.lstrip().lstrip("Mal").replace(" ", "")]
            # print(times)
            makroline = self.prog[line_number + 1]
            for i in range(times - 1):
                # print(makroline)
                self.prog.insert(line_number + 1, makroline)

            if times <= 0:
                return (nextline + 1)

        elif not (re.findall(r'^Submakro', line.lstrip())) == []:
            # run submacro

            for key in sorted(self.submakros, reverse=True):
                if key in line:
                    nextline = self.submakros[key][0]
                    self.stack.append(line_number + 1)
                    self.akt_makro.append(key)
                    break

        elif not (re.findall(r'^\)', line)) == []:
            # return control
            nextline = self.stack.pop()
            self.akt_makro.pop()

        return (nextline)

    def update_XYZp(self):
        self.variables["Xp"] = self.position["x"][-1] - self.nullpunkt["x"][self.nullpunktnr]
        self.variables["Yp"] = self.position["y"][-1] - self.nullpunkt["y"][self.nullpunktnr]
        self.variables["Zp"] = self.position["z"][-1] - self.nullpunkt["z"][self.nullpunktnr]

    def go_through(self):
        nextline = self.step(0)

        while len(self.stack) > 0:
            if nextline == len(self.prog) and len(self.stack) == 1:
                break

            nextline = self.step(nextline)

            if len(self.stack) > 20:
                break


def anim(dat,interval=500):
    import numpy as np
    import matplotlib.pyplot as plt
    from matplotlib.animation import FuncAnimation

    fig, ax = plt.subplots()
    xdata, ydata = [], []
    ln, = plt.plot([], [], 'bo', animated=True)  # go

    def init():
        ax.set_xlim(min(dat.position["x"]) - 10, max(dat.position["x"]) + 10)
        ax.set_ylim(min(dat.position["y"]) - 10, max(dat.position["y"]) + 10)
        ln.set_data([], [])
        return ln,

    def update(frame):
        xdata.append(dat.position["x"][frame])
        ydata.append(dat.position["y"][frame])
        ln.set_data(xdata, ydata)
        return ln,

    ani = FuncAnimation(fig, update, frames=np.arange(1, len(dat.position["x"])),
                        init_func=init, blit=True, interval=interval)
    plt.show()


pd.set_option('expand_frame_repr', False)
pd.set_option('display.max_rows', 500)


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


"""Usage: 
a = Datprog("CBU-M_V_neu.mcr") #generate Datron Object
plot_path(a, "y", "x") #plot path
anim(a,100) #animate path
"""
