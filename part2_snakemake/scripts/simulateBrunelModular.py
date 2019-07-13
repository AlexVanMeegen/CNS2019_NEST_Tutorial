"""Simulate a Brunel network.

Usage:
    simulateBrunel.py [options] <network_file> <spikefile> <rasterfile>

Simulates a Brunel network with standard parameters using NEST.
Takes all network parameters from the yaml file <network_file>.
Saves the spiking activity of recorded excitatory neurons
to <spikefile> and plots it in <rasterfile>.

Modular code structure to make it a building block for future use.

Simulation options:
    --simtime=<T>           simulation time in ms [default: 500.0]
    --dt=<dt>               simulation timestep in ms [default: 0.1]

Network options:
    --g=<g>                 relative inhibitory to excitatory synaptic weight
                            (w_I = - g * w_E) [default: 5.0]
    --nu_ex=<nu_ex>         external rate relative to threshold rate
                            [default: 2.0]
    --N_scale=<N_scale>     scaling factor for neuron number [default: 0.5]

Plotting options:
    --raster_tmin=<t_min>   minimal x value t_min plotted [default: 400.0]
    --raster_tmax=<t_max>   maximal x value t_max plotted [default: 500.0]
"""

import nest


def buildBrunel(N_rec, NE, NI, CE, CI, w, g, d, neuron_params, nu_ex):
    """Build a Brunel network in NEST with the given configuration.

    Parameters:
        N_rec           record from N_rec excitatory and N_rec
                        inhibitory neurons
        NE              number of excitatory neurons
        NI              number of inhibitory neurons
        CE              indegree from excitatory neurons
        CI              indegree from inhibitory neurons
        w               excitatory synaptic weight in mV
        g               relative inhibitory to excitatory synaptic weight:
                        w_I = - g * w_E
        d               synaptic transmission delay in ms
        neuron_params   parameter dictionary for lif_psc_delta neurons
        nu_ex           external rate relative to threshold rate

    Returns:
        pgen, neurons_e, neurons_i, spikes_e, spikes_i: lists of GIDs
    """
    # set default parameters for neurons and create neurons
    nest.SetDefaults('iaf_psc_delta', neuron_params)
    neurons_e = nest.Create('iaf_psc_delta', NE)
    neurons_i = nest.Create('iaf_psc_delta', NI)

    # create poisson generator
    # external rate needed to evoke activity in spks/ms
    nu_th = neuron_params['V_th'] / (w * neuron_params['tau_m'])
    p_rate = 1e3 * nu_ex * nu_th  # spks/ms -> spks/s
    pgen = nest.Create('poisson_generator', params={'rate': p_rate})

    # create spike detectors
    nest.SetDefaults('spike_detector', {'withtime': True,
                                        'withgid': True,
                                        'to_file': False})
    spikes_e = nest.Create('spike_detector')
    spikes_i = nest.Create('spike_detector')

    # create excitatory connections
    # synapse specification
    syn_exc = {'delay': d, 'weight': w}
    # connection specification
    conn_exc = {'rule': 'fixed_indegree', 'indegree': CE}
    # connect excitatory neurons
    nest.Connect(neurons_e, neurons_e, conn_exc, syn_exc)
    nest.Connect(neurons_e, neurons_i, conn_exc, syn_exc)

    # create inhibitory connections
    # synapse specification
    syn_inh = {'delay': d, 'weight': - g * w}
    # connection specification
    conn_inh = {'rule': 'fixed_indegree', 'indegree': CI}
    # connect inhibitory neurons
    nest.Connect(neurons_i, neurons_e, conn_inh, syn_inh)
    nest.Connect(neurons_i, neurons_i, conn_inh, syn_inh)

    # connect poisson generator using the excitatory connection weight
    nest.Connect(pgen, neurons_i, syn_spec=syn_exc)
    nest.Connect(pgen, neurons_e, syn_spec=syn_exc)

    # connect N_rec excitatory / inhibitory neurons to spike detector
    nest.Connect(neurons_e[:N_rec], spikes_e)
    nest.Connect(neurons_i[:N_rec], spikes_i)

    return pgen, neurons_e, neurons_i, spikes_e, spikes_i


def simulateBrunel(simtime, dt, network_config):
    """Build a Brunel network and simulate it.

    Parameters:
        simtime             simulation time in ms
        dt                  simulation timestep in ms
        network_config      keyword arguments for buildBrunel

    Returns:
        (ids_e, times_e), (ids_i, times_i):     array of spike senders / spike
                                                times of recorded neurons
    """
    # configure kernel
    nest.ResetKernel()
    nest.SetKernelStatus({'resolution': dt, 'print_time': True})

    # build the Brunel network
    _, _, _, spikes_e, spikes_i = buildBrunel(**network_config)

    # simulate
    nest.Simulate(simtime)

    # read out spikes from spikedetector
    data_e = nest.GetStatus(spikes_e, 'events')[0]
    ids_e = data_e['senders']
    times_e = data_e['times']
    data_i = nest.GetStatus(spikes_i, 'events')[0]
    ids_i = data_i['senders']
    times_i = data_i['times']

    return (ids_e, times_e), (ids_i, times_i)


if __name__ == '__main__':
    import yaml
    from docopt import docopt
    import numpy as np
    import matplotlib.pyplot as plt

    # parse command line parameters
    args = docopt(__doc__)

    # load network config from network_file
    with open(args['<network_file>'], 'r') as network_file:
        network_config = yaml.load(network_file, Loader=yaml.FullLoader)
    # override g and nu_ex
    network_config['g'] = float(args['--g'])
    network_config['nu_ex'] = float(args['--nu_ex'])
    # scale neuron number (making sure it is an integer)
    network_config['NE'] *= float(args['--N_scale'])
    network_config['NE'] = int(round(network_config['NE']))
    network_config['NI'] *= float(args['--N_scale'])
    network_config['NI'] = int(round(network_config['NI']))

    # simulate network
    (ids_e, times_e), _ = simulateBrunel(
        simtime=float(args['--simtime']), dt=float(args['--dt']),
        network_config=network_config
    )

    # save spikes
    np.save(args['<spikefile>'], [ids_e, times_e])

    # raster plot of spiking activity using matplotlib
    plt.plot(times_e, ids_e, 'o')
    plt.xlabel('Time (ms)')
    plt.xlim(float(args['--raster_tmin']), float(args['--raster_tmax']))
    plt.savefig(args['<rasterfile>'])
