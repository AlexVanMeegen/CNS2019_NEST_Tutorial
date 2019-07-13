"""Plot distribution of rates and CVs.

Usage:
    plotStatistics.py <statistics_file> <plot_file>

"""


if __name__ == '__main__':
    from docopt import docopt
    import numpy as np
    import matplotlib.pyplot as plt

    # parse command line parameters
    args = docopt(__doc__)

    # load rates and CVs
    populations, rates, CVs = np.load(args['<statistics_file>']).T
    rates = rates.astype(np.float)
    CVs = CVs.astype(np.float)

    # plot rate and CV distribution
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(6, 4))
    ax1.hist(rates, bins='auto', rwidth=0.9)
    ax2.hist(CVs, bins='auto', rwidth=0.9)
    ax1.spines["top"].set_visible(False)
    ax2.spines["top"].set_visible(False)
    ax1.spines["right"].set_visible(False)
    ax2.spines["right"].set_visible(False)
    ax1.spines["left"].set_visible(False)
    ax2.spines["left"].set_visible(False)
    ax1.set_title('rate histogram')
    ax2.set_title('CV histogram')
    ax1.set_xlabel('$\\nu$ [spks/s]')
    ax2.set_xlabel('$CV$')
    plt.tight_layout()

    # save plot
    plt.savefig(args['<plot_file>'])
