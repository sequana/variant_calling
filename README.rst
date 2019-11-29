This is is the **variant_calling** pipeline from the `Sequana <https://sequana.readthedocs.org>`_ projet

:Overview: Variant calling from FASTQ files
:Input: FASTQ files from Illumina Sequencing instrument
:Output: VCF and HTML files
:Status: production
:Citation: Cokelaer et al, (2017), 'Sequana': a Set of Snakemake NGS pipelines, Journal of Open Source Software, 2(16), 352, JOSS DOI https://doi:10.21105/joss.00352


Installation
~~~~~~~~~~~~

You must install Sequana first::

    pip install sequana

Then, just install this package::

    pip install sequana_variant_calling

Usage
~~~~~

::

    sequana_pipelines_variant_calling --help
    sequana_pipelines_variant_calling --input-directory DATAPATH --run-mode local --reference measles.fa
    sequana_pipelines_variant_calling --input-directory DATAPATH --run-mode slurm --reference measles.fa

This creates a directory **variant_calling**. You just need to execute the pipeline::

    cd variant_calling
    snakemake -s variant_calling.rules --stats stats.txt


This launch a snakemake pipeline. If you are familiar with snakemake, you can retrieve the fastqc.rules and config.yaml files and then execute the pipeline yourself with specific parameters::

    snakemake -s variant_calling.rules --cores 4 --stats stats.txt

Or use `sequanix <https://sequana.readthedocs.io/en/master/sequanix.html>`_ interface.

Requirements
~~~~~~~~~~~~

This pipelines requires the following executable(s):

- bwa
- freebayes
- picard (picard-tools)
- sambamba
- samtools
- snpEff

.. image:: https://raw.githubusercontent.com/sequana/sequana_variant_calling/master/sequana_pipelines/variant_calling/dag.png

Details
~~~~~~~~

Snakemake variant calling pipeline is based on
`tutorial <https://github.com/ekg/alignment-and-variant-calling-tutorial>`_
written by Erik Garrison. Input reads (paired or single) are mapped using
`bwa <http://bio-bwa.sourceforge.net/>`_ and sorted with
`sambamba-sort <http://lomereiter.github.io/sambamba/docs/sambamba-sort.html>`_.
PCR duplicates are marked with
`sambamba-markdup <http://lomereiter.github.io/sambamba/docs/sambamba-sort.html>`_. 
`Freebayes <https://github.com/ekg/freebayes>`_ is used to detect SNPs and short
INDELs. The INDEL realignment and base quality recalibration are not necessary
with Freebayes. For more information, please refer to a post by Brad Chapman on
`minimal BAM preprocessing methods
<https://bcbio.wordpress.com/2013/10/21/updated-comparison-of-variant-detection-methods-ensemble-freebayes-and-minimal-bam-preparation-pipelines/>`_.

The pipeline provides an analysis of the mapping coverage using
`sequana coverage <http://www.biorxiv.org/content/early/2016/12/08/092478>`_.
It detects and characterises automatically low and high genome coverage regions.

Detected variants are annotated with `SnpEff <http://snpeff.sourceforge.net/>`_ if a
GenBank file is provided. The pipeline does the database building automatically.
Although most of the species should be handled automatically, some special cases
such as particular codon table will required edition of the snpeff configuration file.

Finally, joint calling is also available and can be switch on if desired.


Rules and configuration details
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


Mapping
#########

This pipeline uses the following rule from Sequana to perform the mapping and
marking duplicates.

- snpeff_add_locus_in_fasta
- bwa_mem_dynamic
- sambamba_markdup
- sambamba_filter

Variant Calling
###################

The variant calling itself depends on those rules:

- freebayes
- freebayes_vcf_filter

Joint variants calling
#########################

- joint_freebayes
- joint_freebayes_vcf_filter

Annotation
####################
- snpeff

Coverage analysis
###################
- samtools_depth
- sequana_coverage
