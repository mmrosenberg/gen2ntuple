# gen2ntuple
scripts for making and analyzing ubdl gen2 ntuples

## software setup

### dependencies

* ROOT is needed for all scripts
* The ubdl software environment must be setup to run the ntuple maker (`make_dlgen2_flat_ntuples.py`). See the quick start section fo the readme in the [ubdl repository](https://github.com/LArbys/ubdl) for instructions

### first time setup

Before running the ntuple maker, you need to compile a C++ script in the `helpers` directory (this creates a shared C++ library used for the fiducial volume calculation). To do this, simply run:

```
cd helpers/
source compile_wirecell_fiducial_volume.sh
```

This only needs to be done once after first downloading the repository.

## using ntuple files

See the following section for full documentation of all ntuple variables.

The ntuples are flat ROOT files containing information about reconstructed neutrino interactions and (for Monte Carlo samples) truth information about the simulated neutrino interactions. If you are new to ROOT, this [ROOT Guide For Beginners](https://root.cern.ch/root/htmldoc/guides/primer/ROOTPrimerLetter.pdf) provides a nice, detailed introduction.

For Monte Carlo samples, the ntuples also contain information about the number of protons on target (POT) that would produce the full sample contained in the ntuple.

I have provided an example script, `example_ntuple_analysis_script.py`, that you can take a look at to see how to use the POT data and how to pull some basic information out of the ntuple files using ROOT in python (PyROOT). This script takes as input an ntuple file made from an MC bnb nu overlay sample, makes histograms of true and reconstructed neutrino and primary muon energies, scales the output histograms to the number of events expected for 6.67e+20 POT, and writes these histograms to an output root file.

To run:
```
python example_ntuple_analysis_script.py -i input_ntuple_file.root -o output_histogram_file.root
```

You can then view the histograms in `output_histogram_file.root` in e.g. a ROOT TBrowser:
```
root -l output_histogram_file.root
root [0] new TBrowser
```

## ntuple variable documentation

Please update this readme if you add new variables!

### Acronyms / terms

* __MC__: Monte Carlo simulation
* __CC__: charged current
* __NC__: neutral current
* __POT__: protons on target
* __PDG code__: particle data group code, an integer unique to every type of particle
* __SCE__: space charge effect
* __True__: refers to simulated quantities from MC
* __Reco / reconstructed__: refers to quantities calculated from detector measurements (or simulated detector measurements in the case of MC events)
* __Detsim tracked__: simulated particle tracked by the detector simulation
* __trackID__: a unique integer associated with a simulated particle. Used to identify a particular simulated particle in an event
* __Prong__: a reconstructed track or shower
* __Truth-matched particle__: the simulated particle that deposits the most energy in a reconstructed prong
* __Prong purity__: the fraction of a reco prong produced by it’s truth-matched particle. (Calculated by summing pixel charges for pixels associated with the prong’s reco 3D hits.)
* __Prong completeness__: the fraction of a reco prong’s truth-matched particle that is included in the reco prong. (Calculated by summing pixel charges for pixels associated with the prong’s reco 3D hits.)
* __LArPID__: a convolutional neural network used for particle identification, particle production process classification, and purity and completeness predictions for reconstructed prongs
* __Prong charge__: the sum of all pixel values for pixels associated with prong’s reco 3D hits
* __Hit__: a reconstructed 3D point created from measured/simulated wire plane signals
* __Fiducial Volume__: the region of the detector where we select vertices / events for analyses
* __Wire Cell Fiducial Volume__: the fiducial volume defined in the wire-cell analysis (> 3cm from SCE corrected detector edge)

### Event filters:

* An entry will appear in the flat ntuple files for every input data event
* For MC simulation, events that meet the following criteria are excluded and will not appear in these file:
    * SCE corrected neutrino interaction vertex is outside the wire cell fiducial volume
    * The event’s cross-section weight is unknown or infinite

### potTree variables:

The potTree (present only in ntuples produced from MC samples) provide information about the number of protons on target (POT) that would produce the full sample contained in the ntuple. There is one entry for each merged_dlreco file used to create the ntuple file. To get the full POT count, add up all the entries in the tree.

Variables:

* __totPOT__: total POT for the file represented by this entry
* __totGoodPOT__: total good POT for the file represented by this entry

I am not entirely sure what the distinction is between the "total POT" and "total good POT" reported in merged_dlreco files, but the two are always the same in every sample I've looked at. I would recomment using `totGoodPOT` and ignoring the `totPOT` entries.

### EventTree file/event identification variables:

* __fileid__: File ID number for larflowreco file that this event was from. Can be used to locate the larflowreco and merged_dlreco files for a particular event
* __run__: run number for event
* __subrun__: subrun number for event
* __event__: event number for event

### EventTree simulation variables for MC events:

These variables are not included for data.

* __xsecWeight__: cross section weight for MC events, use to weight events for POT scaling.
* __trueNuE__: true energy in GeV of simulated neutrino.
* __trueNuPDG__: PDG code of simulated neutrino.
* __trueNuCCNC__: integer indicating if simulated neutrino interaction is CC or NC. 0 for CC, 1 for NC.
* __trueVtx{X,Y,Z}__: SCE corrected X,Y,Z coordinates (in cm) of simulated neutrino interaction vertex.
* __trueLepE__: true energy in GeV of primary lepton.
* __trueLepPDG__: PDG code of simulated primary lepton.
* __nTruePrimParts__: number of true primary particles (number of stable final state particles from the neutrino interaction that are passed to the detector simulation)
* __truePrimPartPDG__: PDG code of true primary particle. Array of length nTruePrimParts
* __truePrimPart{X,Y,Z}__: SCE corrected X,Y,Z coordinates (in cm) of true primary particle start position. Array of length nTruePrimParts
* __truePrimPart{Px,Py,Pz,E}__: initial 4-momentum of true primary particle in GeV/c for 3-momentum coordinates and GeV for total energy. Array of length nTruePrimParts
* __truePrimPartContained__: integer indicating if true primary particle was contained inside the detector. 1 if SCE corrected true end position is inside wire cell fiducial volume, 0 otherwise
* __nTrueSimParts__: number of simulated detsim-tracked particles (particles tracked by the detector simulation)
* __trueSimPartPDG__: PDG code of detsim-tracked particle. Array of length nTrueSimParts
* __trueSimPartTID__: trackID of detsim-tracked particle. Array of length nTrueSimParts
* __trueSimPartMID__: trackID of detsim-tracked particle’s “mother” (ancestor particle that e.g. decayed, producing this particle). Array of length nTrueSimParts
* __trueSimPartProcess__: Integer indicating the process by which a detsim-tracked particle was created. 0 for primary particles from neutrino interaction, 1 for particles produced in a decay, 2 for all other processes
* __trueSimPart{X,Y,Z}__: SCE corrected X,Y,Z coordinates (in cm) of true detsim-tracked particle start position. Array of length nTrueSimParts
* __trueSimPartEDep{X,Y,Z}__: SCE corrected X,Y,Z coordinates (in cm) of point at which detsim-tracked particle begins depositing energy. Point of first photo-conversion for photons, identical to trueSimPart{X,Y,Z} for all other particles. Array of length nTrueSimParts
* __trueSimPart{Px,Py,Pz,E}__: initial 4-momentum of true primary particle in MeV/c for 3-momentum coordinates and MeV for total energy. Array of length nTrueSimParts
* __trueSimPartContained__: integer indicating if detsim-tracked particle was contained inside the detector. 1 if SCE corrected true end position is inside wire cell fiducial volume, 0 otherwise

### EventTree reconstruction variables:

#### Vertex/event variables

* __foundVertex__: 1 if a neutrino interaction vertex was reconstructed, 0 otherwise. (Technical details: a neutrino interaction vertex was considered to be reconstructed if there was at least one LArMatch keypoint with a neutrino keypoint type. If there are multiple neutrino keypoints, the one with the highest keypoint score is selected as the reconstructed neutrino vertex.)
* __vtx{X,Y,Z}__: X,Y,Z coordinates (in cm) of reco neutrino vertex. Defaults to -999 if foundVertex = 0
* __vtxIsFiducial__: 1 if the reco neutrino vertex is inside the wire cell fiducial volume, 0 otherwise. Defaults to -1 if foundVertex = 0
* __vtxContainment__: 2 if all hits in all prongs associated with the reco neutrino vertex are inside the wire cell fiducial volume. 1 if at least one hit in a neutrino-vertex-associated prong is outside the wire cell fiducial volume, but the reco neutrino vertex is inside. 0 if the reco neutrino vertex is outside the wire cell fiducial volume. Defaults to -1 if foundVertex = 0
* __vtxScore__: keypoint score of reco neutrino vertex. Defaults to -1 if foundVertex = 0
* __vtxFracHitsOnCosmic__: fraction of all hits associated with the reco neutrino vertex that match cosmic-tagged pixels
* __vtxDistToTrue__: distance (in cm) between reco and SCE-corrected true neutrino interaction vertex. Not present for data
* __recoNuE__: reconstructed neutrino energy in MeV. Calculated by summing the reconstructed energies of all tracks and showers attached to the reco neutrino vertex
* __eventPCAxis{0,1,2}__: 3-vectors indicating the direction of the first, second, and third principal component axes in a PCA analysis using the coordinates of all hits in all prongs associated with the reconstructed neutrino vertex
* __eventPCEigenVals__: array of three numbers: the eigenvalues assocated with the PCA analysis described above (e.g. eventPCEigenVals[1] gives the eigenvalue associated with eventPCAxis1)
* __eventPCAxis0TSlope__: diagnostic variable verifying that the first PCA axis (eventPCAxis0) is pointing in direction of increasing hit times (1 if yes, -1 if not)
* __eventPCProjMaxGap__: array of five numbers indicating the largest gap (in cm) of hit projections onto the first PCA axis (eventPCAxis0). All hits in all prongs associated with the reco nuetrino vertex are used for the 0th element (eventPCProjMaxGap[0]). In the 1st, 2nd, 3rd, and 4th elements, the 10%, 20%, 30%, and 40%, respectively, of hits furthest from the vertex are excluded. All elements default to -9 if foundVertex = 0
* __eventPCProjMaxDist__: array of five numbers indicating the largest distance between hit projections onto the first PCA axis (eventPCAxis0) without a gap of distance greater than X, where X = 2cm, 4cm, 6cm, 8cm, or 10cm for the 0th (eventPCProjMaxDist[0]), 1st, 2nd, 3rd, and 4th elements, respectively. All hits in all prongs associated with the reco neutrino vertex are used. All elements default to -9 if foundVertex = 0
* __nKeypoints__: number of LArMatch keypoint clusters for this event
* __kpClusterType__: keypoint cluster type (0: kNuVertex, 1: kTrackStart, 2: kTrackEnd, 3: kShowerStart, 4: kShowerMichel, 5: kShowerDelta, 6: kVertexActivity, 7: kStopMuVtx, 8: kNumKeyPoints). Array of length nKeypoints
* __kpFilterType__: 0 if neutrino activity keypoint cluster, 1 if cosmic keypoint cluster. Array of length nKeypoints
* __kpMaxScore__: Maximum score of any keypoint in cluster. Array of length nKeypoints
* __kpMaxPos{X,Y,Z}__: X,Y,Z coordinates (in cm) of the keypoint in cluster with the highest score. Array of length nKeypoints

#### Track variables

* __nTracks__: number of reco tracks attached to reco neutrino vertex. Defaults to 0 if foundVertex = 0
* __trackIsSecondary__: 1 if track was attached to reco neutrino vertex as a secondary particle (a particle produced downstream from the interaction vertex as a result of e.g. the decay of a primary particle produced in the neutrino interaction itself). Array of length nTracks
* __trackNHits__: number of reco 3D hits in track. Array of length nTracks
* __trackHitFrac__: trackNHits divided by total number of hits associated with reco neutrino vertex. Array of length nTracks
* __trackCharge__: Sum of pixel values for all above-noise-threshold pixels associated with track hits (noise threshold: 10). Array of length nTracks
* __trackChargeFrac__: trackCharge divided by sum of all above-noise-threshold pixels associated with reco neutrino vertex. Array of length nTracks
* __trackCosTheta__: cosine of angle between track start direction and beam (z-axis). Track start direction calculated as unit vector pointing from track start position to point on track 5cm from start position (or end of track if length < 5cm). Defaults to -9 if track has fewer than two trajectory points or a length of < 1e-6 cm. Array of length nTracks
* __trackCosThetaY__: cosine of angle between track start direction and gravity (y-axis). Track start direction calculated as unit vector pointing from track start position to point on track 5cm from start position (or end of track if length < 5cm). Defaults to -9 if track has fewer than two trajectory points or a length of < 1e-6 cm. Array of length nTracks
* __trackDistToVtx__: distance (in cm) between track start point and reco neutrino vertex. Defaults to -9 if track has fewer than two trajectory points or a length of < 1e-6 cm. Array of length nTracks
* __trackStartPos{X,Y,Z}__: X,Y,Z coordinates (in cm) of track start position. Defaults to -9 if track has fewer than two trajectory points or a length of < 1e-6 cm. Array of length nTracks
* __trackStartDir{X,Y,Z}__: Coordinates of unit vector pointing in initial track direction, calculated as the vector pointing from the beginning of the track to the first trajectory point at least 5cm from track start (or end of track if track length is less than 5cm). Defaults to -9 if track has fewer than two trajectory points or a length of < 1e-6 cm. Array of length nTracks
* __trackEndPos{X,Y,Z}__: X,Y,Z coordinates (in cm) of track end position. Defaults to -9 if track has fewer than two trajectory points or a length of < 1e-6 cm. Array of length nTracks
* __trackClassified__: 1 if track was classified, 0 otherwise. Track is “classified” if it was processed by LArPID, which will happen if the track has at least 2 trajectory points, a length of >1e-6 cm, and at least 10 above-noise-threshold pixels in all three wire planes (noise threshold: 10). Array of length nTracks
* __trackPID__: Predicted PDG code of track, from LArPID. Defaults to 0 if trackClassified = 0. Array of length nTracks
* __trackElScore__: Track’s electron score from LArPID. Defaults to -99 if trackClassified = 0. Array of length nTracks
* __trackPhScore__: Track’s photon score from LArPID. Defaults to -99 if trackClassified = 0. Array of length nTracks
* __trackMuScore__: Track’s muon score from LArPID. Defaults to -99 if trackClassified = 0. Array of length nTracks
* __trackPiScore__: Track’s pion score from LArPID. Defaults to -99 if trackClassified = 0. Array of length nTracks
* __trackPrScore__: Track’s proton score from LArPID. Defaults to -99 if trackClassified = 0. Array of length nTracks
* __trackComp__: Track’s predicted completeness from LArPID. Defaults to -1 if trackClassified = 0. Array of length nTracks
* __trackPurity__: Track’s predicted purity from LArPID. Defaults to -1 if trackClassified = 0. Array of length nTracks
* __trackProcess__: Track's predicted particle production process from LArPID (0: primary particle from neutrino interaction, 1: secondary particle with a neutral parent, 2: secondary particle with a charged parent). Defaults to -1 if trackClassified = 0. Array of length nTracks
* __trackPrimaryScore__: Track's primary particle score from LArPID. Defaults to -99 if trackClassified = 0. Array of length nTracks
* __trackFromNeutralScore__: Track's secondary particle with neutral parent score from LArPID. Defaults to -99 if trackClassified = 0. Array of length nTracks
* __trackFromChargedScore__: Track's secondary particle with charged parent score from LArPID. Defaults to -99 if trackClassified = 0. Array of length nTracks
* __trackRecoE__: reconstructed energy of track in MeV, calculated from range assuming it is a muon, proton, or pion: whichever has the highest LArPID score. Defaults to -1 if trackClassified = 0. Array of length nTracks
* __trackTruePID__: The PDG code of the track’s truth-matched particle. Defaults to 0 if no simulated particle deposited energy in track's pixels. Not filled for data events. Array of length nTracks
* __trackTrueTID__: The trackID of the track’s truth-matched particle. Defaults to -1 if no simulated particle deposited energy in track's pixels. Not filled for data events. Array of length nTracks
* __trackTrueE__: The true energy (in MeV) of the track’s truth-matched particle. Defaults to -1 if no simulated particle deposited energy in track's pixels. Not filled for data events. Array of length nTracks
* __trackTruePurity__: The true purity of the reco track, calculated from its truth-matched particle. Defaults to 0 if no simulated particle deposited energy in track's pixels. Not filled for data events. Array of length nTracks
* __trackTrueComp__: The true completeness of the reco track, calculated from its truth-matched particle. Defaults to 0 if no simulated particle deposited energy in track's pixels. Not filled for data events. Array of length nTracks
* __trackTrueElPurity__: The fraction of the charge in the reco track produced by simulated electrons. Not filled for data events. Array of length nTracks
* __trackTruePhPurity__: The fraction of the charge in the reco track produced by simulated photons. Not filled for data events. Array of length nTracks
* __trackTrueMuPurity__: The fraction of the charge in the reco track produced by simulated muons. Not filled for data events. Array of length nTracks
* __trackTruePiPurity__: The fraction of the charge in the reco track produced by simulated pions. Not filled for data events. Array of length nTracks
* __trackTruePrPurity__: The fraction of the charge in the reco track produced by simulated protons. Not filled for data events. Array of length nTracks

#### Shower variables

* __nShowers__: number of reco showers attached to reco neutrino vertex. Defaults to 0 if foundVertex = 0
* __showerIsSecondary__: 1 if shower was attached to reco neutrino vertex as a secondary particle (a particle produced downstream from the interaction vertex as a result of e.g. the decay of a primary particle produced in the neutrino interaction itself). Array of length nShowers
* __showerNHits__: number of reco 3D hits in shower. Array of length nShowers
* __showerHitFrac__: showerNHits divided by total number of hits associated with reco neutrino vertex. Array of length nShowers
* __showerCharge__: Sum of pixel values for all above-noise-threshold pixels associated with shower hits (noise threshold: 10). Array of length nShowers
* __showerChargeFrac__: showerCharge divided by sum of all above-noise-threshold pixels associated with reco neutrino vertex. Array of length nShowers
* __showerCosTheta__: cosine of angle between shower start direction and beam (z-axis). Shower start direction calculated as unit vector pointing from shower trunk start position to shower trunk end position. Array of length nShowers
* __showerCosThetaY__: cosine of angle between shower start direction and gravity (y-axis). Shower start direction calculated as unit vector pointing from shower trunk start position to shower trunk end position. Array of length nShowers
* __showerDistToVtx__: distance (in cm) between shower start point and reco neutrino vertex. Array of length nShowers
* __showerStartPos{X,Y,Z}__: X,Y,Z coordinates (in cm) of shower start position. Array of length nShowers
* __showerStartDir{X,Y,Z}__: Coordinates of unit vector pointing in initial shower direction, calculated as the vector pointing from the beginning to the end of the shower trunk. Array of length nShowers
* __showerClassified__: 1 if shower was classified, 0 otherwise. Shower is “classified” if it has at least 10 above-noise-threshold pixels in all three wire planes (noise threshold: 10). Array of length nShowers
* __showerPID__: Predicted PDG code of shower, from LArPID. Defaults to 0 if showerClassified = 0. Array of length nShowers
* __showerElScore__: Shower’s electron score from LArPID. Defaults to -99 if showerClassified = 0. Array of length nShowers
* __showerPhScore__: Shower’s photon score from LArPID. Defaults to -99 if showerClassified = 0. Array of length nShowers
* __showerMuScore__: Shower’s muon score from LArPID. Defaults to -99 if showerClassified = 0. Array of length nShowers
* __showerPiScore__: Shower’s pion score from LArPID. Defaults to -99 if showerClassified = 0. Array of length nShowers
* __showerPrScore__: Shower’s proton score from LArPID. Defaults to -99 if showerClassified = 0. Array of length nShowers
* __showerComp__: Shower’s predicted completeness from LArPID. Defaults to -1 if showerClassified = 0. Array of length nShowers 
* __showerPurity__: Shower’s predicted purity from LArPID. Defaults to -1 if showerClassified = 0. Array of length nShowers
* __showerProcess__: Shower's predicted particle production process from LArPID (0: primary particle from neutrino interaction, 1: secondary particle with a neutral parent, 2: secondary particle with a charged parent). Defaults to -1 if showerClassified = 0. Array of length nShowers
* __showerPrimaryScore__: Shower's primary particle score from LArPID. Defaults to -99 if showerClassified = 0. Array of length nShowers
* __showerFromNeutralScore__: Shower's secondary particle with neutral parent score from LArPID. Defaults to -99 if showerClassified = 0. Array of length nShowers
* __showerFromChargedScore__: Shower's secondary particle with charged parent score from LArPID. Defaults to -99 if showerClassified = 0. Array of length nShowers
* __showerRecoE__: reconstructed energy of shower in MeV, calculated from calibrated collection plane charge. Defaults to -1 if showerClassified = 0. Array of length nShowers
* __showerTruePID__: The PDG code of the shower’s truth-matched particle. Defaults to 0 if no simulated particle deposited energy in shower's pixels. Not filled for data events. Array of length nShowers
* __showerTrueTID__: The trackID of the shower’s truth-matched particle. Defaults to -1 if no simulated particle deposited energy in shower's pixels. Not filled for data events. Array of length nShowers
* __showerTrueE__: The true energy (in MeV) of the shower’s truth-matched particle. Defaults to -1 if no simulated particle deposited energy in shower's pixels. Not filled for data events. Array of length nShowers
* __showerTruePurity__: The true purity of the reco shower, calculated from its truth-matched particle. Defaults to 0 if no simulated particle deposited energy in shower's pixels. Not filled for data events. Array of length nShowers
* __showerTrueComp__: The true completeness of the reco shower, calculated from its truth-matched particle. Defaults to 0 if no simulated particle deposited energy in shower's pixels. Not filled for data events. Array of length nShowers
* __showerTrueElPurity__: The fraction of the charge in the reco shower produced by simulated electrons. Not filled for data events. Array of length nShowers
* __showerTruePhPurity__: The fraction of the charge in the reco shower produced by simulated photons. Not filled for data events. Array of length nShowers
* __showerTrueMuPurity__: The fraction of the charge in the reco shower produced by simulated muons. Not filled for data events. Array of length nShowers
* __showerTruePiPurity__: The fraction of the charge in the reco shower produced by simulated pions. Not filled for data events. Array of length nShowers
* __showerTruePrPurity__: The fraction of the charge in the reco shower produced by simulated protons. Not filled for data events. Array of length nShowers


