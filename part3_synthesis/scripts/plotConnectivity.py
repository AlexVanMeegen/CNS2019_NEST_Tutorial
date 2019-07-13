"""Plot network connectivity.

Usage:
    plotConnectivity.py <synapse_file> <plot_file>

"""


if __name__ == '__main__':
    from docopt import docopt
    import numpy as np
    import matplotlib.pyplot as plt

    # parse command line parameters
    args = docopt(__doc__)

    # load synapse number
    synapses = np.load(args['<synapse_file>'])
    recurrent_synapses = synapses[:, :-1]

    # plot connetivity
    plt.imshow(
        np.log10(recurrent_synapses), aspect='equal',
        interpolation='none'
    )
    plt.colorbar(label='log10( number of synapses )')
    plt.title('connectivity matrix')
    plt.xticks([])
    plt.yticks([])
    plt.tight_layout()

    # save plot
    plt.savefig(args['<plot_file>'])
