# autosmalt
Automatic read mapping of FastQ sequence data against a specified reference - from .gz to .vcf with as little hands on time as possible.

In Progress and not fully debugged.

i.e. it likely doesn't work... yet.

This program assumes your fastq data is still labelled using the Illumina naming scheme - it can take either raw zipped (.gz) or unzipped (.fastq) read files directly from machine output.

For the program to work, your files should contain a unique identifier, followed by an underscore, followed by either 'R1' or 'R2'. The program uses the underscore to seperate the identifier from the rest of the filename.

e.g. sample1_R1.fastq would result in a VCF output 'sample1.vcf - sample_1_R1.fastq would result in a vcf output 'sample.vcf'.
     sample1_l04d5_of_R!nD0M_Chr$_R1.fastq would also be fine, as the initial underscore and R1 identifier are in tact.

Known Issues:
If a sample is vastly different to the reference, you may experience truncated file errors: I validated this using reads against a different species assembly. I have not been able to reproduce the error with very distantly related members of the same species, or  genus.

Dependencies (validated version):
Samtools (1.3), BCFtools (1.3), SMALT (0.7.6), VCFtools (0.1.14)
