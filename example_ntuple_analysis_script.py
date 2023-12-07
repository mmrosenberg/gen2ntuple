
import sys, argparse
import numpy as np
import ROOT as rt


parser = argparse.ArgumentParser("Make energy histograms from a bnb nu overlay ntuple file")
parser.add_argument("-i", "--infile", type=str, required=True, help="input ntuple file")
parser.add_argument("-o", "--outfile", type=str, default="example_ntuple_analysis_script_output.root", help="output root file name")
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

  #since we'll be plotting reco muon energy using range,
  #skip events where all prongs attached to reco neutrino vertex are not contained inside the fiducial volume
  if not (eventTree.vtxContainment == 2):
    continue

  #skip events where no reco muon was identified by LArPID
  foundMuon = False
  for iT in range(eventTree.nTracks):
    #skip if track wasn't classified by LArPID or was attached as secondary
    if eventTree.trackIsSecondary[iT] == 1 or eventTree.trackClassified[iT] != 1:
      continue
    if eventTree.trackPID[iT] == 13:
      foundMuon = True
      break
  if not foundMuon:
    continue

  #get true muon energy by looping over primary particles
  trueMuE = -1.
  for iP in range(eventTree.nTruePrimParts):
    if abs(eventTree.truePrimPartPDG[iP]) == 13:
      #we found the true primary muon
      trueMuE = eventTree.truePrimPartE[iP]
      break

  #this should never happen as we skipped non CCnumu events, but it's good to do sanity checks:
  if trueMuE < 0.:
    print("ERROR: true primary muon not found in true CCnumu interaction")
    continue

  #get reco muon energy by finding track with largest LArPID muon score
  #this very likely isn't sufficient for a good reco muon selection, this is just to provide an example
  recoMuE = -1.
  bestMuScore = -999.
  for iT in range(eventTree.nTracks):
    #skip if track wasn't classified by LArPID or was attached as secondary
    if eventTree.trackIsSecondary[iT] == 1 or eventTree.trackClassified[iT] != 1:
      continue
    #skip if track wasn't identified as a muon
    if eventTree.trackPID[iT] != 13:
      continue
    if eventTree.trackMuScore[iT] > bestMuScore:
      bestMuScore = eventTree.trackMuScore[iT]
      recoMuE = eventTree.trackRecoE[iT]/1000. #convert from MeV to GeV

  #this should never happen as we skipped events without an identified muon track, but it's good to do sanity checks:
  if recoMuE < 0.:
    print("ERROR: reco muon not found after attempting to skip events with no reco muon tracks")
    continue

  #fill histograms, weighting each event by cross-section weight to allow for proper POT scaling

  #fill true neutrino energy histogram
  h_trueNuE.Fill(eventTree.trueNuE, eventTree.xsecWeight)
  #fill reco neutrino energy histogram, convert from MeV to GeV
  h_recoNuE.Fill(eventTree.recoNuE/1000., eventTree.xsecWeight)
  #fill true muon energy histogram
  h_trueMuE.Fill(trueMuE, eventTree.xsecWeight)
  #fill reco muon energy histogram
  h_recoMuE.Fill(recoMuE, eventTree.xsecWeight)

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



