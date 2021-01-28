#!/usr/bin/env python3

import sys, os, subprocess

# samples of use:
#  ./bench.py
#  ./bench.py insert_random_full insert_random_full_reserve
#  ./bench.py small_string string

######################################################################
### Fill free to change the following defaults
programs = [
    'std_unordered_map',
    'boost_unordered_map',
    'google_sparse_hash_map',
    'google_dense_hash_map',
    'google_dense_hash_map_mlf_0_9',
    'qt_qhash',
    'spp_sparse_hash_map',
    'emilib_hash_map',
    'ska_flat_hash_map',
    'ska_flat_hash_map_power_of_two',
    'ska_bytell_hash_map',
    'tsl_sparse_map',
    'tsl_hopscotch_map',
    'tsl_hopscotch_map_mlf_0_5',
    'tsl_hopscotch_map_store_hash',
    'tsl_robin_map',
    'tsl_robin_map_mlf_0_9',
    'tsl_robin_map_store_hash',
    'tsl_robin_pg_map',
    'tsl_ordered_map',
    'tsl_array_map',
    'tsl_array_map_mlf_1_0',
    'judyL',
    'judyHS',
    #'nata88',
    #'nataF8'
]

minkeys  =  2*100*1000
maxkeys  = 30*100*1000
#interval =  2*100*1000
step_percent =  30 # you may use this variable instead of "interval" for exponetial step
best_out_of = 5

######################################################################
outfile = open('output', 'w')

short_names = {
    'random_shuffle_range': [
        'insert_random_shuffle_range', 'read_random_shuffle_range'
    ],
    'random_full': [
        'insert_random_full', 'insert_random_full_reserve',
        'read_random_full', 'read_miss_random_full',
        'delete_random_full', 'read_random_full_after_delete',
        'iteration_random_full'
    ],
    'small_string': [
        'insert_small_string', 'insert_small_string_reserve',
        'read_small_string', 'read_miss_small_string',
        'delete_small_string',
        'read_small_string_after_delete'
    ],
    'string': [
        'insert_string', 'insert_string_reserve',
        'read_string', 'read_miss_string',
        'delete_string',
        'read_string_after_delete'
    ]
}

if ("interval" in dir() and "step_percent" in dir()) or \
   ("interval" not in dir() and "step_percent" not in dir()):
    print("Either (exclusively) 'interval' or 'step_percent' variable should be set")
    sys.exit(1)

if len(sys.argv) > 1:
    benchtypes = []
    for x in sys.argv[1:]:
        benchtypes.extend(short_names.get(x, [x]))
else:
    benchtypes = short_names['random_shuffle_range'] + short_names['random_full'] \
        + short_names['small_string'] + short_names['string']

if "interval" in dir():
    points = range(minkeys, maxkeys + 1, interval)
else:
    points = []
    keys = minkeys
    while keys <= maxkeys:
        points.append(keys)
        keys = int(max(keys + 1, keys * (100 + step_percent) / 100))

for nkeys in points:
    for benchtype in benchtypes:
        for program in programs:
            fastest_attempt = 1000000
            fastest_attempt_data = ''

            for attempt in range(best_out_of):
                try:
                    output = subprocess.check_output(['./build/' + program, str(nkeys), benchtype],
                                                     stderr=subprocess.STDOUT)
                    words = output.strip().split()
                    
                    runtime_seconds = float(words[0])
                    memory_usage_bytes = int(words[1])
                    load_factor = float(words[2])
                except subprocess.CalledProcessError as e:
                    if e.returncode == 71: # unknown test type for program?
                        continue # silently ignore this case

                    if e.returncode == -2 or e.returncode == -3: # SIGINT or SIGQUIT?
                        #os.exit(128 - e.returncode) # exit with error
                        sys.exit(76)

                    print("Error with %s" % str(['./build/' + program, str(nkeys), benchtype]), file=sys.stderr)
                    print("Exit status is %d" % e.returncode, file=sys.stderr)
                    print(e.stdout.decode("utf-8"), file=sys.stderr)
                    break

                line = ','.join(map(str, [benchtype, nkeys, program, "%0.2f" % load_factor, 
                                          memory_usage_bytes, "%0.6f" % runtime_seconds]))

                if runtime_seconds < fastest_attempt:
                    fastest_attempt = runtime_seconds
                    fastest_attempt_data = line

            if fastest_attempt != 1000000:
                print(fastest_attempt_data, file=outfile)
                print(fastest_attempt_data)

        # Print blank line
        print(file=outfile)
        print()
