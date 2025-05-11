# List of python scripts

1. ***read_h5_files.py*** : Goes through the directories containing the simulation files and reads the *database.h5* files.
It reads the values of *a* and *b* from the database and also records the path of the *h5* file. It saves a *csv* file
containing a table with headers *a,b,path*.

2. ***process_h5_files.py*** : This looks at the *csv* file generated in the previous step and processes each of the *database.h5* 
files. By process, it is meant that it does the following.
It reads a file which contains the steady state tip deflections of the cilia when there is no particle in the flow. However the pressure difference
is maintained the same. This script calls a function *find_extreme_window* from another script ***generate_signatures.py***. This function operates on 
the database file and uses the steady state tip deflections. It outputs two arrays. One is the tip deflection of the cilia and the other is a mask which
corresponds to the values of the tip deflection which are above/below the steady state value. In total we have 4 lists, corresponding to the two components 
of cilia tip deflection. This data is saved as *pkl* file with the name ***simdata_tip.pkl***.

3. ***generate_cilia_features.py*** : This script is used to generate a list of features for each of the particle case. The list of features is still 
under progress. The features are generated taking into account either the *x* or *y* component of the tip deflections in its individual run. The component
can be changed inside the script before running it. The script takes the tip deflection which comprise the *signal* and subtracts the appropriate steady state
deflection value followed by taking absolute value of the result. This ensures that all the valleys are also converted to peaks and eases the process of 
calculating area under the signal. Currently the following features are calculated.
    1. Absolute value of the maximum Deflection of the cilia tip from the steady state value.
    2. Area under the signal 
    3. Width of the signal
    4. Number of peaks in the signal

These data is stored in the following data-structure which a list of lists. And each component of this list of lists is a numpy array.
***ciliafeatures[icilia][ifeature]***


