import easydev
import os
import tempfile
import subprocess
import sys


sequana_path = easydev.get_package_location('sequana_variant_calling')
sharedir = os.sep.join([sequana_path , "sequana_pipelines/variant_calling", 'data'])
reference = os.sep.join([sequana_path , "sequana_pipelines/variant_calling", 'data']) + os.sep + "JB409847.fasta"
annotation = os.sep.join([sequana_path , "sequana_pipelines/variant_calling", 'data']) + os.sep + "JB409847.gbk"


def test_standalone_subprocess():
    directory = tempfile.TemporaryDirectory()
    cmd = "sequana_pipelines_variant_calling --input-directory {} "
    cmd += "--working-directory {} --run-mode local --force --annotation {} "
    cmd += " --reference {}"
    cmd = cmd.format(sharedir, directory.name, annotation, reference)
    subprocess.call(cmd.split())



#def test_standalone_script():
#    directory = tempfile.TemporaryDirectory()
#    import sequana_pipelines.variant_calling.main as m
#    sys.argv = ["test", "--fastq-directory", sharedir, "--output-directory",
#        directory.name, "--run-mode", "local", "--force"]
#    m.main()
