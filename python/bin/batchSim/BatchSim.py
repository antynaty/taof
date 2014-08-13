#!/usr/bin/python
'''
\author Thomas Watteyne <watteyne@eecs.berkeley.edu>    
\author Xavier Vilajosana <xvilajosana@eecs.berkeley.edu>
\author Kazushi Muraoka <k-muraoka@eecs.berkeley.edu>
\author Nicola Accettura <nicola.accettura@eecs.berkeley.edu>
'''

#============================ adjust path =====================================

import os
import sys
import time
if __name__=='__main__':
    here = sys.path[0]
    sys.path.insert(0, os.path.join(here, '..', '..'))

#============================ logging =========================================

import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('BatchSim')
log.setLevel(logging.ERROR)
log.addHandler(NullHandler())

#============================ imports =========================================

import logging.config

from argparse      import ArgumentParser
from SimEngine     import SimEngine,   \
                          SimSettings, \
                          Propagation
from SimGui        import SimGui

#============================ defines =========================================

#============================ main ============================================

def parseCliOptions():
    
    parser = ArgumentParser()
    
    parser.add_argument( '--numMotesList',
        dest       = 'numMotesList',
        nargs      = '+',
        type       = int,
        default    = [20, 40],
        help       = 'List of network sizes, in number of simulated motes.',
    )
    
    parser.add_argument( '--pkPeriodList',
        dest       = 'pkPeriodList',
        nargs      = '+',
        type       = float,
        default    = [1.0, 2.0],
        help       = 'List of average periods (is s) between two packets generated by a mote.',
    )
    
    parser.add_argument( '--pkPeriodVarList',
        dest       = 'pkPeriodVarList',
        nargs      = '+',
        type       = float,
        default    = [0.1, 0.2],
        help       = 'List of variability percentages of the traffic, in [0..1[ (use 0 for CBR).',
    )
    
    parser.add_argument( '--otfThresholdList',
        dest       = 'otfThresholdList',
        nargs      = '+',
        type       = int,
        default    = [0, 10],
        help       = 'List of OTF thresholds, in cells.',
    )
    
    parser.add_argument( '--numRuns',
        dest       = 'numRuns',
        type       = int,
        default    = 3, 
        help       = 'Number of simulation runs per each configurations.',
    )
    
    opts           = parser.parse_args()
    numRuns=opts.__dict__.pop('numRuns')
    
    return numRuns, opts

def postprocessing(filename, postprocessingFilename, numRuns, cycles):
    f=open(filename)
    lines=f.readlines()
    f.close()
    while lines[0].startswith('#'):
        lines.pop(0)
    assert len(lines)==numRuns*cycles
    matrix=[]
    for run in xrange(numRuns):
        matrix+=[[[float(l) for l in lines.pop(0).strip().split('\t')[2:]] for i in xrange(cycles)]]
    #To Be Updated
    
def main():
    
    # initialize logging
    logging.config.fileConfig('logging.conf')
    
    # parse CLI options
    numRuns, options   = parseCliOptions()
    print options
    
    for numMotes in options.numMotesList:
        for pkPeriod in options.pkPeriodList:
            for pkPeriodVar in options.pkPeriodVarList:
                for otfThreshold in options.otfThresholdList:
                    directory = os.path.join('results', \
                        'numMotes_{0}_pkPeriod_{1}ms_pkPeriodVar_{2}%_otfThreshold_{3}cells'.format(numMotes,int(pkPeriod*1000),int(pkPeriodVar*100),otfThreshold))
                    if not os.path.exists(directory):
                        os.makedirs(directory)
                    idfilename=int(time.time())
                    filename='//output_{0}.dat'.format(idfilename)
                    settings = SimSettings.SimSettings(\
                                numMotes=numMotes, \
                                pkPeriod=pkPeriod, \
                                pkPeriodVar=pkPeriodVar, \
                                otfThreshold=otfThreshold, \
                                outputFile=directory+filename, \
                                )
                    # run the simulation runs
                    for runNum in xrange(numRuns):
                        
                        # logging
                        print('run {0}, start'.format(runNum))
                        
                        # create singletons
                        propagation     = Propagation.Propagation()
                        simengine       = SimEngine.SimEngine(runNum) # start simulation
                        
                        # wait for simulation to end
                        simengine.join()
                        
                        # destroy singletons
                        simengine.destroy()
                        propagation.destroy()
                        
                        # logging
                        print('run {0}, end'.format(runNum))
                    
                    postprocessingFilename='//postprocessing_{0}_{1}.dat'.format(numRuns,idfilename)
                    postprocessing(directory+filename, directory+postprocessingFilename, numRuns, settings.numCyclesPerRun)
                    settings.destroy()                       # destroy the SimSettings singleton

if __name__=="__main__":
    main()
