import numpy as np
import matplotlib.pyplot as plt

def plot_pool_n(basis, n_point, pool_n, bal_ratio_func):
    ''' Plots a legend for the colour scheme
    given by abc_to_rgb. Includes some code adapted
    from http://stackoverflow.com/a/6076050/637562'''

    fig, ax = plt.subplots(1, 1)
    # ax = fig.add_subplot(111,aspect='equal')

    # Plot points
    if pool_n == 3:
        grids = np.mgrid[0.0:1.0:n_point, 0.0:1.0:n_point, 0.0:1.0:n_point]
    elif pool_n == 4:
        grids = np.mgrid[0.0:1.0:n_point, 0.0:1.0:n_point, 0.0:1.0:n_point, 0.0:1.0:n_point]
    else:
        raise ValueError(f'Unsupported pool size {pool_n}')

    abc = np.dstack(tuple(g.flatten() for g in grids))[0][1:]
    abc = abc / abc.sum(axis=1)[:, np.newaxis]

    data = np.dot(abc, basis)
    # colours = [abc_to_rgb(A=point[0],B=point[1],C=point[2]) for point in abc]
    # ax.scatter(data[:,0], data[:,1],marker=',',edgecolors='none',facecolors=colours)
    bal_ratio = bal_ratio_func(abc)
    ax.scatter(data[:,0], data[:,1],
                marker=',',
                edgecolors='none',
                c=bal_ratio, # np.ones(data[:,0].shape) * 256
                cmap=plt.get_cmap('Greens'))

    # Plot triangle
    ax.plot([[basis[_,0] for _ in range(pool_n)] + [0,]],
            [[basis[_,1] for _ in range(pool_n)] + [0,]],
            **{'color':'black','linewidth':3})

    # Plot labels at vertices
    offset = 0.25
    fontsize = 12
    for nn in range(pool_n):
        ax.text(basis[nn,0]*(1+offset),
                basis[nn,1]*(1+offset),
                f'Token {nn+1}',
                horizontalalignment='center',
                verticalalignment='center',
                fontsize=fontsize)

    ax.set_frame_on(False)
    ax.set_xticks(())
    ax.set_yticks(())

    return fig, ax

def plot_pool_n_data(basis, n_point, pool_n, bal_ratio_func):
    ''' Plots a legend for the colour scheme
    given by abc_to_rgb. Includes some code adapted
    from http://stackoverflow.com/a/6076050/637562'''

    # Plot points
    if pool_n == 3:
        grids = np.mgrid[0.0:1.0:n_point, 0.0:1.0:n_point, 0.0:1.0:n_point]
    elif pool_n == 4:
        grids = np.mgrid[0.0:1.0:n_point, 0.0:1.0:n_point, 0.0:1.0:n_point, 0.0:1.0:n_point]
    else:
        raise ValueError(f'Unsupported pool size {pool_n}')

    abc = np.dstack(tuple(g.flatten() for g in grids))[0][1:]
    abc = abc / abc.sum(axis=1)[:, np.newaxis]

    data = np.dot(abc, basis)
    # colours = [abc_to_rgb(A=point[0],B=point[1],C=point[2]) for point in abc]
    # ax.scatter(data[:,0], data[:,1],marker=',',edgecolors='none',facecolors=colours)
    bal_ratio = bal_ratio_func(abc)

    return data, bal_ratio