

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
#rt.TH1.SetDefaultSumw2(rt.kTRUE)

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
onePhotonHist = rt.TH1F("onePhotonHist", "Energy of NC events with one secondary photon",60,0,6)
twoPhotonHist = rt.TH1F("twoPhotonHist", "Energy of NC events with two secondary photons",60,0,6)
threePhotonHist = rt.TH1F("threePhotonHist", "Energy of NC events with three secondary photons",60,0,6)
morePhotonHist = rt.TH1F("morePhotonHist", "Energy of NC events with more than three secondary photons", 60, 0, 6)

#set histogram axis titles and increase line width
def configureHist(h):
  h.GetYaxis().SetTitle("events per "+targetPOTstring+" POT")
  h.GetXaxis().SetTitle("energy (GeV)")
  h.SetLineWidth(2)
  return h

#Scale the histograms
onePhotonHist = configureHist(onePhotonHist)
twoPhotonHist = configureHist(twoPhotonHist)
threePhotonHist = configureHist(threePhotonHist)
morePhotonHist = configureHist(morePhotonHist)

#Set detector volumes
xMin, xMax = 0, 256
yMin, yMax = -116.5, 116.5
zMin, zMax = 0, 1036
fiducialWidth = 10

#h_trueMuE = configureHist(h_trueMuE)
#h_recoMuE = configureHist(h_recoMuE)

#begin loop over events in ntuple file

for i in range(eventTree.GetEntries()):

  eventTree.GetEntry(i)

  #filter for neutral curren
  if eventTree.trueNuCCNC != 1:
    continue

  if eventTree.trueVtxX <= (xMin + fiducialWidth) or eventTree.trueVtxX >= (xMax - fiducialWidth) or \
    eventTree.trueVtxY <= (yMin + fiducialWidth) or eventTree.trueVtxY >= (yMax - fiducialWidth) or \
    eventTree.trueVtxZ <= (zMin + fiducialWidth) or eventTree.trueVtxZ >= (zMax - fiducialWidth):
    continue
        
  #Filter out cosmic cuts, because that seems like the right thing to do
  #skip events where all hits overlap with tagged cosmic rays
  if eventTree.vtxFracHitsOnCosmic >= 1.:
    continue
  
  #Determine whether there are photons as secondary particles
  photonInSecondary = False
  primList = []
  #Check if Neutral Pion and Kaon in primaries - must be a photon if so
  if 111 in eventTree.truePrimPartPDG or 311 in eventTree.truePrimPartPDG:
    photonInSecondary = True
  else:
  #Create a list of prime particle Track IDs
    for x in range(len(eventTree.trueSimPartTID)):
      if eventTree.trueSimPartTID[x] == eventTree.trueSimPartMID[x]:
        primList.append(eventTree.trueSimPartTID[x])
  #Iterate through to find photons
    for x in range(len(eventTree.trueSimPartPDG)):
      if eventTree.trueSimPartPDG[x] == 22:
  #Check for parent particle in the primary list
        if eventTree.trueSimPartMID[x] in primList:
          photonInSecondary = True
  #Check if the photon has coordinates exactly equal to that of the event vertex
        if abs(eventTree.trueSimPartX[x] - eventTree.trueVtxX) <= 0.15 and abs(eventTree.trueSimPartY[x] - eventTree.trueVtxY) <= 0.15 and abs(eventTree.trueSimPartZ[x] -eventTree.trueVtxZ) <= 0.15:
          photonInSecondary = True
  #Discard event unless a secondary photon is found
  if photonInSecondary == False:
    continue


  #Count the photons to determine histogram sorting
  photonCount = 0
  for x in eventTree.trueSimPartPDG:
    if x == 22:
      photonCount += 1
  #fill our histogram using energy based on photon count
  if photonCount == 0:
    continue
  elif photonCount == 1:
    onePhotonHist.Fill(eventTree.trueNuE, eventTree.xsecWeight)
  elif photonCount ==2:
    twoPhotonHist.Fill(eventTree.trueNuE, eventTree.xsecWeight)
  elif photonCount == 3:
    threePhotonHist.Fill(eventTree.trueNuE, eventTree.xsecWeight)
  elif photonCount > 3:
    morePhotonHist.Fill(eventTree.trueNuE, eventTree.xsecWeight)

#----- end of event loop ---------------------------------------------#

#scale histograms to target POT
onePhotonHist.Scale(targetPOT/ntuplePOTsum)
twoPhotonHist.Scale(targetPOT/ntuplePOTsum)
threePhotonHist.Scale(targetPOT/ntuplePOTsum)
morePhotonHist.Scale(targetPOT/ntuplePOTsum)


#Create stack histogram, add others to it
histStack = rt.THStack("histStack", "NC Histograms with Secondary Photons")

onePhotonHist.SetLineColor(rt.kGreen)
#onePhotonHist.SetFillColor(rt.kGreen)
histStack.Add(onePhotonHist)

twoPhotonHist.SetLineColor(rt.kRed)
#twoPhotonHist.SetFillColor(rt.kOrange)
histStack.Add(twoPhotonHist)

threePhotonHist.SetLineColor(rt.kMagenta)
#threePhotonHist.SetFillColor(rt.kMagenta)
histStack.Add(threePhotonHist)

morePhotonHist.SetLineColor(rt.kCyan)
#morePhotonHist.SetFillColor(rt.kCyan)
histStack.Add(morePhotonHist)

legend = rt.TLegend(0.7, 0.7, 0.9, 0.9)  # (x1, y1, x2, y2) in NDC coordinates

legend.AddEntry(onePhotonHist, "Energy of NC events with one secondary photon", "l")
legend.AddEntry(twoPhotonHist, "Energy of NC events with two secondary photons", "l")
legend.AddEntry(threePhotonHist, "Energy of NC events with three secondary photons", "l")
legend.AddEntry(morePhotonHist, "Energy of NC events with four or more secondary photons", "l")

histCanvas = rt.TCanvas()
histStack.Draw("HIST")
legend.Draw()
rt.gPad.Update()

#create output root file and write histograms to file
outFile = rt.TFile(args.outfile, "RECREATE")
histCanvas.Write()
