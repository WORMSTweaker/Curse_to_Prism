import sys
import os
import json
import textwrap

import pkg_resources
from dataclasses import dataclass
from typing import List

###############
#
# Curseforge to PrismLauncher conversion script
# Quickly written by WORMSTweaker
# under the GPL-3.0-or-later License
#
###############

@dataclass
class ModFile:
    projectID: str
    fileID: str
    require: bool = True


@dataclass
class PrismManifest:
    minecraft_version: str
    forge_version: str
    name: str
    author: str
    overrides: str
    projectID: int
    projectVersion: int
    projectName: str
    files: List[ModFile]
    overridenFiles: List[str]
    version: str = ""


def decode_file(curse_file):
    f = open(curse_file)
    curse_manifest = json.load(f)

    try:
        instance_author = curse_manifest['manifest']['author']
        has_overrides = curse_manifest['manifest']['overrides']
        instance_version = curse_manifest['manifest']['version']
        project_name = curse_manifest['manifest']['name']
    except TypeError:
        print("Pack has no manifest field, manually made pack? Some values will be replaced")
        instance_author = curse_manifest['customAuthor']
        has_overrides = ""
        instance_version = "0.1"    # A default placeholder value
        project_name = curse_manifest['name']

    minecraft_version = curse_manifest['baseModLoader']['minecraftVersion']
    forge_version = curse_manifest['baseModLoader']['forgeVersion']
    instance_name = curse_manifest['name']
    project_id = curse_manifest['projectID']
    project_version = curse_manifest['fileID']
    modpack_overrides = curse_manifest['modpackOverrides']

    modfiles_list = []

    for i in curse_manifest['installedAddons']:
        # We specify the addonID (Curseforge mod ID), the fileID (Curseforge mod version ID), and if this mod is
        # required. Mods will ALWAYS be marked as "required", since Curseforge manifests don't care about
        # "facultative" mods
        modfiles_list.append(ModFile(i['addonID'], i['installedFile']['id']))

    f.close()
    return PrismManifest(minecraft_version, forge_version, instance_name, instance_author, has_overrides, project_id,
                         project_version, project_name, modfiles_list, modpack_overrides, instance_version)


def encode_prism_instance(curse_manifest):
    # Create flame and output directory
    output = curse_manifest.name
    print("Pack name: " + curse_manifest.name)
    print("Pack author: " + curse_manifest.author)
    print("Pack version: " + str(curse_manifest.version))
    print("Forge version: " + curse_manifest.forge_version)
    print("Minecraft version: " + curse_manifest.minecraft_version, end="\n\n")
    print("Pack files will be in " + output, end="\n\n")
    try:
        os.mkdir(output)
        os.mkdir(output + '/flame')
        print("Created output folder")
    except FileExistsError:
        print("Flame directory exists")

    # Generate modpack files overrides
    if curse_manifest.overridenFiles is not None and len(curse_manifest.overridenFiles) > 0:
        overrides = open(output + '/flame/overrides.txt', 'w')
        for i in curse_manifest.overridenFiles:
            i = i.replace('\\', '/')  # Path conversion. Might be needed, or not, who knows
            overrides.write(i + '\n')
        overrides.close()
        print("Generated overrides.txt")

    # Generate manifest.json
    manifest = open(output + '/flame/manifest.json', 'w')
    files = []
    for file in curse_manifest.files:
        files.append({"projectID": file.projectID, "fileID": file.fileID, "required": file.require})

    # Manifest template
    manifest_data = {
          "minecraft": {
            "version": curse_manifest.minecraft_version,
            "modLoaders": [
              {
                "id": "forge-" + curse_manifest.forge_version,  # Only support Forge packs, as I do not have a sample
                "primary": True                                 # of a Fabric modpack on Curse and Prism
              }
            ]
          },
          "manifestType": "minecraftModpack",
          "manifestVersion": 1,
          "name": curse_manifest.name,
          "version": curse_manifest.version,
          "author": curse_manifest.author,
          "projectID": curse_manifest.projectID,
          "files": files,
          "overrides": curse_manifest.overrides
        }
    json.dump(manifest_data, manifest)
    manifest.close()
    print("Generated manifest.json")

    # Generate instance.cfg
    # Use of textwrap dedent to keep a clean template
    instance_data = textwrap.dedent("""\
                    IgnoreJavaCompatibility=false
                    InstanceType=OneSix
                    JavaArchitecture=64
                    JavaPath=
                    JavaRealArchitecture=amd64
                    JavaTimestamp=
                    JavaVersion=
                    JoinServerOnLaunch=false
                    LogPrePostOutput=false
                    MCLaunchMethod=LauncherPart
                    ManagedPack=true
                    ManagedPackID=""" + str(curse_manifest.projectID) + """
                    ManagedPackName=""" + str(curse_manifest.name) + """
                    ManagedPackType=flame
                    ManagedPackVersionID=""" + str(curse_manifest.projectVersion) + """
                    ManagedPackVersionName=""" + str(curse_manifest.projectName) + """
                    MaxMemAlloc=
                    MinMemAlloc=
                    OverrideCommands=false
                    OverrideConsole=false
                    OverrideGameTime=false
                    OverrideJavaArgs=false
                    OverrideJavaLocation=false
                    OverrideMCLaunchMethod=false
                    OverrideMemory=false
                    OverrideMiscellaneous=false
                    OverrideNativeWorkarounds=false
                    OverridePerformance=false
                    OverrideWindow=false
                    PermGen=128
                    iconKey=default
                    lastLaunchTime=
                    lastTimePlayed=
                    name=""" + str(curse_manifest.name) + """
                    notes=
                    totalTimePlayed=""")  # TODO: Maybe implement playtime/lastplayed conversion? For now, not important

    instance = open(output + '/instance.cfg', 'w')
    instance.write(instance_data)
    instance.close()
    print("Generated instance.cfg")

    # Generate mmc-pack.json
    mmc_data = {
        "components": [
            {
                "cachedName": "Minecraft",
                "cachedRequires": [
                    {
                        "suggests": "2.9.4-nightly-20150209",
                        "uid": "org.lwjgl"
                    }
                ],
                "cachedVersion": "",
                "important": True,
                "uid": "net.minecraft",
                "version": ""
            },
            {
                "cachedName": "Forge",
                "cachedRequires": [
                    {
                        "equals": "",
                        "uid": "net.minecraft"
                    }
                ],
                "cachedVersion": "",
                "uid": "net.minecraftforge",
                "version": ""
            }
        ],
        "formatVersion": 1
    }

    mmc_data['components'][0]['cachedVersion'] = curse_manifest.minecraft_version
    mmc_data['components'][0]['version'] = curse_manifest.minecraft_version
    mmc_data['components'][1]['cachedRequires'][0]['equals'] = curse_manifest.minecraft_version
    mmc_data['components'][1]['cachedVersion'] = curse_manifest.forge_version
    mmc_data['components'][1]['version'] = curse_manifest.forge_version

    # This check MIGHT not be right, I am not sure which version switched to LWJGL3
    if pkg_resources.parse_version(curse_manifest.minecraft_version) > pkg_resources.parse_version("1.12.2"):
        print("1.13+ pack, setting LWJGL to 3")
        mmc_data['components'][0]['cachedRequires'][0]['suggests'] = "3.2.2"
        mmc_data['components'][0]['cachedRequires'][0]['uid'] = "org.lwjgl3"
        try:
            os.mkdir(output + '/minecraft')
        except FileExistsError:
            print("Minecraft directory exists")
    elif pkg_resources.parse_version(curse_manifest.minecraft_version) <= pkg_resources.parse_version("1.12.2"):
        print("1.12.2 or lower pack, setting LWJGL to 2")
        mmc_data['components'][0]['cachedRequires'][0]['suggests'] = "2.9.4-nightly-20150209"
        mmc_data['components'][0]['cachedRequires'][0]['uid'] = "org.lwjgl"
        try:
            os.mkdir(output + '/.minecraft')
        except FileExistsError:
            print(".minecraft directory exists")
    else:
        print("Uh oh, that's not supposed to happen, unsupported MC version!?")

    mmc = open(output + '/mmc-pack.json', 'w')
    json.dump(mmc_data, mmc, indent=4)
    mmc.close()
    print("Generated mmc-pack.json", end="\n\n")


def print_usage():
    print('Usage:')
    print('python curse_to_prism.py minecraftinstance.json')
    # TODO: Implement batch processing


if __name__ == '__main__':
    try:
        curse_manifest = decode_file(sys.argv[1:][0])
        encode_prism_instance(curse_manifest)
        print("Done. If everything went well, you should have an output folder named like your instance")
        print("Inside, you will have an instance.cfg file, mmc-pack.json file, a flame folder containing overrides.txt")
        print("and manifest.json, and finally a Minecraft (or .minecraft)")
        print("Copy the instance files in the Minecraft folder, then copy the instance folder in your 'instances' folder")
    except IndexError:
        print("Specify a curseforge manifest file")
        print_usage()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
