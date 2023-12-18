
import sys, argparse
import numpy as np
import ROOT as rt

from helpers.larflowreco_ana_funcs import getCosThetaGravVector


parser = argparse.ArgumentParser("Make energy histograms from a bnb nu overlay ntuple file")
parser.add_argument("-i", "--infile", type=str, required=True, help="input ntuple file")
parser.add_argument("-o", "--outfile", type=str, default="example_ntuple_analysis_script_output.root", help="output root file name")
parser.add_argument("-fc", "--fullyContained", action="store_true", help="only consider fully contained events")
parser.add_argument("-ncc", "--noCosmicCuts", action="store_true", help="don't apply cosmic rejection cuts")
args = parser.parse_args()

#needed for proper scaling of error bars:
rt.TH1.SetDefaultSumw2(rt.kTRUE)

#open input file and get event and POT trees
ntuple_file = rt.TFile(args.infile)
eventTree = ntuple_file.Get("EventTree")
potTree = ntuple_file.Get("potTree")

#we will scale histograms to expected event counts from POT in runs 1-3: 6.67e+20
targetPOT = 6.67e+20
targetPOTstring = "6.67e+20" #for plot axis titles

#calculate POT represented by full ntuple file after applying cross section weights
ntuplePOTsum = 0.
for i in range(potTree.GetEntries()):
  potTree.GetEntry(i)
  ntuplePOTsum = ntuplePOTsum + potTree.totGoodPOT

#define histograms to fill
#we will write histograms to output file for:
#true neutrino energy in GeV
h_trueNuE = rt.TH1F("h_trueNuE","True Neutrino Energy",30,0,6)
#reco neutrino energy in GeV
h_recoNuE = rt.TH1F("h_recoNuE","Reconstructed Neutrino Energy",30,0,6)
#true primary muon energy in GeV
h_trueMuE = rt.TH1F("h_trueMuE","True Muon Energy",30,0,5)
#reco energy of reco primary muon (LArPID-identified muon track with highest muon score) in GeV
h_recoMuE = rt.TH1F("h_recoMuE","Reconstructed Muon Energy",30,0,5)

#set histogram axis titles and increase line width
def configureHist(h):
  h.GetYaxis().SetTitle("events per "+targetPOTstring+" POT")
  h.GetXaxis().SetTitle("energy (GeV)")
  h.SetLineWidth(2)
  return h
h_trueNuE = configureHist(h_trueNuE)
h_recoNuE = configureHist(h_recoNuE)
h_trueMuE = configureHist(h_trueMuE)
h_recoMuE = configureHist(h_recoMuE)


#begin loop over events in ntuple file

for i in range(eventTree.GetEntries()):

  eventTree.GetEntry(i)

  #skip events that are not CC numu interactions
  #ntuple only has file with nu interactions inside fiducial volume, so no need to check for that
  if not (abs(eventTree.trueNuPDG) == 14 and eventTree.trueNuCCNC == 0):
    continue

  #skip event with no reco neutrino vertex inside the fiducial volume
  if not (eventTree.foundVertex == 1 and eventTree.vtxIsFiducial == 1):
    continue

  #since we'll be plotting reco muon energy using range, then if requested:
  #skip events where all prongs attached to reco neutrino vertex are not contained inside the fiducial volume
  if args.fullyContained and not (eventTree.vtxContainment == 2):
    continue

  #skip events where no reco muon was identified by LArPID
  #identify the reco muon with the highest muon score if more than one is present
  foundMuon = False
  muon_iT = -1 #we will be able to access track variables for selected reco muon using this index
  max_muonScore = -99.
  for iT in range(eventTree.nTracks):
    #skip if track wasn't classified by LArPID or was attached as secondary
    if eventTree.trackIsSecondary[iT] == 1 or eventTree.trackClassified[iT] != 1:
      continue
    #look at track's that were classified by LArPID as muons
    if eventTree.trackPID[iT] == 13:
      foundMuon = True
      if eventTree.trackMuScore[iT] > max_muonScore:
        max_muonScore = eventTree.trackMuScore[iT]
        muon_iT = iT
  if not foundMuon:
    continue

  #apply cosmic ray rejection cuts unless user requested that we not
  if not args.noCosmicCuts:
    #skip events where all hits overlap with tagged cosmic rays
    if eventTree.vtxFracHitsOnCosmic >= 1.:
      continue
    #skip events for which the reco nuetrino vertex doesn't have a high neutrino keypoint score
    if eventTree.vtxScore < 0.9:
      continue
    #skip events where the reco muon is upwards (against gravity) going
    # neutrino vertices are sometimes reconstructed from cosmic michel decays at the end of the muon track
    # this causes the cosmic muon to be mis-reconstructed as upwards going rather than downwards going
    cosMuonAngleToGrav = getCosThetaGravVector(eventTree.trackStartDirX[muon_iT],
     eventTree.trackStartDirY[muon_iT], eventTree.trackStartDirZ[muon_iT])
    if cosMuonAngleToGrav < -0.9:
      continue
    #skip events where reco muon is not classified as a primary particle
    if eventTree.trackProcess[muon_iT] != 0:
      continue
    #skip events where reco muon has a high "secondary particle with neutral parent" score
    if eventTree.trackFromNeutralScore[muon_iT] > -3.5:
      continue

  #fill histograms, weighting each event by cross-section weight to allow for proper POT scaling

  #fill true neutrino energy histogram
  h_trueNuE.Fill(eventTree.trueNuE, eventTree.xsecWeight)
  #fill reco neutrino energy histogram, convert from MeV to GeV
  h_recoNuE.Fill(eventTree.recoNuE/1000., eventTree.xsecWeight)
  #fill true muon energy histogram
  #since we are looking at true CCnumu events, we can get this from the trueLepE variable
  h_trueMuE.Fill(eventTree.trueLepE, eventTree.xsecWeight)
  #fill reco muon energy histogram, convert from MeV to GeV
  h_recoMuE.Fill(eventTree.trackRecoE[muon_iT]/1000., eventTree.xsecWeight)

#----- end of event loop ---------------------------------------------#


#scale histograms to target POT
h_trueNuE.Scale(targetPOT/ntuplePOTsum)
h_recoNuE.Scale(targetPOT/ntuplePOTsum)
h_trueMuE.Scale(targetPOT/ntuplePOTsum)
h_recoMuE.Scale(targetPOT/ntuplePOTsum)

#create output root file and write histograms to file
outFile = rt.TFile(args.outfile, "RECREATE")
h_trueNuE.Write()
h_recoNuE.Write()
h_trueMuE.Write()
h_recoMuE.Write()



