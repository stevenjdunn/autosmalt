#!/usr/bin/env python
import os
import glob
import subprocess
import time
import shutil

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
print "Are your FastQ reads still zipped? (i.e. *.gz)"
print ''
choice = raw_input("Y/N:").lower()
print ''
print ''
choiceyes = ['y', 'ye', 'yes', '']
directory = raw_input("Complete path to directory containing reads:")
if not os.path.exists(directory):
    print ''
    print ''
    print '##############'
    print '##  ERROR!  ##'
    print '##############'
    print ''
    time.sleep(1)
    print ''
    print "Directory does not exist!"
    print ''
    print "Please ensure you are specifying a complete path, i.e. /home/user/Desktop/folder/"
    print ''
    time.sleep(1)
    print ''
    print '#################'
    print '##   EXITING   ##'
    print '#################'
    exit(1)
print ''
print ''
print 'Directory sucessfully located...'
time.sleep(1)
print ''
print ''
reference = raw_input("Complete path to reference sequence in FASTA format:")
if not os.path.exists(reference):
    print ''
    print ''
    print '##############'
    print '##  ERROR!  ##'
    print '##############'
    print ''
    time.sleep(1)
    print ''
    print "Reference sequence cannot be found at that location."
    print ''
    print "Please ensure you are specifying a complete path, i.e. /home/user/Desktop/folder/"
    print ''
    time.sleep(1)
    print ''
    print '#################'
    print '##   EXITING   ##'
    print '#################'
    exit(1)
print ''
print ''
print 'Reference successfully located...'
time.sleep(1)
print ''
print ''
print 'Mapping produces several intermediate (and often near duplicate) files.'
print ''
print 'Would you like to remove them after use to conserve disk space?'
print ''
choiceremoval = raw_input('Y/N:').lower()
print ''
print ''

# Gzip Extraction (optional)
if choice in choiceyes:
    print '######################'
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
    print '#######################'
    print ''
    time.sleep(1)
    print ''

# Varable generation
print 'Processing'
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
print '.....'
time.sleep(1)
print ''
print ''

# Index generation
print ''
print ''
print '##################################'
print '## Commencing Index Generation  ##'
print '##################################'
print ''
print ''
time.sleep(1)
os.chdir(directory)
shutil.copyfile(reference, directory1)
print ''
print ''
print 'Preparing smalt index...'
time.sleep(1)
print ''
subprocess.call(['smalt', 'index', '-k', '17', '-s', '2', 'ref', str(directory1)])
print ''
print ''
print 'Index prepared!'
print ''
time.sleep(1)
print ''
print 'Preparing samtools index...'
time.sleep(1)
print ''
subprocess.call(['samtools', 'faidx', str(directory1)])
time.sleep(1)
print 'Index prepared!'
time.sleep(1)
print ''
print ''
print '#######################'
print '##       DONE!      ##'
print '#######################'
print ''
print ''
print ''
print ''
time.sleep(1)

# Smalt mapping
print '###############################'
print '##  Commencing Read Mapping  ##'
print '###############################'
print ''
print ''
time.sleep(1)
print '         WARNING!'
print 'This process will take some time.'
print ''
time.sleep(2)
print ''
for r1,r2,sam, in zip(readoneraw, readtworaw, smaltsam):
    subprocess.call(['smalt', 'map', '-n', '12', '-f', 'sam', '-o', sam,'ref', r1, r2])
print ''
print ''
time.sleep(1)

print '#######################'
print '##       DONE!      ##'
print '#######################'
print ''
print ''
print ''
print ''
time.sleep(1)

# Conversion pretext
print '################################'
print '##  Commencing File Curation  ##'
print '################################'
print ''
print ''
time.sleep(1)
print 'Several files will be created during this process.'
print ''
print 'If you opted to remove intermediate files, they will be deleted when redundant.'
print ''
time.sleep(2)

# SAM conversion
print ''
print 'Converting SAM -> BAM...'
print ''
for sam, bam, in zip(smaltsam, samtoolsbam):
    subprocess.call(['samtools', 'view', '-@', '12', '-bS', '-t', 'reference.fasta.fai', '-o', bam, sam])
print ''
print 'DONE!'
print ''
time.sleep(1)


# SAM removal (optional)
if choiceremoval in choiceyes:
    print ''
    print 'Removing temporary files.'
    print ''
    for rmv, in zip(smaltsam):
        subprocess.call(['rm', rmv])
    print ''
    print 'DONE!'
    print ''
    time.sleep(1)
# BAM sort
print ''
print 'Sorting BAM files...'
print ''
for bam, sort, in zip(samtoolsbam, samtoolssort):
    subprocess.call(['samtools', 'sort', '-@', '12', bam, '-o', sort])
print ''
print 'DONE!'
print ''
time.sleep(1)

# BAM removal (optional)
if choiceremoval in choiceyes:
    print ''
    print 'Removing temporary files.'
    print ''
    for rmv, in zip(samtoolsbam):
        subprocess.call(['rm', rmv])
    print ''
    print 'DONE!'
    print ''
    time.sleep(1)

# BAM rmdup
print ''
print 'Removing BAM duplicates...'
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
if choiceremoval in choiceyes:
    print ''
    print 'Removing temporary files.'
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
print ''
print '####################'
print '## Generating VCF ##'
print '####################'
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
print ''
print 'Cleaning up.'
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

if choiceremoval in choiceyes:
    miscremoval = ['ref.smi', 'ref.sma', 'reference.fasta.fai', 'out.log']
    print ''
    print 'Removing temporary files.'
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
print ''
print '#######################'
print '##       DONE!      ##'
print '#######################'
time.sleep(1)




# Finish
print ''
print ''
print 'Pipeline complete!'
print ''
print ''
print 'BCF files located in:',
print outputfolder2
print ''
print ''
print 'VCF files located in:',
print outputfolder1
print ''
print ''
print 'Pipeline author: Steven Dunn'
print ''
print 'www.stevendunn.co.uk'
print ''
print ''
print 'Real programming credit to SAMtools, BCFTools, VCFtools and SMALT.'
print ''
print 'Visit www.github.com/stevenjdunn/autosmalt for more info.'
print ''
print ''
print '################'
print '##  Finished  ##'
print '################'
print ''
exit(1)
