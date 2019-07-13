"""Simulate a multi-area network.

Usage:
    simulateMultiareaNetwork.py [options] <neuron_parameter_file>
                                          <structure_file> <neuron_file>
                                          <synapse_file> <weight_file>
                                          <spikes_file> <simconfig_file>

Simulation options:
    --simtime=<T>           simulation time in ms [default: 500.0]
    --dt=<dt>               simulation timestep in ms [default: 0.1]
    --master_seed=<seed>    master seed for random numbers [default: 0]
    --num_threads=<t>       number of threads per MPI process [default: 1]
    --V0_mean=<V0_mean>     mean initial membrane potential [default: -58.0]
    --V0_std=<V0_std>       standard deviation of initial membrane potential
                            [default: 10.0]

Network options:
    --nu_ext=<nu_ext>       rate of external (Poissonian) input [default: 5.0]
    --N_scale=<N_scale>     scaling factor for neuron number [default: 0.01]
    --K_scale=<K_scale>     scaling factor for indegree [default: 0.01]
"""

import numpy as np
import nest


def _round_to_int(arr, dtype=np.int):
    """
    Helper function to round float arrays and cast to int.
    """
    return np.round(arr).astype(dtype)


def buildMultiareaNetwork(structure, population_sizes, synapses, weights,
                          neuron_parameters, nu_ext):
    """Build a multi-area network in NEST.

    Parameters:
        structure           names of all populations
        population_sizes    number of neurons
        synapses            number of synapses
        weights             average weights
        neuron_parameters   neuron parameters
        nu_ext              rate of external Poisson input

    Returns:
        poisson_generators, neurons, spike_detectors: dicts of gid lists
    """
    # assert matching number of populations
    assert np.allclose(structure.shape, population_sizes.shape)
    assert np.allclose(structure.shape, synapses.shape[0])
    assert np.allclose(structure.shape, synapses.shape[1] - 1)
    assert np.allclose(structure.shape, weights.shape[0])
    assert np.allclose(structure.shape, weights.shape[1] - 1)

    # separate recurrent from external synapses / weights
    recurrent_synapses = synapses[:, :-1]
    external_indegree = _round_to_int(synapses[:, -1] / population_sizes)
    recurrent_weights = weights[:, :-1]
    external_weights = weights[:, -1]

    # build all neurons, spike_detectors, and Poisson generators
    neurons = {}
    spike_detectors = {}
    poisson_generators = {}
    nest.SetDefaults('spike_detector', {
        'withtime': True, 'withgid': True, 'to_file': False, 'to_memory': True
    })
    # NOTE: In an actual simulation, you probably want to dump the
    #       spiking activity to_file and not to_memory because often
    #       memory is the main constraint. Here we do it for simplicity.
    nest.SetDefaults('iaf_psc_exp', neuron_parameters)
    for ii, pop in enumerate(structure):
        poisson_generators[pop] = nest.Create('poisson_generator', params={
            'rate': external_indegree[ii] * nu_ext
        })
        neurons[pop] = nest.Create('iaf_psc_exp', population_sizes[ii])
        spike_detectors[pop] = nest.Create('spike_detector')

    # create recurrent connections
    for ii, targetPop in enumerate(structure):
        for jj, sourcePop in enumerate(structure):
            conn_spec = {
                'rule': 'fixed_total_number', 'N': recurrent_synapses[ii, jj]
            }
            syn_spec = {
                'model': 'static_synapse', 'weight': recurrent_weights[ii, jj]
            }
            nest.Connect(
                neurons[sourcePop], neurons[targetPop], conn_spec, syn_spec
            )

    # connect devices
    for ii, pop in enumerate(structure):
        nest.Connect(poisson_generators[pop], neurons[pop], syn_spec={
            'weight': external_weights[ii]
        })
        nest.Connect(neurons[pop], spike_detectors[pop])

    return poisson_generators, neurons, spike_detectors


def simulateMultiareaNetwork(simtime, dt, master_seed, num_threads,
                             V0_mean, V0_std, network_config):
    """Build a multi-area network and simulate it.

    Parameters:
        simtime             simulation time in ms
        dt                  simulation timestep in ms
        master_seed         master seed for random numbers
        num_threads         number of threads per MPI process
        V0_mean             mean initial membrane potential
        V0_std              standard deviation of initial membrane potential
        network_config      keyword arguments for buildBrunel

    Returns:
        spikes:             dict of spike senders / spike times of all
                            neurons in all populations
    """
    # configure kernel
    nest.ResetKernel()
    nest.SetKernelStatus({
        'local_num_threads': num_threads, 'resolution': dt, 'print_time': False
    })

    # seed all random number generators
    if nest.Rank() == 0:
        print('Master seed: %i ' % master_seed)
    N_tp = nest.GetKernelStatus(['total_num_virtual_procs'])[0]
    if nest.Rank() == 0:
        print('Total number of processes: %i' % N_tp)
    pyrng_seeds = list(range(master_seed, master_seed+N_tp))
    grng_seed = master_seed + N_tp
    rng_seeds = list(range(master_seed+1+N_tp, master_seed+1+2*N_tp))
    pyrngs = [np.random.RandomState(s) for s in pyrng_seeds]
    nest.SetKernelStatus({'grng_seed': grng_seed, 'rng_seeds': rng_seeds})

    # build the Brunel network
    _, neurons, spike_detectors = buildMultiareaNetwork(**network_config)

    # distribute initial voltages
    for thread in np.arange(nest.GetKernelStatus('local_num_threads')):
        # Using GetNodes is a work-around until NEST 3.0 is released. It
        # will issue a deprecation warning.
        local_nodes = nest.GetNodes([0], {'model': 'iaf_psc_exp',
                                          'thread': thread},
                                    local_only=True)[0]
        vp = nest.GetStatus(local_nodes)[0]['vp']
        # vp is the same for all local nodes on the same thread
        nest.SetStatus(
            local_nodes, 'V_m', pyrngs[vp].normal(
                V0_mean, V0_std, len(local_nodes)
            )
        )
        if nest.Rank() == 0:
            print('Number of local nodes: %i' % len(local_nodes))

    # simulate
    nest.Simulate(simtime)

    # read out spikes from spikedetectors
    spikes = {}
    for pop in spike_detectors:
        data = nest.GetStatus(spike_detectors[pop], 'events')[0]
        spikes[pop] = {
            'ids': data['senders'], 'times': data['times'],
            'min_id': neurons[pop][0], 'max_id': neurons[pop][-1]
        }

    return spikes


if __name__ == '__main__':
    import yaml
    from docopt import docopt

    # parse command line parameters
    args = docopt(__doc__)

    # load neuron parameters
    with open(args['<neuron_parameter_file>'], 'r') as network_file:
        neuron_yaml = yaml.load(network_file, Loader=yaml.FullLoader)

    # scale number of neurons & connections
    # NOTE: very naive implementation. How to do better:
    #       van Albada, Helias, Diesmann (2015) PLoS CB
    N_scale = float(args['--N_scale'])
    K_scale = float(args['--K_scale'])
    neurons_scaled = _round_to_int(N_scale*np.load(args['<neuron_file>']))
    synapses_scaled = _round_to_int(
        K_scale*N_scale*np.load(args['<synapse_file>'])
    )
    weights_scaled = np.load(args['<weight_file>']) / K_scale

    # parse simulation config
    simulation_config = {
        'simtime': float(args['--simtime']), 'dt': float(args['--dt']),
        'V0_mean': float(args['--V0_mean']), 'V0_std': float(args['--V0_std']),
        'master_seed': int(args['--master_seed']),
        'num_threads': int(args['--num_threads'])
    }

    # simulate network
    spikes = simulateMultiareaNetwork(
        network_config={
            'neuron_parameters': neuron_yaml,
            'structure': np.load(args['<structure_file>']),
            'population_sizes': neurons_scaled, 'synapses': synapses_scaled,
            'weights': weights_scaled, 'nu_ext': float(args['--nu_ext'])
        },
        **simulation_config
    )

    # save spikes
    np.save(args['<spikes_file>'], [[
        pop, spikes[pop]['min_id'], spikes[pop]['max_id'],
        spikes[pop]['ids'], spikes[pop]['times']] for pop in spikes
    ])

    # save simulation config
    with open(args['<simconfig_file>'], 'w') as simconf_file:
        yaml.dump(simulation_config, simconf_file)
