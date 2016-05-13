# autosmalt
Automatic read mapping of FastQ sequence data against a reference sequence - from .gz to filtered .vcf with as little hands on time as possible.

### Pipeline

smalt index -k 17 -s 2 Refindex ?.fasta
smalt map -f sam -o ?.sam Refindex ?_1.fastq ?_2.fastq 
samtools faidx ref.fasta 
samtools view -@ 16 -bS -t ref.fasta.fai -o ?.bam ?.sam 
samtools sort -@ 16 ?.bam -o ?.sort 
samtools rmdup ?.sort.bam ?.out.bam 
samtools mpileup -uf ref.fasta ?.out.bam -o ?.bcf 
bcftools call --threads 12 --variants-only -vc -O v ?.bcf -o ?.vcf 
vcftools --vcf ?.vcf --remove-indels --minQ 30 --minDP 8 --max-maf 0.1 --recode-INFO-all 

You can tweak the commands at will by editing the called python subprocess function. For example, forcing SMALT to use an exhaustive search would usually require you to specify the flag '-x' - to add that to this program you would edit at line 155:

### Original:
for r1,r2,sam, in zip(readoneraw, readtworaw, smaltsam):
    subprocess.call(['smalt', 'map', '-n', '12', '-f', 'sam', '-o', sam,'ref', r1, r2])
 
With exhaustive flag:
for r1,r2,sam, in zip(readoneraw, readtworaw, smaltsam):
    subprocess.call(['smalt', 'map', '-n', '12', **'-x'**, '-f', 'sam', '-o', sam,'ref', r1, r2)]SMALT
                                                ^^^^^^
The flag would need to be inbetween ' characters, and be separated from other variables by a comma. 


### Files

This program assumes your fastq data is still labelled using the Illumina naming scheme - it can take either raw zipped (.gz) or unzipped (.fastq) read files directly from machine output.

For the program to work, your files should contain a unique identifier, followed by an underscore, followed by either 'R1' or 'R2'. The program uses the underscore to seperate the identifier from the rest of the filename.

e.g. sample1_R1.fastq would result in a VCF output 'sample1.vcf
     sample_1_R1.fastq would result in a vcf output 'sample.vcf' as the sample identifier contains an underscore.
     sample1_l04d5_of_R!nD0M_Ch4r$_R1.fastq would also result in a vcf output 'sample1.vcf', as the initial underscore and R1 identifier are in tact.
     
     

### Disk Space

Mapping will consume large amounts of disk space. The program will if instructed remove intermediate files once they are no longer needed. This howevever will still produce a lot of data and as such sufficient disk space is required on the disk containing your read files. 

Opting to remove intermediate files will get rid of everything except the final filtered VCF output and the initial unadultered BCF.



### Known Issues:

If a sample is vastly different to the reference, you may experience truncated file errors: I validated this using reads against a different species assembly. I have not been able to reproduce the error with very distantly related members of the same species, or  genus.



### Dependencies (validated version):

[Samtools](http://samtools.sourceforge.net/) (1.3) 
[BCFtools](https://samtools.github.io/bcftools/bcftools.html) (1.3) 
[SMALT](http://www.sanger.ac.uk/science/tools/smalt-0) (0.7.6)
[VCFtools](http://vcftools.sourceforge.net/) (0.1.14)

Tested on OSX El Capitan and Ubuntu 14.04 LTS.


www.stevendunn.co.uk
