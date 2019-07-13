"""Plot the phase diagram of the Brunel network.

Usage:
    plotPhaseDiagram.py [options] <plotfile> <spikefile>...

Arguments:
    plotfile    Output file for plot.
    spikefile   Input file(s) with spike data.

Plotting options:
    --g_min=<g_min>             Minimal g value plotted [default: 1]
    --g_max=<g_max>             Maximal g value plotted [default: 8]
    --nu_ex_min=<nu_ex_min>     Minimal nu_ex value plotted [default: 0]
    --nu_ex_max=<nu_ex_max>     Maximal nu_ex value plotted [default: 4]
    --CV_min=<CV_min>           Minimal CV value in colorscale [default: 0]
    --CV_max=<CV_max>           Maximal CV value in colorscale [default: 1]
    --markersize=<markersize>   Markersize [default: 500]
"""

import os
import numpy as np


def _calculateCV(spikefiles):
    """Calculate the CV from standardized input files: spikes_{g}_{nu_ex}.npy

    Parameters:
        spikefiles:     list of spikefiles

    Returns:
        g_list, nu_ex_list, CV_list: list of respective parameters
    """
    g_list = []
    nu_ex_list = []
    CV_list = []
    for sf in spikefiles:
        # extract name of the file
        fn = os.path.splitext(os.path.basename(sf))[0]

        # extract parameters from filename
        g_list.append(float(fn.split('_')[1]))
        nu_ex_list.append(float(fn.split('_')[2]))

        # load the spike file
        ids, times = np.load(sf)
        ids = ids.astype(np.int)

        # calculate CV for current setting
        CV = 0.
        unique_ids = set(ids)
        if len(unique_ids) > 0:
            for id in unique_ids:
                ISIs = np.diff(times[ids == id])
                if len(ISIs) > 1:
                    CV += np.std(ISIs) / np.mean(ISIs)
            CV /= len(unique_ids)
        CV_list.append(CV)

    return g_list, nu_ex_list, CV_list


if __name__ == '__main__':
    from docopt import docopt
    import matplotlib.pyplot as plt

    # parse command line parameters
    args = docopt(__doc__)

    # calculate CV for all simulation
    g_list, nu_ex_list, CV_list = _calculateCV(args['<spikefile>'])

    # make scatter plot, CV indicated by color
    plt.scatter(
        g_list, nu_ex_list, c=CV_list, marker='s',
        s=float(args['--markersize']), vmin=float(args['--CV_min']),
        vmax=float(args['--CV_max'])
    )
    # set axis range and label
    plt.xlim(float(args['--g_min']), float(args['--g_max']))
    plt.xlabel('$g$')
    plt.ylim(float(args['--nu_ex_min']), float(args['--nu_ex_max']))
    plt.ylabel('$\\nu_{ext}/\\nu_{thr}$')
    # add colorbar and title
    plt.colorbar()
    plt.title('Coefficient of Variation')

    plt.savefig(args['<plotfile>'])
