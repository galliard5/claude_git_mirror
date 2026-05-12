change filenames from map.svg to map.aimap.svg
error: (cairosvg not installed; skipping PNG output)

reword claude specific phrasing to something more agnostic. claude_map_dexcription becomes AI_map_description, claude_section_end becomes ai_context_depth, etc (get recomendations on exact phrasing)
can the current script handle being used from explorer? user drags a wxx or aimap.svg/anottation file combo on the script, and it can run using the files given?
add a clearcnce field for bridges. whats the distance between the surface of the water at normal conditions to the bottom of the bridge
add a depth field for rivers (deep, medium, shallow, fordable)
are unkeyed path conditions seen as just a string/notes? (-1, 38): to the cendrel border

are wxx poi's included in the svg, but not listed in the annotated file? concider pre-populating the annotatyin file with the wxx poi's (towns, bridges, etc)

check out the silberbach city map. used diferent conventions for labeling etc

near term goals

unify poi entries to a single format, rather than separate layouts for bridge/toll/etc?

include a location in the poi itself, rather than having to refer back to the path entry. 

check for line width and other metadata about paths in the .wxx file
concider automatic conversions for line width to river/road width? (river: width = width in meters? road: width =width in feet? half a foot?)

make sure it's safe for a road and a river to both reference the same poi

basic gui front end... open/save files, .svg preview window, generate blank annotation file from map, open anottation file in explorer/notepad/obsidian/editor of choice. 
open a specific wxx file for conversion, with svg preview and annotation file generation. 
include dark mode :o
save as standard .svg and other file tipes.. jpg, png, bmp, pdf.
choose a specific annotations file to merge with to generate a .aimap.svg. 
ensure the two files are actualy compatable..  basic md5 fingerprint generation on the graphic portion saved to the annotation file?


long term plans
concider an app to open the svg simultaneously with the annotations.md. start with a simple text editor, but look at a tabbed data entry style interface, to eventualy include hex path highlighting, the ability to select a specific hex and add poi's and notes etc.
keep raw text editing, to import poi/pathing data from previous iterations of a map
import/export of individual poi's for reuse?
global poi list for reusing common poi's?
image file/data sheet link embeding in poi locations on the graphical map?
same for nested parent/child maps?
automatic crosslinking path condition locations in the path descriptions to the poi entry.
ai agent integration for content generation etc? (client side ai agent using mcp calls to look inside the app to pull data, generate poi's etc)


eventual cool stuff:

built in hex map editor.
built in icon library editor.
figure out which is best for road/river pathing.. 
a) contiguous center-center, same format the path is currently listed in?
b) edge based? paths follow hex edges rather than crossing them
c) current spline based is ok for defining them, but in a standalone app, a or b would be easier to implement?

concider nested map references.. parent_map=aethelmark_worldmap.aimap.svg, map references in poi's silberbach/map_file=silberbach_citymap.aimap.svg

