# coding: utf-8

import os
import math

import FWCore.ParameterSet.Config as cms
from FWCore.ParameterSet.VarParsing import VarParsing
from reco_prodtools.templates.GSD_fragment import process

# option parsing
options = VarParsing('python')
options.setDefault('outputFile', 'file:DUMMYFILENAME')
options.setDefault('maxEvents', DUMMYEVTSPERJOB)
options.register("pileup", DUMMYPU, VarParsing.multiplicity.singleton, VarParsing.varType.int,
    "pileup")
options.register("seed", DUMMYSEED, VarParsing.multiplicity.singleton, VarParsing.varType.int,
    "random seed")
options.parseArguments()

process.maxEvents.input = cms.untracked.int32(options.maxEvents)

# random seeds
process.RandomNumberGeneratorService.generator.initialSeed = cms.untracked.uint32(options.seed)
process.RandomNumberGeneratorService.VtxSmeared.initialSeed = cms.untracked.uint32(options.seed)
process.RandomNumberGeneratorService.mix.initialSeed = cms.untracked.uint32(options.seed)

# Input source
process.source.firstLuminosityBlock = cms.untracked.uint32(options.seed)

# Output definition
process.FEVTDEBUGHLToutput.fileName = cms.untracked.string(
    options.__getattr__("outputFile", noTags=True))

# helper
def calculate_rho(z, eta):
    return z * math.tan(2 * math.atan(math.exp(-eta)))

#DUMMYPUSECTION

gunmode = 'GUNMODE'

if gunmode == 'default':
    process.generator = cms.EDProducer("GUNPRODUCERTYPE",
        AddAntiParticle = cms.bool(True),
        PGunParameters = cms.PSet(
            MaxEta = cms.double(DUMMYETAMAX),
            MaxPhi = cms.double(math.pi),
            MAXTHRESHSTRING = cms.double(DUMMYTHRESHMAX),
            MINTHRESHSTRING = cms.double(DUMMYTHRESHMIN),
            MinEta = cms.double(DUMMYETAMIN),
            MinPhi = cms.double(-math.pi),
            #DUMMYINCONESECTION
            PartID = cms.vint32(DUMMYIDs)
        ),
        Verbosity = cms.untracked.int32(0),
        firstRun = cms.untracked.uint32(1),
        psethack = cms.string('multiple particles predefined pT/E eta 1p479 to 3')
    )
elif gunmode == 'pythia8':
    process.generator = cms.EDFilter("GUNPRODUCERTYPE",
        maxEventsToPrint = cms.untracked.int32(1),
        pythiaPylistVerbosity = cms.untracked.int32(1),
        pythiaHepMCVerbosity = cms.untracked.bool(True),
        PGunParameters = cms.PSet(
          ParticleID = cms.vint32(DUMMYIDs),
          AddAntiParticle = cms.bool(True),
          MinPhi = cms.double(-math.pi),
          MaxPhi = cms.double(math.pi),
          MINTHRESHSTRING = cms.double(DUMMYTHRESHMIN),
          MAXTHRESHSTRING = cms.double(DUMMYTHRESHMAX),
          MinEta = cms.double(1.479),
          MaxEta = cms.double(3.0)
          ),
        PythiaParameters = cms.PSet(parameterSets = cms.vstring())
    )
elif gunmode == 'closeby':
    process.generator = cms.EDProducer("GUNPRODUCERTYPE",
        AddAntiParticle = cms.bool(False),
        PGunParameters = cms.PSet(
            PartID = cms.vint32(DUMMYIDs),
            EnMin = cms.double(DUMMYTHRESHMIN),
            EnMax = cms.double(DUMMYTHRESHMAX),
            RMin = cms.double(DUMMYRMIN),
            RMax = cms.double(DUMMYRMAX),
            ZMin = cms.double(DUMMYZMIN),
            ZMax = cms.double(DUMMYZMAX),
            Delta = cms.double(DUMMYDELTA),
            Pointing = cms.bool(DUMMYPOINTING),
            Overlapping = cms.bool(DUMMYOVERLAPPING),
            RandomShoot = cms.bool(DUMMYRANDOMSHOOT),
            NParticles = cms.int32(DUMMYNRANDOMPARTICLES),
            MaxEta = cms.double(DUMMYETAMAX),
            MinEta = cms.double(DUMMYETAMIN),
            MaxPhi = cms.double(math.pi / 6.),
            MinPhi = cms.double(-math.pi / 6.)
        ),
        Verbosity = cms.untracked.int32(10),
        psethack = cms.string('single or multiple particles predefined E moving vertex'),
        firstRun = cms.untracked.uint32(1)
    )
elif gunmode == 'closebydr':
    process.generator = cms.EDProducer("CloseByFlatDeltaRGunProducer",
        # particle ids
        particleIDs=cms.vint32(DUMMYIDs),
        # max number of particles to shoot at a time
        nParticles=cms.int32(DUMMYNRANDOMPARTICLES),
        # shoot exactly the particles defined in particleIDs in that order
        exactShoot=cms.bool(DUMMYEXACTSHOOT),
        # randomly shoot [1, nParticles] particles, each time randomly drawn from particleIDs
        randomShoot=cms.bool(DUMMYRANDOMSHOOT),
        # energy range
        eMin=cms.double(DUMMYTHRESHMIN),
        eMax=cms.double(DUMMYTHRESHMAX),
        # phi range
        phiMin=cms.double(-math.pi),
        phiMax=cms.double(math.pi),
        # eta range
        etaMin=cms.double(1.52),
        etaMax=cms.double(3.00),
        # longitudinal gun position in cm
        zMin=cms.double(DUMMYZMIN),
        zMax=cms.double(DUMMYZMAX),
        # deltaR settings
        deltaRMin=cms.double(DUMMYRMIN),
        deltaRMax=cms.double(DUMMYRMAX),
        # debug flag
        debug=cms.untracked.bool(True),
    )
elif gunmode == 'physproc':

    # GUNPRODUCERTYPE is a string in the form of proc[:jetColl:threshold:min_jets]
    physicsProcess = 'GUNPRODUCERTYPE'
    proc_cfg = physicsProcess.split(':')
    proc = proc_cfg[0]

    # phase space cuts
    ptMin = DUMMYTHRESHMIN
    ptMax = DUMMYTHRESHMAX

    from reco_prodtools.templates.hgcBiasedGenProcesses_cfi import *

    #define the process
    print 'Setting process to', proc
    defineProcessGenerator(process, proc=proc, ptMin=ptMin, ptMax=ptMax)

    #set a filter path if it's available
    if len(proc_cfg)==4:
        jetColl = proc_cfg[1]
        thr = float(proc_cfg[2])
        minObj = int(proc_cfg[3])
        print 'Adding a filter with the following settings:'
        print '\tgen-jet collection for filtering:', jetColl
        print '\tpT threshold [GeV]:', thr
        print '\tmin. number of jets with the above threshold:', minObj
        filterPath = defineJetBasedBias(process, jetColl=jetColl, thr=thr, minObj=minObj)
        process.schedule.extend([filterPath])
        process.FEVTDEBUGHLToutput.SelectEvents.SelectEvents=cms.vstring(filterPath.label())

# reload and configure the appropriate pileup modules
if options.pileup > 0:
    process.load("SimGeneral.MixingModule.mix_POISSON_average_cfi")
    process.mix.input.nbPileupEvents.averageNumber = cms.double(options.pileup)
    # process.mix.input.fileNames = cms.untracked.vstring(["/store/relval/CMSSW_10_6_0_patch2/RelValMinBias_14TeV/GEN-SIM/106X_upgrade2023_realistic_v3_2023D41noPU-v1/10000/F7FE3FE9-565B-544A-855E-902BA4E3C5FD.root', '/store/relval/CMSSW_10_6_0_patch2/RelValMinBias_14TeV/GEN-SIM/106X_upgrade2023_realistic_v3_2023D41noPU-v1/10000/82584FBA-A1E6-DF48-99BA-B1759C3A190F.root', '/store/relval/CMSSW_10_6_0_patch2/RelValMinBias_14TeV/GEN-SIM/106X_upgrade2023_realistic_v3_2023D41noPU-v1/10000/F806295A-492F-EF4F-9D91-15DA8769DD72.root', '/store/relval/CMSSW_10_6_0_patch2/RelValMinBias_14TeV/GEN-SIM/106X_upgrade2023_realistic_v3_2023D41noPU-v1/10000/6FCA2E1D-D1E2-514B-8ABA-5B71A2C1E1B3.root', '/store/relval/CMSSW_10_6_0_patch2/RelValMinBias_14TeV/GEN-SIM/106X_upgrade2023_realistic_v3_2023D41noPU-v1/10000/287275CC-953A-0C4C-B352-E39EC2D571F0.root', '/store/relval/CMSSW_10_6_0_patch2/RelValMinBias_14TeV/GEN-SIM/106X_upgrade2023_realistic_v3_2023D41noPU-v1/10000/657065A5-F35B-3147-AED9-E4ACA915C982.root', '/store/relval/CMSSW_10_6_0_patch2/RelValMinBias_14TeV/GEN-SIM/106X_upgrade2023_realistic_v3_2023D41noPU-v1/10000/2C56BC73-5687-674C-8684-6C785A88DB78.root', '/store/relval/CMSSW_10_6_0_patch2/RelValMinBias_14TeV/GEN-SIM/106X_upgrade2023_realistic_v3_2023D41noPU-v1/10000/B96F4064-156C-5E47-90A0-07475310157A.root', '/store/relval/CMSSW_10_6_0_patch2/RelValMinBias_14TeV/GEN-SIM/106X_upgrade2023_realistic_v3_2023D41noPU-v1/10000/2564B36D-A0DB-6C42-9105-B1CFF44F311D.root', '/store/relval/CMSSW_10_6_0_patch2/RelValMinBias_14TeV/GEN-SIM/106X_upgrade2023_realistic_v3_2023D41noPU-v1/10000/2CB8C960-47C0-1A40-A9F7-0B62987097E0.root"])  # noqa: E501
    local_pu_dir = "/eos/user/m/mrieger/data/hgc/RelvalMinBias14"
    process.mix.input.fileNames = cms.untracked.vstring([
        "file://" + os.path.abspath(os.path.join(local_pu_dir, elem))
        for elem in os.listdir(local_pu_dir)
        if elem.endswith(".root")
    ])
else:
    process.load("SimGeneral.MixingModule.mixNoPU_cfi")
