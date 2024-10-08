Thank you for trying out the You Have To Win The Game randomizer!
This is version 1.3.
This was originally created by ZZKer and extended by Spontanicus.
If you have any questions or suggestions, feel free to contact me on discord @Spontanicus
or better yet, join the Win the Game [community server](https://discord.com/invite/bZs99rY).
If you find any seeds that don't work, please use this github to report it as an Issue.

## Version features

#### 1.3:
 - **Graphical User Interface for ease of use**
 - **Complete rework of the randomizer logic**.
Now uses a path-finding algorithm to check for valid configurations.
 - This version may contain softlocks - mainly by going to the blue orb area first and not finding any powerups there.
 - All treasure is now available for randomization
 - Added option to require all orbs to win
 - Added option to replace all other treasure with lose orbs
 - Added option to randomize the spawn location
 - Settings Seed to share your settings with others (will be more helpful as more options are added)
 - Seed can now be any alpha-numeric string, not just numbers.
 - Map includes additional paths for more routing options.

#### 1.2:
 -  Orbs are now randomized with most treasures (66/70 locations)
 -  Special map edit to prevent hardlocks, but not all possible softlocks ;)

#### 1.1:
 -  Special map edit designed for Randomizer to prevent softlocks.

#### 1.0:
 -  Orb randomization.
 -  Seeded random.
 -  BUG: Some seeds lead to softlocks if orbs are done in the wrong order. To avoid this, always go right at the beginning.

## Needed files:
 -  [Python 3.8.1 to run program](https://www.python.org/downloads/)
 -  [You Have to Win the Game example map](http://www.piratehearts.com/files/YHtWtG_Campaign.zip)
 -  You Have to Win the Game on Steam (available for free)

## Install:
 1. Make sure Python is installed
 2. Make sure You Have to Win the Game on Steam is installed and played at least once (to initialize folders)
 3. Unzip YHtWtG_Campaign.zip into C:\Users\\\[your user name\]\Documents\my games\You Have to Win the Game\Maps
 4. Extract the contents of the release archive to the Maps folder as well (same as in previous step)
    - Alternatively you can place these files in another folder and transfer the randomBase.map (only once) together 
with Rooms_random_{your_seed}.xml and random_{your_seed}.gam (for every generated seed) to the maps folder later
 -  That's it! :D

## To Run:
 1. Execute RandomizeYHTWTG.py to bring up the user interface.
 2. Check the options you want and enter the seed in the "Randomizer Seed" (leave empty for random seed).
 3. Click the "Randomize" button to create the randomized map.
 4. The new map will appear in your map list in-game.

## Options Explanation:
 -  Require All Orbs: All 4 orbs are required to reach the Win orb.
 -  Replace Treasure with Lose: Instead of money bags, all regular treasure is replaced with lose orbs.
 -  Shuffle Spawn Location: Spawns you at a random treasure location (regular spawn becomes a treasure).
 -  Difficulty: Lets you select between Unrestricted (all glitches), Glitchless and Custom (customized gltich settings + start with powerups).

## The Future:
 - [ ] more glitch options
 - [ ] new treasure locations
 - [ ] teleporter randomization
 - [ ] magic word randomization
 - [ ] bell and enemy randomization (maybe)
 - [ ] replace rooms with Spicy rooms (maybe)
 - [ ] room randomization (maybe, really difficult)
