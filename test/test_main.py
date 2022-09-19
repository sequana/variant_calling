import os
import tempfile
import subprocess

import pytest

from . import test_dir

sharedir = f"{test_dir}/data"
reference = sharedir+ os.sep + "JB409847.fasta"
annotation = sharedir + os.sep + "JB409847.gbk"


def test_standalone_subprocess():
    directory = tempfile.TemporaryDirectory()
    cmd = "sequana_variant_calling --input-directory {} "
    cmd += "--working-directory {} --run-mode local --force --annotation-file {} "
    cmd += " --reference-file {}"
    cmd = cmd.format(sharedir, directory.name, annotation, reference)
    subprocess.call(cmd.split())


def test_check_output_ref_annot():

    with tempfile.TemporaryDirectory() as wk:

        cmd = "sequana_variant_calling --input-directory {} "
        cmd += "--working-directory {} --run-mode local --force --annotation-file {} "
        cmd += " --reference-file {}"
        cmd = cmd.format(sharedir, wk, annotation, reference)
        # create the wokring directory and script
        subprocess.call(cmd.split())

        subprocess.call("sh variant_calling.sh".split(), cwd=wk)

        from sequana.freebayes_vcf_filter import VCF_freebayes, Variant
        vcf = VCF_freebayes(wk + "/data/freebayes/data.raw.vcf")
        vcf.rewind()
        vv = [Variant(v)._resume for v in vcf]
        # this may change depending on the freebayes version...
        assert len(vv) == pytest.approx(65, .1)
        vv = vv[0].copy()
        del vv['freebayes_score']
        del vv['fisher_pvalue']

        assert vv == {'alternative': 'T',
             'chr': 'JB409847',
             'depth': 23,
             #'freebayes_score': 2.78452e-14,
             'type': 'SNV',
             'frequency': '0.261',
             'position': '2221',
             'reference': 'C',
             'strand_balance': '0.333'}


def test_version():
    cmd = "sequana_variant_calling --version"
    subprocess.call(cmd.split())

def test_check_output_no_annotation():

    with tempfile.TemporaryDirectory() as wk:

        cmd = "sequana_variant_calling --input-directory {} "
        cmd += "--working-directory {} --run-mode local --force "
        cmd += " --reference-file {}"
        cmd = cmd.format(sharedir, wk, reference)
        # create the wokring directory and script
        subprocess.call(cmd.split())

        subprocess.call("sh variant_calling.sh".split(), cwd=wk)

        from sequana.freebayes_vcf_filter import VCF_freebayes, Variant
        vcf = VCF_freebayes(wk + "/data/freebayes/data.raw.vcf")
        vcf.rewind()
        vv = [Variant(v)._resume for v in vcf]
        # this may change depending on the freebayes version...
        assert len(vv) == pytest.approx(65, .1)
        vv = vv[0].copy()
        del vv['freebayes_score']
        del vv['fisher_pvalue']
        assert vv == {'alternative': 'T',
             'chr': 'JB409847',
             'depth': 23,
             #'freebayes_score': 2.78452e-14,
             'type': 'SNV',
             'frequency': '0.261',
             'position': '2221',
             'reference': 'C',
             'strand_balance': '0.333'}


def test_version():
    cmd = "sequana_variant_calling --version"
    subprocess.call(cmd.split())
