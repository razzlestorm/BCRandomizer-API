SEED=42069
rm program.$SEED.rom program.$SEED.rom.bak program.$SEED.rom.wine
python randomizer.py program.rom .$1.$SEED test
mv program.$SEED.rom program.$SEED.rom.bak
wine-development beyondchaos.exe program.rom .$1.$SEED
mv program.$SEED.rom program.$SEED.rom.wine
python randomizer.py program.rom .$1.$SEED test
diff program.$SEED.rom program.$SEED.rom.bak
diff program.$SEED.rom program.$SEED.rom.wine
diff program.$SEED.rom.bak program.$SEED.rom.wine
