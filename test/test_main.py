import os
import tempfile
import subprocess
from sequana_pipelines.variant_calling.main import main
from click.testing import CliRunner

import pytest

from . import test_dir

sharedir = f"{test_dir}/data"
reference = sharedir+ os.sep + "JB409847.fasta"
annotation = sharedir + os.sep + "JB409847.gbk"


def test_standalone_subprocess():
    directory = tempfile.TemporaryDirectory()
    cmd = "sequana_variant_calling --input-directory {} "
    cmd += "--working-directory {}  --force --annotation-file {} "
    cmd += " --reference-file {}"
    cmd = cmd.format(sharedir, directory.name, annotation, reference)
    subprocess.call(cmd.split())



def test_standalone_script():

    wk = tempfile.TemporaryDirectory()
    runner = CliRunner()
    results = runner.invoke(main,
        ["--input-directory", sharedir, "--working-directory", wk.name, "--force", 
            "--annotation-file", annotation,
            "--reference-file", reference])
    assert results.exit_code == 0

def test_standalone_script_with_coverage():

    wk = tempfile.TemporaryDirectory()
    runner = CliRunner()
    results = runner.invoke(main,
        ["--input-directory", sharedir, "--working-directory", wk.name, "--force", 
            "--annotation-file", annotation, "--do-coverage",
            "--reference-file", reference])
    assert results.exit_code == 0




def test_check_output_ref_annot():

    with tempfile.TemporaryDirectory() as wk:

        cmd = "sequana_variant_calling --input-directory {} "
        cmd += "--working-directory {}  --force --annotation-file {} "
        cmd += " --reference-file {}"
        cmd = cmd.format(sharedir, wk, annotation, reference)
        # create the wokring directory and script
        subprocess.call(cmd.split())

        subprocess.call("sh variant_calling.sh".split(), cwd=wk)

        from sequana.variants import VariantFile

        vcf = VariantFile(wk + "/data/freebayes/data.raw.vcf")
        vv = [vcf._variant_to_dict(v) for v in vcf]
        # this may change depending on the freebayes version...
        assert len(vv) == pytest.approx(65, 2)
        vv = vv[0].copy()
        del vv['freebayes_score']
        del vv['fisher_pvalue']

        del vv['depth']
        del vv['frequency']
        del vv['strand_balance']
        del vv['ID']
        print(vv)
        assert vv == {'alternative': 'T',
             'chr': 'JB409847',
             #'depth': 24,
             'type': 'snp',
             #'frequency': '0.250',
             'position': 2221,
             'reference': 'C',
             #'strand_balance': '0.333'
            }


def test_version():
    cmd = "sequana_variant_calling --version"
    subprocess.call(cmd.split())

def test_check_output_no_annotation():

    with tempfile.TemporaryDirectory() as wk:

        cmd = "sequana_variant_calling --input-directory {} "
        cmd += "--working-directory {}  --force "
        cmd += " --reference-file {}"
        cmd = cmd.format(sharedir, wk, reference)
        # create the wokring directory and script
        subprocess.call(cmd.split())

        subprocess.call("sh variant_calling.sh".split(), cwd=wk)

        from sequana.variants import VariantFile
        vcf = VariantFile(wk + "/data/freebayes/data.raw.vcf")
        
        vv = [vcf._variant_to_dict(v) for v in vcf]
        # this may change depending on the freebayes version...
        assert len(vv) == pytest.approx(65, .1)
        vv = vv[0].copy()
        del vv['freebayes_score']
        del vv['fisher_pvalue']
        del vv['depth']
        del vv['frequency']
        del vv['strand_balance']
        del vv['ID']
        print(vv)
        assert vv == {'alternative': 'T',
             'chr': 'JB409847',
             #'depth': 24,   " sometimes 24 or 23
             #'freebayes_score': 2.78452e-14,
             'type': 'snp',
             #'frequency': '0.250',   # freebayes 1.3.9 gives 0.250 previous version were giving 0.261...
             'position': 2221,
             'reference': 'C',
             #'strand_balance': '0.333'
            }


def test_version():
    cmd = "sequana_variant_calling --version"
    subprocess.call(cmd.split())
