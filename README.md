# Curseforge Instance to Prism Launcher instance
A quick & dirty Python 3 script to convert a Curseforge/Twitch Launcher `minecraftinstance.json` to a PrismLauncher.

## How to use?
Simply run the script with python, with the `minecraftinstance.json` path as the first argument:
```commandline
python3 curse_to_prism.py minecraftinstance.json
```
The script will output a folder named like your instance.

No Python dependencies should be needed to run this script, but be sure to run it on a recent version of Python.

## Why make this?
Because when I searched around, I could not find a decent converter for this exact case.
I changed launcher a long time ago, and kept my old instances around but never exported them. Since such a tool never existed, I was left with useless Minecraft instance that I couldn't use with modern solutions.

This is where this script comes in, and let me recover those old instances and convert them to another, more modern format.

## Will it be maintained?
Maybe. This is supposed to be a quick project because I needed it on the moment. If I were to maintain it, here's the features I'd add:
    - [ ] Batch processing
    - [ ] Automatically copy the instance files in the new folder (goes in pair with batch processing)
    - [ ] Playtime/lastplayed time conversion
    - [ ] Fabric modpacks
    - [ ] Adding other information like memory or override arguments

## Licensing
This project is licensed under the [GPL-3.0-or-later license](COPYING.md) ([What does that mean?](https://choosealicense.com/licenses/gpl-3.0))
You can use this script however you feel like, but you may NOT redistribute it under closed sources. The license must be preserved if used in a project.
