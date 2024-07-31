#!/bin/bash

#SBATCH --job-name=nuNTuple
#SBATCH --time=48:00:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem-per-cpu=4000
#SBATCH --array=0-95
##SBATCH --partition=wongjiradlab
#SBATCH --partition=batch
##SBATCH --exclude=i2cmp006,s1cmp001,s1cmp002,s1cmp003,p1cmp005,p1cmp041,c1cmp003,c1cmp004

NFILES=1

CONTAINER=/cluster/tufts/wongjiradlabnu/larbys/larbys-container/singularity_minkowskiengine_u20.04.cu111.torch1.9.0_comput8.sif

VALSCRIPT=/cluster/tufts/wongjiradlabnu/azhang15/gen2ntuple/tufts_run_ntuple_maker.sh

#RECOFILELIST=/cluster/tufts/wongjiradlabnu/mrosen25/filelists/larflowreco_v2_me_06/mcc9_v28_wctagger_bnboverlay_filelist.txt
#TRUTHFILELIST=/cluster/tufts/wongjiradlabnu/mrosen25/filelists/mcc9_v28_wctagger_bnboverlay_filelist.txt
#WEIGHTFILE=weights_forCV_v48_Sep24_bnb_nu_run1.pkl

RECOFILELIST=/cluster/tufts/wongjiradlabnu/mrosen25/filelists/mcc9_v29e_dl_run3b_bnb_nu_overlay_nocrtremerge_filelist.txt
TRUTHFILELIST=/cluster/tufts/wongjiradlabnu/mrosen25/filelists/mcc9_v29e_dl_run3b_bnb_nu_overlay_nocrtremerge_filelist.txt
WEIGHTFILE=weights_forCV_v48_Sep24_bnb_nu_run3.pkl

OUTTAG=reco_v2me06_gen2ntuple_photon_edep_fix
CNNMODEL=run3bOverlays_quadTask_plAll_2inChan_5ClassHard_minHit10_b64_oneCycleLR_v2me05_noPCTrainOrVal/ResNet34_recoProng_5class_epoch20.pt

module load singularity/3.5.3

singularity exec --bind /cluster/tufts/wongjiradlabnu:/cluster/tufts/wongjiradlabnu,/cluster/tufts/wongjiradlab:/cluster/tufts/wongjiradlab ${CONTAINER} bash -c "source $VALSCRIPT make_dlgen2_flat_ntuples.py $RECOFILELIST $TRUTHFILELIST $WEIGHTFILE $CNNMODEL $OUTTAG $NFILES -mc"
