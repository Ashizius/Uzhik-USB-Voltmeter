
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.transforms import Affine2D
from matplotlib.patches import Circle
from matplotlib.patches import Polygon
from matplotlib.lines import Line2D
from matplotlib.figure import Figure
import tkinter as tk
from time import perf_counter_ns
import matplotlib
matplotlib.use('TkAgg')

LINESTYLES = (
    ('solid',                 (0, ())),
    ('long dash with offset', (5, (10, 3))),
    ('dotted',                (0, (1, 1))),
    ('loosely dashdotdotted', (0, (3, 10, 1, 10, 1, 10))))

COLORS = ('green', 'maroon', 'blue', 'purple', 'black', 'orange')

class Plotter():

    def __init__(self, window: tk.Toplevel):
        self.window = window
        self._lines: list[list[Line2D]] = list()
        self._plots: dict[int, tuple[int, dict[int, int]]] = dict()
        self.isCreated = False
        self._isPlotterInit = False

    def create_plottables(self, subplotIndex: int, *, x: list[int] = None, interval=1, defLabel='y'):
        """
        create the matplotlib artists to be animated
        """
        lsI = 0
        colorI = 0
        lineList = list()
        subplotDict = dict()
        self._plots.update({subplotIndex: (len(self._lines), subplotDict)})
        self._lines.append(lineList)

        # (ln1,) = self.ax.plot(x, y, animated=True) #create the matplotlib artists to be animated
        def addLine(lineIndex, y, lineLabel=defLabel):
            nonlocal x, subplotDict, interval, lsI, colorI, defLabel
            if (x == None):
                x = self._createXArray(y, interval)
            # print(x)

            line = Line2D(
                x, y, linestyle=LINESTYLES[lsI][1], animated=True, color=COLORS[colorI], label=lineLabel)
            if lsI >= len(LINESTYLES)-1:
                lsI = 0
            else:
                lsI += 1
            if colorI >= len(COLORS)-1:
                colorI = 0
            else:
                colorI += 1
            lineList.append(line)
            subplotDict.update({lineIndex: len(lineList)-1})
        return addLine

    def set_plot_area(self, xLim: tuple[float, float], yLim: tuple[float, float]):
        """
        set up plot area and store it in cache
        """
        print('===set_plot_area===')

        self.figure, ax = plt.subplots(
            nrows=len(self._plots.keys()), ncols=1, num=1, clear=True)  # , figsize=(3, 3)
        self.canvas = FigureCanvasTkAgg(self.figure, self.window)
        tkArea = self.canvas.get_tk_widget()
        tkArea.pack(expand=True, fill='both')
        self.tkArea = tkArea
        self.axes = self.figure.axes
        self.isCreated = True

        for ax in self.axes:
            ax.set_xlim(xLim)
            ax.set_ylim(yLim)
            ax.set_xlabel(self.xLabel)
            ax.set_ylabel(self.yLabel)
            ax.grid(ls='--')

        for p in range(0, len(self._lines)):
            self.axes[p].legend(self._lines[p], list(
                map(lambda x: x.get_label(), self._lines[p])))
            for line in self._lines[p]:
                print(line.get_label())

        # draw figure now and cache it so that draw artists works later on
        self.figure.canvas.draw()
        self.bg = self.figure.canvas.copy_from_bbox(self.figure.bbox)

        return self

    def plot_update(self, subplotIndex: int, *, x: list[float] = None, interval=1, defLabel='y'):

        # update the artists
        (p, linesI) = self._plots[subplotIndex]

        def update_line(lineIndex: int, y: list[float], lineLabel=defLabel):
            nonlocal p, linesI, defLabel, x
            if x != None:
                self._lines[p][l].set_xdata(x)
            l = linesI[lineIndex]
            self._lines[p][l].set_ydata(y)
            self._lines[p][l].set_transform(self.axes[p].transData)
            self._lines[p][l].set_label(lineLabel)
        return update_line

    def plots_redraw(self):
        # redraw figure layout
        self.figure.canvas.restore_region(self.bg)

        # redraw the updated artists
        for p in range(0, len(self._lines)):
            for line in self._lines[p]:
                self.axes[p].draw_artist(line)
            self.axes[p].legend()

        # push the update to the gui framework
        self.figure.canvas.blit(self.figure.bbox)

        # flush pending gui events
        self.figure.canvas.flush_events()

    def _createXArray(self, yList, interval):
        if len(yList) == 0:
            return list()
        x = [i*interval for i in range(0, len(yList))]
        return x

    def initPlot(self, xLim: tuple[float, float], yLim: tuple[float, float], xLabel: str = '', yLabel: str = ''):
        if self.isCreated:
            self.destroy()
        self.xLim = xLim
        self.yLim = yLim
        self.xLabel = xLabel
        self.yLabel = yLabel
        self._isPlotterInit = False

    def getUpdater(self):
        if not self.isCreated:
            return self.create_plottables
        return self.plot_update

    def plot(self):
        if not self._isPlotterInit:
            if self.xLim == None:
                return
            self.set_plot_area(self.xLim, self.yLim)
            self._isPlotterInit = True
        else:
            self.plots_redraw()

    def destroy(self):
        self._lines: list[list[Line2D]] = list()
        self._plots: dict[int, tuple[int, dict[int, int]]] = dict()
        self.axes = list()
        self.isCreated = False
        self._isPlotterInit = False
        self.figure.canvas.flush_events()
        self.figure.clf()
        self.tkArea.destroy()
        self.bg = None


# if __name__ == '__main__':
#
#    xlim=(0,500)
#    ylim=(0,500)
#    root=tk.Tk()
#    plotter = Plotter(root)
#    plotter.initPlot(xlim,ylim)
#    addLine=plotter.getUpdater()(0)
#    addLine(0,[i for i in range(0,500)])
#
#
#    plotter.plot()
#    updateLine=plotter.getUpdater()(0)
#    updateLine(0,[i for i in range(0,500)])
#    plotter.plot()
#    updateLine=plotter.getUpdater()(0)
#    updateLine(0,[i/2 for i in range(0,500)])
#    plotter.plot()
#    plotter.destroy()
#    root.mainloop()
#
