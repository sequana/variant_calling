
.. image:: https://badge.fury.io/py/sequana-variant-calling.svg
     :target: https://pypi.python.org/pypi/sequana_variant_calling

.. image:: http://joss.theoj.org/papers/10.21105/joss.00352/status.svg
    :target: http://joss.theoj.org/papers/10.21105/joss.00352
    :alt: JOSS (journal of open source software) DOI

.. image:: https://github.com/sequana/variant_calling/actions/workflows/main.yml/badge.svg
   :target: https://github.com/sequana/variant_calling/actions

.. image:: https://img.shields.io/badge/python-3.8%20%7C%203.9%20%7C3.10-blue.svg
    :target: https://pypi.python.org/pypi/sequana
    :alt: Python 3.8 | 3.9 | 3.10

This is the **variant_calling** pipeline from the `Sequana <https://sequana.readthedocs.org>`_ projet

:Overview: Variant calling from FASTQ files
:Input: FASTQ files from Illumina Sequencing instrument
:Output: VCF and HTML files
:Status: production
:Citation: Cokelaer et al, (2017), 'Sequana': a Set of Snakemake NGS pipelines, Journal of Open Source Software, 2(16), 352, JOSS DOI https://doi:10.21105/joss.00352


Installation
~~~~~~~~~~~~

You can install sequana_variant_calling pipeline using::

    pip install sequana_variant_calling --upgrade

I would recommend to setup a *sequana_variant_calling* conda environment executing::

    conda env create -f environment.yml

where the environment.yml can be found in the https://github.com/sequana/variant_calling repository.

Later, you can activate the environment as follows::

  conda activate sequana_variant_calling

Note, however, that the recommended method is to use singularity/apptainer as explained here below.


Usage
~~~~~

::

    sequana_variant_calling --input-directory DATAPATH --reference-file measles.fa 

This creates a directory **variant_calling**. You just need to move into the directory and execute the script::

    cd variant_calling
    sh variant_calling.sh

This launch a snakemake pipeline. If you are familiar with snakemake, you can
retrieve the pipeline itself and its configuration files and then execute the pipeline yourself with specific parameters::

    snakemake -s variant_calling.rules -c config.yaml --cores 4 --stats stats.txt

you can also edit the profile file in .sequana/profile/config.ya,l

Or use `sequanix <https://sequana.readthedocs.io/en/main/sequanix.html>`_ interface.

Usage with singularity::
~~~~~~~~~~~~~~~~~~~~~~~~~

With singularity, initiate the working directory as follows::

    sequana_variant_calling --use-singularity --singularity-prefix ~/.sequana/apptainers

Images are downloaded in a global direcory (here .sequana/apptainers) so that you can reuse them later.

and then as before::

    cd variant_calling
    sh variant_calling.sh

if you decide to use snakemake manually, do not forget to add singularity options::

    snakemake -s variant_calling.rules -c config.yaml --cores 4 --stats stats.txt --use-singularity --singularity-prefix ~/.sequana/apptainers --singularity-args "-B /home:/home"

Requirements
~~~~~~~~~~~~

If you rely on singularity/apptainer, no extra dependencies are required (expect python and
https://damona.readthedocs.io). If you cannot use apptainer, you will need to install some software: 

- bwa
- freebayes
- picard (picard-tools)
- sambamba
- minimap2
- samtools
- snpEff you will need 5.0 or 5.1d (note the d); 5.1 does not work.


.. image:: https://raw.githubusercontent.com/sequana/sequana_variant_calling/main/sequana_pipelines/variant_calling/dag.png

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

Tutorial
~~~~~~~~

Let us download an ecoli reference genome and the data set used to create the assembly. All tools used here below can be
installed with damona (or your favorite environment manager)::

    pip install damona
    damona create TEST
    damona activate TEST
    damona install pigz
    damona install sratoolkit # for fasterq-dump
    damona install datasets

Then, download the data::

    fasterq-dump SRR13921546
    pigz SRR*fastq

and the reference genome with its annnotation::

    datasets download genome accession GCF_000005845.2 --include gff3,rna,cds,protein,genome,seq-report,gbff
    unzip ncbi_dataset.zip
    ln -s ncbi_dataset/data/GCF_000005845.2/GCF_000005845.2_ASM584v2_genomic.fna ecoli.fa
    ln -s ncbi_dataset/data/GCF_000005845.2/genomic.gff ecoli.gff


Initiate the pipeline::

    sequana_variant_calling --input-directory . --reference-file ecoli.fa --aligner-choice bwa_split \
        --do-coverage --annotation-file ecoli.gff  \
        --use-apptainer --apptainer-prefix ~/.sequana/apptainers \ 
        --input-readtag "_[12]." 

Explication:

- we use apptainer/singularity
- we use the reference genome ecoli.fa (--reference-file) and its annotation for SNPeff (--annotation-file)
- we use the sequana_coverage tool (True by default) to get coverage plots.
- we use --input-directory to indicatre where to find the input files
- This data set is paired. In NGS, it is common to have _R1_ and _R2_ tags to differentiate the 2 files. Here the tag are `_1` and `_2`. In sequana we define the a wildcard for the read tag. So here we tell the software that thex ecpted tag follow this pattern: "_[12]." and everything is then automatic.

Then follow the instructions (prepare and execute the pipeline).

You should end up with a summary.hml report.


You can browse the different samples (only one in this example) and get a table with variant calls:

.. image:: https://raw.githubusercontent.com/sequana/variant_calling/refs/heads/main/doc/table.png

If you set the coverage one, (not recommended for eukaryotes), you should see this kind of plots:

.. image:: https://raw.githubusercontent.com/sequana/variant_calling/refs/heads/main/doc/coverage.png





Changelog
~~~~~~~~~

========= ======================================================================
Version   Description
========= ======================================================================
1.4.0     * handles long reads data. Use sequana html_report to create the VCF
            html reports instead of wrapper. More dynamic. Updated some 
            containers, in particular for sequana_coverage.
          * Fixed regression in bwa mapping
          * Fixed ordered of contigs on genomecov that was not sorted in the 
            same way as samtools in some cases. 
1.3.0     * Updated version to use latest damona containers and latest 
            sequana version 0.19.1. added plot in HTML report with distribution
            of variants. added tutorial. added bwa_split and freebaye split to 
            process ultra deep sequencing.
1.2.0     * -Xmx8g option previously added is not robust. Does not work with
            snpEff 5.1 for instance.
          * add minimap aligner
          * add --nanopore and --pacbio to automatically set minimap2 as the
            aligner and the minimap options (map-pb or map-ont)
          * add minimap2 container.
          * add missing resources in snpeff section
1.1.2     * add -Xmx8g option in snpeff rule at the build stage.
          * add resources (8G) in the snpeff rule at run stage
          * fix missing output_directory in sequana_coverage rule
          * fix joint calling (regression) input function and inputs
1.1.1     * Fix regression in coverage rule
1.1.0     * add specific apptainer for freebayes (v1.2.0)
          * Update API to use click
1.0.2     * Fixed failure in multiqc if coverage and snpeff are off
1.0.1     * automatically fill the bwa index algorithm and fix bwa_index rule to
            use the options in the config file (not the harcoded one)
1.0.0     * use last warppers and graphviz apptainer
0.12.0    * set all apptainers containers and add vcf to bcf conversions
          * Update rule sambamba to use latest wrappers
0.11.0    * Add singularity containers
0.10.0    * fully integrated sequana wrappers and simplification of HTML reports
0.9.10    * Uses new sequana_pipetools and wrappers
0.9.5     * fix typo in the onsuccess and update sequana requirements to use
            most up-to-date snakemake rules
0.9.4     * fix typo related to the reference-file option new name not changed
            everyhere in the pipeline.
0.9.3     * use new framework (faster --help, --from-project option)
          * rename --reference into --reference-file and --annotation to
            --annotation-file
          * add custom summary page
          * add multiqc config file
0.9.2     * snpeff output files are renamed sample.snpeff (instead of
            samplesnpeff)
          * add multiqc to show sequana_coverage and snpeff summary sections
          * cleanup onsuccess section
          * more options sanity checks and options (e.g.,
          * genbank_file renamed into annotation_file in the config
          * use --legacy in freebayes options
          * fix coverage section to use new sequana api
          * add the -do-coverage, --do-joint-calling options as well as
            --circular and --frebayes--ploidy
0.9.1     * Fix input-readtag, which was not populated
0.9.0     First release
========= ======================================================================

Contribute & Code of Conduct
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To contribute to this project, please take a look at the
`Contributing Guidelines <https://github.com/sequana/sequana/blob/maib/CONTRIBUTING.rst>`_ first. Please note that this project is released with a
`Code of Conduct <https://github.com/sequana/sequana/blob/main/CONDUCT.md>`_. By contributing to this project, you agree to abide by its terms.
