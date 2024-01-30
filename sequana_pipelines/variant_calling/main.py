#
#  This file is part of Sequana software
#
#  Copyright (c) 2016-2021 - Sequana Development Team
#
#  Distributed under the terms of the 3-clause BSD license.
#  The full license is in the LICENSE file, distributed with this software.
#
#  website: https://github.com/sequana/sequana
#  documentation: http://sequana.readthedocs.io
#
##############################################################################
import os
import sys

import click_completion
import rich_click as click

click_completion.init()

from sequana_pipetools import SequanaManager
from sequana_pipetools.options import *

NAME = "variant_calling"


help = init_click(
    NAME,
    groups={
        "Pipeline Specific": [
            "--reference-file",
            "--aligner-choice",
            "--annotation-file",
            "--circular",
            "--do-coverage",
            "--do-joint-calling",
            "--freebayes-ploidy",
            "--nanopore",
            "--pacbio",
        ],
    },
)


@click.command(context_settings=help)
@include_options_from(ClickSnakemakeOptions, working_directory=NAME)
@include_options_from(ClickSlurmOptions)
@include_options_from(ClickInputOptions)
@include_options_from(ClickGeneralOptions)
@click.option(
    "--aligner-choice",
    "aligner",
    type=click.Choice(["bwa", "minimap2"]),
    default="bwa",
    show_default=True,
    help="The aligner in bwa / minimap2 .",
)
@click.option(
    "--do-coverage",
    "do_coverage",
    is_flag=True,
    default=False,
    show_default=True,
    help="perform the coverage analysis using sequana_coverage.",
)
@click.option(
    "--annotation-file",
    "annotation",
    default=None,
    help="The annotation for snpeff. This is optional but highly recommended to obtain meaningful HTML report.",
)
@click.option(
    "--do-coverage",
    "do_coverage",
    is_flag=True,
    default=False,
    show_default=True,
    help="perform the coverage analysis using sequana_coverage.",
)
@click.option(
    "--nanopore",
    is_flag=True,
    default=False,
    show_default=True,
    help="if set, fix minimap2 as the aligner, and uses -x map-ont for the minimap2 options",
)
@click.option(
    "--pacbio",
    is_flag=True,
    default=False,
    show_default=True,
    help="if set, fix minimap2 as the aligner, and uses -x map-pb for the minimap2 options",
)
@click.option("--do-joint-calling", "do_joint_calling", is_flag=True, help="do the joint calling analysis")
@click.option(
    "--freebayes-ploidy",
    type=int,
    default=1,
    show_default=True,
    help="""For population, or eukaryotes, change the ploidy to the correct values. For population, you may set it to 10.""",
)
@click.option("-o", "--circular", is_flag=True, help="Recommended for bacteria genomes and circularised genomes")
@click.option("--reference-file", "reference", required=True, help="The input reference to mapped reads onto")
def main(**options):
    # the real stuff is here
    manager = SequanaManager(options, NAME)
    manager.setup()

    # aliases
    options = manager.options
    cfg = manager.config.config

    manager.fill_data_options()

    def fill_annotation_file():
        if options.annotation:
            cfg.snpeff.do = True
            cfg.general.annotation_file = os.path.abspath(options.annotation)
            # manager.exists(cfg.annotation_file)
            # print("." in cfg.annotation_file,  cfg.annotation_file.split(".")[-1])
            if "." not in cfg.general.annotation_file or cfg.general.annotation_file.split(".")[-1] not in [
                "gbk",
                "gff",
                "gff3",
            ]:
                click.echo(
                    "The annotation file must in in .gbk or .gff or .gff3. You provided {cfg.general.annotation_file}"
                )
                sys.exit(1)
        else:
            cfg.snpeff.do = False
            cfg["sequana_coverage"]["genbank_file"] = ""

    def fill_do_coverage():
        cfg["sequana_coverage"]["do"] = options.do_coverage

    def fill_circular_coverage():
        cfg["sequana_coverage"]["circular"] = options.circular

    def fill_do_joint_freebayes():
        cfg["joint_freebayes"]["do"] = options.do_joint_calling

    def fill_ploidy_freebayes():
        cfg["freebayes"]["ploidy"] = options.freebayes_ploidy

    def fill_reference_file():
        # required argument
        cfg.general.reference_file = os.path.abspath(options.reference)

    # first if option --long-read is used (overwritten by other options)
    if options["nanopore"]:
        cfg.general.aligner_choice = "minimap2"
        cfg.minimap2.options = "-x map-ont"
    elif options["pacbio"]:
        cfg.general.aligner_choice = "minimap2"
        cfg.minimap2.options = "-x map-pb"

    if options["from_project"]:
        raise NotImplementedError
    else:
        fill_annotation_file()
        fill_do_coverage()
        fill_circular_coverage()
        fill_do_joint_freebayes()
        fill_ploidy_freebayes()
        fill_reference_file()

    # Given the reference, let us compute its length and the index algorithm
    from sequana import FastA

    f = FastA(cfg.general.reference_file)
    N = f.get_stats()["total_length"]

    # seems to be a hardcoded values in bwa according to the documentation
    if N >= 2000000000:
        cfg["bwa_mem"]["index_algorithm"] = "bwtsw"
    else:
        cfg["bwa_mem"]["index_algorithm"] = "is"

    # finalise the command and save it; copy the snakemake. update the config
    # file and save it.
    manager.teardown()


if __name__ == "__main__":
    main()
