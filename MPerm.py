#!/usr/bin/env python3
"""
MPerm: Base driver for the analysis tool.
"""

import shutil
import sys
import subprocess
import xml.etree.ElementTree as ET

from Harvest import Harvest
from Report import Report

def get_manifest_tree(project_root):
    """Parses AndroidManifest into XML tree."""
    manifest = project_root + "/app/AndroidManifest.xml"
    tree = ET.parse(manifest)
    return tree

def get_package_name(manifest_tree):
    """Analyze manifest to see package name of app."""
    root = manifest_tree.getroot()
    return root.attrib['package']

def get_third_party_permissions(manifest_tree):
    """Analyze manifest to see what permissions to request."""
    root = manifest_tree.getroot()
    values = []
    third_party = set()
    for neighbor in root.iter('uses-permission'):
        values.append(list(neighbor.attrib.values()))
    for val in values:
        for perm in val:
            if 'com' in perm:
                third_party.add(perm)
    return third_party

def get_all_permissions(manifest_tree):
    """Analyze manifest to see what permissions to request."""
    root = manifest_tree.getroot()
    permissions = set()
    values = []
    for neighbor in root.iter('uses-permission'):
        values.append(list(neighbor.attrib.values()))
    for val in values:
        for perm in val:
            permissions.add(perm)
    return permissions


def decompile(apk_path):
    """
    Only decompile the provided APK. The decompiled APK will be
    left within the same directory.
    """
    apk_name = apk_path.rsplit('/', 1)[-1]

    print("Decompiling " + apk_name)
    subprocess.call(["./android-scraper/tools/apk-decompiler/apk_decompiler.sh", apk_path])
    print("Decompilation finished!")
    print("Moving " + apk_name + " to sample_apks/...")
    try:
        shutil.move("android-scraper/tools/apk-decompiler/" + apk_name +
                    ".uncompressed", "sample_apks/" + apk_name + ".uncompressed")
        print("Move finished! Check sample_apks/ for the decompiled app.")
    except FileNotFoundError:
        print("Error: couldn't find "
              + apk_name + ".It might already be in sample_apks/")

def main():
    """Primary driver of MPermission. """
    arguments = sys.argv
    source_path = ""
    if len(arguments) < 3:
        print("Error: missing arguments. ")
        exit(1)
    elif len(arguments) >= 3 and len(arguments) < 5:
        source_path = arguments[1]
        if '-h' in arguments:
            manifest_tree = get_manifest_tree(source_path)
            package_name = get_package_name(manifest_tree)
            permissions = get_all_permissions(manifest_tree)
            third_party_permissions = get_third_party_permissions(manifest_tree)

            # Scrape the source
            harvest = Harvest(source_path, package_name, permissions)
            source_report = harvest.search_project_root()

            # Analyze and print results
            report = Report(package_name, permissions, third_party_permissions)
            report.print_analysis(permissions, source_report)

        elif '-d' in arguments:
            decompile(source_path)

if __name__ == "__main__":
    main()
