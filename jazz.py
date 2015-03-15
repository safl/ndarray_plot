from mpl_toolkits.mplot3d import axes3d
import matplotlib.pyplot as plt
from matplotlib import rcParams
import numpy as np
rcParams['axes.labelsize'] = 14
rcParams['axes.titlesize'] = 16
rcParams['xtick.labelsize'] = 14
rcParams['ytick.labelsize'] = 14
rcParams['legend.fontsize'] = 14
rcParams['font.family'] = 'serif'
rcParams['font.serif'] = ['Computer Modern Roman']
rcParams['text.usetex'] = True
rcParams['grid.alpha'] = 0.0

def make_cube():
    """ A Cube consists of a bunch of planes..."""

    planes = {
        "top"    : np.asarray( [[[0,1],[0,1]], [[0,0],[1,1]], [[1,1],[1,1]]] ),
        "bottom" : np.asarray( [[[0,1],[0,1]], [[0,0],[1,1]], [[0,0],[0,0]]] ),
        "left"   : np.asarray( [[[0,0],[0,0]], [[0,1],[0,1]], [[0,0],[1,1]]] ),
        "right"  : np.asarray( [[[1,1],[1,1]], [[0,1],[0,1]], [[0,0],[1,1]]] ),
        "front"  : np.asarray( [[[0,1],[0,1]], [[0,0],[0,0]], [[0,0],[1,1]]] ),
        "back"   : np.asarray( [[[0,1],[0,1]], [[1,1],[1,1]], [[0,0],[1,1]]] )
    }

    """
    planes = {
        "top"    : np.asarray( [[[1,2],[1,2]], [[1,1],[2,2]], [[2,2],[2,2]]] ),
        "bottom" : np.asarray( [[[1,2],[1,2]], [[1,1],[2,2]], [[1,1],[1,1]]] ),
        "left"   : np.asarray( [[[1,1],[1,1]], [[1,2],[1,2]], [[1,1],[2,2]]] ),
        "right"  : np.asarray( [[[2,2],[2,2]], [[1,2],[1,2]], [[1,1],[2,2]]] ),
        "front"  : np.asarray( [[[1,2],[1,2]], [[1,1],[1,1]], [[1,1],[2,2]]] ),
        "back"   : np.asarray( [[[1,2],[1,2]], [[2,2],[2,2]], [[1,1],[2,2]]] )
    }
    """

    return planes

def skew(l, m, n, recipe=None):
    """Position of array elements in relation to each other."""

    if recipe is None:
        return (0,0,0)
    elif recipe == "even":
        return (l*0.1, m*0.1, n*0.1)
    elif recipe == "even_wide":
        return (l*2.0, m*0.1, n*0.1)
    elif recipe == "layered_tight":
        return (l*0.1, -l*0.5, l*0.5)
    elif recipe == "layered_loose":
        return (l*1.0, -l*1.0, l*1.0)
    elif recipe == "layered":
        return (l*0.75, -l*0.75, l*0.75)
    else:
        raise TypeError("Unknown recipe[%s]" % recipe)

class NDArrayPlotter(object):

    def __init__(self, shape, color="blue", alpha="0.6", scale=(1, 1, 1), skewer=None):
        self.defaults = {
            "color": color,
            "alpha": alpha,
            "shape": shape,
            "scale": scale,
            "skewer":  skewer
        }
        self.set_shape(shape)
        self.set_color(color)
        self.set_alpha(alpha)
        self.set_skewer(skewer)
        self.set_scale(scale)

    def set_shape(self, shape):
        self.shape = shape

        return self.shape

    def set_color(self, color):
        self.colors = np.zeros(self.shape, dtype=('a10'))
        self.colors[:] = color

        return self.colors

    def set_alpha(self, alpha):
        self.alphas = np.empty(self.shape, dtype=np.float32)
        self.alphas[:] = alpha

        return self.alphas

    def set_scale(self, scale):
        self.scale = scale

        return self.scale

    def set_skewer(self, skewer):
        self.skewer = skewer

        return self.skewer

    def render(self, ary, text=None, highlight=None, azim=-15, elev=15):
        
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')

        cube = make_cube()

        for l in xrange(0, ary.shape[0]):
            for m in xrange(0, ary.shape[1]):
                for n in xrange(0, ary.shape[2]):

                    # Extract settings that apply to all sides of the cube
                    alpha = self.alphas[l, m, n]
                    color = self.colors[l, m, n]

                    if highlight and highlight[l, m, n] == 1:
                        alpha = 1

                    relative_pos = skew(l, m, n, self.skewer)

                    for side in cube:
                        (Ls, Ms, Ns) = (
                            self.scale[0]*(cube[side][0] + l ) +relative_pos[0],
                            self.scale[1]*(cube[side][1] + m ) +relative_pos[1],
                            self.scale[2]*(cube[side][2] + n ) +relative_pos[2]
                        )
                        ax.plot_surface(
                            Ls, Ns, Ms,
                            rstride=1, cstride=1,
                            alpha=alpha,
                            color=color
                        )
                    
                    if text:

                        if text == 'coords':
                            elmt_label = "[%d,%d,%d]" %(l, m, n)
                        elif text == 'values':
                            elmt_label = str(ary[l,m, n])
                        else:
                            elmt_label = text

                        elmt_center_coord = np.asarray([l,m,n])
                        elmt_center_coord = elmt_center_coord*np.asarray(self.scale) \
                                         + np.asarray(relative_pos)
                        elmt_center_coord = elmt_center_coord + np.asarray(self.scale)/2.0

                        elmt_label_coord = elmt_center_coord

                        ax.text(
                            elmt_label_coord[0], elmt_label_coord[2], elmt_label_coord[1], 
                            elmt_label,
                            horizontalalignment='center', verticalalignment='center',
                            zdir='y'
                        )

        highest = 0                         # Make it look cubic
        for size in ary.shape:
            if size > highest:
                highest = size
        ax.set_xlim((0,highest))
        ax.set_ylim((0,highest))
        ax.set_zlim((0,highest))
        
        ax.set_title("ND array(l, m, n) = %dD %s" % (ary.ndim, str(ary.shape)))

        ax.set_xlabel('l' )   # Meant to visualize ROW-MAJOR ordering 
        ax.set_ylabel('n')
        ax.set_zlabel('m')

        # Get rid of the ticks
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_zticks([])

        # Get rid of the panes
        ax.w_xaxis.set_pane_color((1.0, 1.0, 1.0, 0.0))
        ax.w_yaxis.set_pane_color((1.0, 1.0, 1.0, 0.0))
        ax.w_zaxis.set_pane_color((1.0, 1.0, 1.0, 0.0))

        # Get rid of the spines
        ax.w_xaxis.line.set_color((1.0, 1.0, 1.0, 0.0))
        ax.w_yaxis.line.set_color((1.0, 1.0, 1.0, 0.0))
        ax.w_zaxis.line.set_color((1.0, 1.0, 1.0, 0.0))

        plt.gca().invert_zaxis()

        ax.view_init(azim=azim, elev=elev)

        return (fig, ax)

def main():
    

    """
    colors = plotter.colors
    colors[:] = "#00FF00"
    colors[ 0,  :, :] = "#FF0000"
    colors[-1,  :, :] = "#FF0000"
    colors[ :,  0, :] = "#FF0000"
    colors[ :, -1, :] = "#FF0000"
    colors[ :,  :, 0] = "#FF0000"
    colors[ :,  :,-1] = "#FF0000"

    alphas = plotter.alphas
    alphas[:] = 0.3
    alphas[ 0,  :, :] = 0.05
    alphas[-1,  :, :] = 0.05
    alphas[ :,  0, :] = 0.05
    alphas[ :, -1, :] = 0.05
    alphas[ :,  :, 0] = 0.05
    alphas[ :,  :,-1] = 0.05
    alphas = plotter.alphas
    alphas[:] = 0.05

    colors = plotter.set_color("#0000FF")

    colors[:,1,1] = "#FF0000"
    alphas[:,1,1] = 0.75

    colors[1,:,1] = "#FF0000"
    alphas[1,:,1] = 0.75
    """
    #subject = np.ones((1,3,3))
    subject = np.arange(0,9).reshape((1,3,3))
    plotter = NDArrayPlotter(subject.shape, skewer="even_wide")
    colors = plotter.set_color("#FFFF00")
    alphas = plotter.set_alpha(0.2)

    colors[:,1,:] = "#FF0000"
    colors[:,0,:] = "#00FF00"
    colors[:,2,:] = "#0000FF"
    print subject
    #(fig, ax) = plotter.render(subject, text='coords')
    (fig_coord, ax_coors) = plotter.render(subject, text='coords')
    (fig_values, ax_value) = plotter.render(subject, text='values')
    plt.show()

if __name__ == "__main__":
    main()
