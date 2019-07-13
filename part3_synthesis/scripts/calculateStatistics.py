"""Calculate average rate and CV per population.

Usage:
    calculateStatistics.py <spikes_file> <simconfig_file> <statistics_file>

"""


if __name__ == '__main__':
    import yaml
    from docopt import docopt
    import numpy as np

    # parse command line parameters
    args = docopt(__doc__)

    # load spikes file
    spikes = np.load(args['<spikes_file>'], allow_pickle=True)

    # load simulation config
    with open(args['<simconfig_file>'], 'r') as simconf_file:
        simulation_config = yaml.load(simconf_file, Loader=yaml.FullLoader)

    # calculate rates and CVs
    stats = []
    simtime = simulation_config['simtime']
    for pop, min_id, max_id, ids, times in spikes:
        neurons_pop = max_id - min_id + 1

        rate_pop = 1e3 * len(times) / simtime / neurons_pop

        CV_pop = 0.
        for id in range(min_id, max_id+1):
            ISIs = np.diff(times[ids == id])
            if len(ISIs) > 1:
                CV_pop += np.std(ISIs) / np.mean(ISIs)
        CV_pop /= neurons_pop

        stats.append([pop, rate_pop, CV_pop])

    # save rates
    np.save(args['<statistics_file>'], stats)
