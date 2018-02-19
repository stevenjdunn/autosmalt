#!/usr/bin/env python
import os
import glob
import subprocess
import time
import shutil
import argparse
import re

# Argparse argument setup
parser = argparse.ArgumentParser(description="Automatic read mapping of FastQ sequence data against a specified reference - from .gz to .vcf with as little hands on time as possible.")
requiredargs = parser.add_argument_group('required arguments')
requiredargs.add_argument("-i", "--input", required=True, help="Path directory containing raw Illumina reads.")
requiredargs.add_argument("-r", "--reference", required=True, help="Path to reference FASTA file.")
requiredargs.add_argument("-o", "--output", required=True, help="Path to output destination")
parser.add_argument("-g", "--gzipped", action='store_true', help="Specifies that reads are gzipped (i.e. *.gz)")
parser.add_argument("-d", "--delete", action='store_true', help="Deletes intermediate files.")
args = parser.parse_args()

# Colour set up
class colours:
    warning = '\033[91m'
    blue = '\033[94m'
    invoking = '\033[93m'
    bold = '\033[1m'
    term = '\033[0m'

# Logger set up
ansi_rm = re.compile(r'\x1b\[[0-9;]*m')
class Logger(object):
    def __init__(self):
        self.terminal = sys.stdout
        self.log = open("autosmalt.log", "w")

    def write(self, message):
        self.terminal.write(message)
        self.log.write(re.sub(ansi_rm, '', message))

sys.stdout = Logger()

# User input
print '##############################'
print '##   Welcome to AutoSmalt   ##'
print '##############################'
print ''
print ''
print 'This program will take some time to run, depending on how many input reads are being processed.'
print ''
print 'It will also consume a large amount of disk space on the drive containing your FastQ files.'
print ''
print ''
time.sleep(1)
print ''
# Directory orientation
invoked_from = os.getcwd()
os.chdir(args.output)
directory = os.getcwd()
os.chdir(invoked_from)
if not os.path.exists(args.input):
    print colours.warning + ''
    print ''
    print '##############'
    print '##  ERROR!  ##'
    print '##############'
    print ''
    print ''
    print "Directory does not exist!"
    print ''
    print "Please ensure you are specifying a complete path, i.e. /home/user/Desktop/folder/"
    print ''
    print ''
    print '#################'
    print '##   EXITING   ##'
    print '#################' + colours.term
    exit(1)
print ''
print ''
print 'Directory sucessfully located...'
print ''
print ''
reference = raw_input("Complete path to reference sequence in FASTA format:")
if not os.path.exists(args.reference):
    print colours.warning + ''
    print ''
    print '##############'
    print '##  ERROR!  ##'
    print '##############'
    print ''
    print ''
    print "Reference sequence cannot be found at that location."
    print ''
    print "Please ensure you are specifying a complete path, i.e. /home/user/Desktop/folder/"
    print ''
    print ''
    print '#################'
    print '##   EXITING   ##'
    print '#################' + colours.term
    exit(1)
print ''

# Gzip Extraction (optional)
if args.gzipped:
    print colours.bold + '######################'
    print '## Extracting reads ##'
    print '######################'
    print ''
    time.sleep(1)
    print ''
    gzip = list(glob.glob(os.path.join(directory, '*.gz')))
    for gz, in zip(gzip):
        subprocess.check_call(['gunzip', gz])
    print ''
    print ''
    print '#######################'
    print '##       DONE!      ##'
    print '#######################' + colours.term
    print ''
    time.sleep(1)
    print ''

# Varable generation
print colours.invoking + 'Processing...'
time.sleep(1)
print '.'
readoneraw = list(glob.glob(os.path.join(directory, '*R1*')))
readoneraw.sort()
readtworaw = list(glob.glob(os.path.join(directory, '*R2*')))
readtworaw.sort()
print '..'
time.sleep(1)
rawnameraw = [x.split(directory)[1].split('_')[0] for x in readoneraw]
rawnameraw.sort()
rawname = [s.strip('/') for s in rawnameraw]
directory1 = str(directory)
directory1 += 'reference.fasta'
print '...'
time.sleep(1)

# List comprehension
smaltsam = [x + '.sam' for x in rawname]
samtoolsbam = [x + '_temp.bam' for x in rawname]
samtoolssort = [x + '_sort_temp.bam' for x in rawname]
print '....'
time.sleep(1)
samtoolsfinal = [x + '.bam' for x in rawname]
pileupbcf = [x + '.bcf' for x in rawname]
rawvcf = [x + '.vcf' for x in rawname]
print '.....' + colours.term
time.sleep(1)
print ''
print ''

# Index generation
print ''
print '' + colours.bold
print '##################################'
print '## Commencing Index Generation  ##'
print '##################################' + colours.term
print ''
print ''
time.sleep(1)
os.chdir(directory)
shutil.copyfile(reference, directory1)
print ''
print '' + colours.invoking
print 'Preparing smalt index...' + colours.term
time.sleep(1)
print ''
subprocess.call(['smalt', 'index', '-k', '17', '-s', '2', 'ref', str(directory1)])
print ''
print '' + colours.bold
print 'Index prepared!' + colours.term
print ''
time.sleep(1)
print '' + colours.invoking
print 'Preparing samtools index...' + colours.term
time.sleep(1)
print ''
subprocess.call(['samtools', 'faidx', str(directory1)])
time.sleep(1)
print colours.bold + 'Index prepared!'
time.sleep(1)
print ''
print ''
print '#######################'
print '##       DONE!      ##'
print '#######################' + colours.term
print ''
print ''
print ''
print ''
time.sleep(1)

# Smalt mapping
print colours.bold + '###############################'
print '##  Commencing Read Mapping  ##'
print '###############################' + colurs.term
print ''
print ''
time.sleep(1)
print colours.blue + '         WARNING!'
print 'This process will take some time.' + colours.term
print ''
time.sleep(2)
print ''
for r1,r2,sam, in zip(readoneraw, readtworaw, smaltsam):
    subprocess.call(['smalt', 'map', '-n', '12', '-f', 'sam', '-o', sam,'ref', r1, r2])
print ''
print ''
time.sleep(1)
print colours.bold + '#######################'
print '##       DONE!      ##'
print '#######################' + colours.term
print ''
print ''
print ''
print ''
time.sleep(1)

# Conversion pretext
print colours.bold + '################################'
print '##  Commencing File Curation  ##'
print '################################' + colours.term
print ''
print ''
time.sleep(1)
print 'Several files will be created during this process.'
print ''
print 'If you opted to remove intermediate files, they will be deleted when redundant.'
print ''
time.sleep(2)

# SAM conversion
print '' + colours.invoking
print 'Converting SAM -> BAM...' + colours.term
print ''
for sam, bam, in zip(smaltsam, samtoolsbam):
    subprocess.call(['samtools', 'view', '-@', '12', '-bS', '-t', 'reference.fasta.fai', '-o', bam, sam])
print ''
print 'DONE!'
print ''
time.sleep(1)

# SAM removal (optional)
if args.delete:
    print '' + colours.invoking
    print 'Removing temporary files.'
    print '' + colours.term
    for rmv, in zip(smaltsam):
        subprocess.call(['rm', rmv])
    print ''
    print 'DONE!'
    print ''
    time.sleep(1)

# BAM sort
print '' + colours.invoking
print 'Sorting BAM files...' + colours.term
print ''
for bam, sort, in zip(samtoolsbam, samtoolssort):
    subprocess.call(['samtools', 'sort', '-@', '12', bam, '-o', sort])
print ''
print 'DONE!'
print ''
time.sleep(1)

# BAM removal (optional)
if args.delete:
    print '' + colours.invoking
    print 'Removing temporary files.' + colours.term
    print ''
    for rmv, in zip(samtoolsbam):
        subprocess.call(['rm', rmv])
    print ''
    print 'DONE!'
    print ''
    time.sleep(1)

# BAM rmdup
print '' + colours.invoking
print 'Removing BAM duplicates...' + colours.term
print ''
for sort, final, in zip(samtoolssort, samtoolsfinal):
    subprocess.call(['samtools', 'rmdup', sort, final])
print ''
print 'DONE!'
print ''
print '.'
time.sleep(1)
print '..'
time.sleep(1)
print '...'
time.sleep(1)

# BAM sort removal (optional)
if args.delete:
    print '' + colours.invoking
    print 'Removing temporary files.' + colours.term
    print '.'
    print '..'
    print '...'
    for rmv, in zip(samtoolssort):
        subprocess.call(['rm', rmv])
    print ''
    print 'DONE!'
    print ''
    time.sleep(1)

# BCF/VCF generation
print ''
print '' + colours.bold
print '####################'
print '## Generating VCF ##'
print '####################' + colours.term
print ''
print ''
time.sleep(1)
print '.'
for final, pileup, in zip(samtoolsfinal, pileupbcf):
    subprocess.call(['samtools', 'mpileup', '-uf', str(directory1), final, '-o', pileup])
print '..'
# VCF output
for pileup, vcfraw, in zip(pileupbcf, rawvcf):
    subprocess.call(['bcftools', 'call', '--threads', '12', '--variants-only', '-vc', '-O', 'v', pileup, '-o', vcfraw])
print '...'
# Final VCF (overwrites intermediate)
for vcf, in zip(rawvcf):
    subprocess.call(['vcftools', '--vcf', vcf, '--remove-indels', '--minQ', '30', '--minDP', '8', '--max-maf', '0.1', '--recode-INFO-all'])
print '...'
print '' + colours.invoking
print 'Cleaning up.' + colours.term
print ''
print '.'
print '..'
print '...'
print ''
# VCF Move
outputfolder1 = directory
outputfolder1 += 'vcf/'
if not os.path.exists(outputfolder1):
    os.mkdir(outputfolder1)
vcfs = os.listdir(directory)
for v in vcfs:
    if (v.endswith(".vcf")):
        shutil.move(v, outputfolder1)
# BCF Move
outputfolder2 = directory
outputfolder2 += 'bcf/'
if not os.path.exists(outputfolder2):
    os.mkdir(outputfolder2)
bcfs = os.listdir(directory)
for b in bcfs:
    if (b.endswith(".bcf")):
        shutil.move(b, outputfolder2)
print ''
print 'DONE!'
print ''
time.sleep(1)

# Final removal (optional)

if args.delete:
    miscremoval = ['ref.smi', 'ref.sma', 'reference.fasta.fai', 'out.log']
    print '' + colours.invoking
    print 'Removing temporary files.' + colours.term
    print '.'
    print '..'
    print '...'
    for rmv, in zip(samtoolsfinal):
        subprocess.call(['rm', rmv])
    for rmv, in zip(miscremoval):
        subprocess.call(['rm', rmv])
    print ''
    print 'DONE!'
    print ''

print ''
time.sleep(2)
print '' + colours.bold
print '#######################'
print '##       DONE!      ##'
print '#######################' + colours.term
time.sleep(1)

# Finish
print ''
print '' + colours.bold
print 'Pipeline complete!' + colours.term
print ''
print '' + colours.blue
print 'BCF files located in:' + colours.term,
print outputfolder2
print ''
print '' + colours.blue
print 'VCF files located in:' + colours.term,
print outputfolder1
print ''
print ''
print 'Author: www.github.com/stevenjdunn/'
print '' + colours.bold
print '################'
print '##  Finished  ##'
print '################' + colours.term
print ''
exit(1)
