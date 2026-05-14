---
name: Directory Index with Files
keywords: [index, directory, structure, map]
description: Auto-generated directory tree snapshot including files
scan_utc: 2026-05-13T23:18:14Z
scan_local: 2026-05-13 23:18:14 UTC
claude_section_end: 932
---
## STARTUP PROCEDURE FOR CLAUDE

CHECK 1: Is directory_index.md loaded in this session?
  - NO: Skip remaining checks. Use this file normally.
  - YES: Proceed to CHECK 2.

CHECK 2: Compare scan_utc timestamps (YAML header).
  - This file NEWER: Discard directory_index.md. Use this file only.
  - directory_index.md NEWER: Proceed to CHECK 3.

CHECK 3: Compare compressed sections for structural differences.
  - IDENTICAL directories: Discard directory_index.md. Use this file only.
  - DIFFERENT directories: Keep both loaded.
    ⚠️ Directory structures may be inconsistent (one file is stale).
    ACTION: Recommend user run: python build_indexes.py

corpus
 .env
 .gitignore
 docker-compose.yml
 fancy ideas from browsing other mcp repositories.md
 file_system_instructions.md
 file_system_reference.md
 Isandar_Quickclaw_Skill_Tree.md
 README.md
 svg map format comments.md
 template.ai-story.json
 Core_Rules/
  core_rules.md
  Looting_Rules.md
  Model_Selection_Guide.md
  Scenario_Extraction_Rules.md
  Skill_Trees.md
  Wxx_Map_Format_Spec.md
  Templates/
   Character_Sheet_Template.md
   Checkpoint_Template.md
   Day_Brief_Template.md
   Faction_Organization_Template.md
   Location_Brief_Template.md
   Noble_House_Template.md
   Perchance_Campaign_Template.json
   Post_Session_Checklist.md
   Scenario_Package_Template.md
   Scenario_Template.md
   Scenario_Timeline_Template.md
   Session_Log_Condensed.txt
   Session_Log_Template.txt
   Session_Summary_Quick_Capture.md
   Session_Summary_System_Guide.md
   Skill_Tree_Block.md
   Timeline_Template.md
 index/
  directory_index.md
  directory_index_with_files.md
  search_index.db
 Miscelanious_RPG_material/
  Legion_ Sevhani's Tale.md
  Game_Masters_apprentice/
   GMA2e_Base_2025_5_3_PnP_Color.pdf
   GMA2e_Base_Deck.json
   GMA2e_Base_VTT.zip
   GMA2e_Complete_Reference.md
   GMA2e_Instructions_2025_05_04.pdf
  rpg books/
   1379792074.thenomeking_virile_insticts_-_a_deer_transformation_novella.pdf
   3EG601-AMPYearOne.pdf
   5E Player's Handbook.pdf
   AMP-Sheet2.pdf
   AMP_Year_Two_(7643525).pdf
   Black Crusade - Tome of Decay.pdf
   Cypher Shorts.pdf
   Cypher System - Revised Edition.pdf
   DSPG.rtf
   Epyllion_20160714.pdf
   fallout_pnp_2_0.pdf
   In_the_Company_of_Dragons.pdf
   In_the_Company_of_Dragons_PFRPG_v2.pdf
   Noble_Wild__lo-res_12-11-08.pdf
   OCC-RCC NetBook.rtf
   Only War - Hammer of The Emperor.pdf
   Playbooks_20160714.pdf
   Ponyfinder_-_Campaign_Setting_-_Dawn_of_the_Fifth_Age.pdf
   Races.txt
   Roan_-_Role_Playing_Game.pdf
   Shard RPG Basic Compendium.pdf
   Ships.txt
   Skyward Steel.pdf
   Star Trek Rpg - Decipher - Book 1 - Players Guide.pdf
   Starfinder CRB.pdf
   Starmada.pdf
   Stars Without Number - Core Edition.pdf
   StarsWithoutNumberRevised-FreeEdition-122917.pdf
   The Metamorphica.pdf
   The Quintessential Kobold.pdf
   The Stars Are Fire (Hyperlinked-and-Bookmarked) [2019-10-17].pdf
   Triten_Gaming_System.pdf
   Updates.txt
   World Tree RPG.pdf
   Worlds.txt
   cypher/
    Cypher Shorts.pdf
    Cypher System - Revised Edition.pdf
    The Stars Are Fire (Hyperlinked-and-Bookmarked) [2019-10-17].pdf
   DnD 5e/
    Dungeon Master's Guide.pdf
    Elemental Evil Player's Companion.pdf
    Monster Manual.pdf
    Player's Handbook.pdf
    Spell Lists.pdf
    Sword Coast Adventurer's Guide.pdf
   EP/
    Eclipse Phase-AnInfiniteHorizon.epub
    EclipsePhase_ElDestinoVerde.epub
    EclipsePhase_IntoTheWhite.epub
    EclipsePhase_Lack.epub
    EclipsePhase_Melt.epub
    PS+10000_Degenesis_Flat_Lowres.pdf
    PS+21000_EclipsePhase_3rdPrinting.pdf
    PS+21101_EP_Panopticon.pdf
    PS+21200_EP_Sunward.pdf
    PS+21201_EP_Gatecrashing.pdf
    PS+21806_TheStarsOurDestination_portrait.pdf
    hack pack/
     Chapter Opens.zip
     character_and_dice.psd
     Characters and Morphs.zip
     eclipsephase_cover.psd
     Gear.zip
     Logos.zip
   Ironclaw/
    dtrpg-2012-07-01_07-50pm.zip
    IRONCLAW_blank_character_sheet.pdf
    IRONCLAW_Book_of_Jade.pdf
    Ironclaw_sample_characters.pdf
    SGP1101_Ironclaw_Omnibus_-_Cover.pdf
    SGP1101_Ironclaw_Omnibus_-_Interior.pdf
    SGP1103_Ironclaw_Players_Book_-_Cover.pdf
    SGP1104_Ironclaw_Hosts_Book_-_Cover.pdf
   Star Wars FFG/
    Age Of Rebellion - Core Rulebook.pdf
    Edge of the Empire - Core Rulebook.pdf
    Force & Destiny - Core Rulebook.pdf
 Other_References/
  sample horizontal.png
  sample horizontal.wxx
  sample square map.png
  sample square map.wxx
  sample_horizontal_map.svg
  setup screen.png
  worldographer terrain.properties
  Wxx_Parsing_Reference.md
 Perchance_prompts/
  Isalias_Estate_Summary.md
  Perchance_AI_Story_Template.md
 Python/
  aethelmark_npcs_export.json
  aethelmark_npcs_export.txt
  batch_update_npcs.py
  build_indexes.py
  cfg_loader.py
  cleanup_legacy_tags.py
  convert_to_markdown.py
  Dockerfile
  index_tools_mcp_server.py
  indexer.cfg
  process_session_summary.py
  query_notion_npcs.py
  refresh_indexes.bat
  requirements.txt
  search_mcp_server.py
  validate_naming.py
  wxx_to_claude.py
  wxx_to_svg.py
  worldographer/
   extract_terrain_palette.py
   files.zip
   ideas.md
   python
   worldographer_atlas.py
   worldographer_palette.py
   wxx_annotations.py
   Wxx_Parsing_Reference.md
   wxx_to_claude.py
   wxx_to_svg.py
   icons/
    __init__.py
    battlemap.py
    cosmic.py
    town.py
    world.py
   projects/
    __init__.py
    aethelmark.py
    default.py
   terrain/
    __init__.py
    battlemap.py
    town.py
    world.py
 Sheet_Import/
  Processed/
   AutoTransfer Mabs wolf ranger Alina.json
   AutoTransfer Mags game.json
   AutoTransfer randoms hi level gestalt.json
   AutoTransfer randoms wyrmling gestalt.json
   Cits hi-powered rifts game - SDC Char Sheet.csv
   Cits MnM dragonstar game.por
   dragons3.xls.xlsx
   fallout deathclaw - Sheet1.csv
   G'lith.pdf
   galli - ricks empire recon.gcs
   galli -rics legion recon.pdf
   Galli's Eclipse Phase Game.pdf
   Galli's shadowrun.pdf
   Galli- rics legion empire scientist.gcs
   Galli.por
   GalliChar - Data.csv
   Garlic Eater DRAGON.pdf
   Garlic Eater.pdf
   Garlic_Eater.pdf
   Heskan.rptok
   heskan_content.xml
   Irooni's shadowrun.por
   Iskandai.por
   Iskandai_Dragon.pdf
   Iskandai_Worg.pdf
   James Dragon.json
   James Kitsune Oracle.json
   James shadowrun.pdf
   James shadowrun.por
   James-marvel-werewolf_detective.pdf
   Jasons dragon game - Witch.json
   kagi's ep game.xlsx
   Kai's HU game, Dragon bussiness tycoon - Heroes Unlimited.csv
   Kais legion empire.json
   Kaisens rifts game - Sheet1.csv
   KaiSF Writeup.docx
   Madila.rptok
   madila_content.xml
   Mags HU catbot - Sheet1.csv
   Ms Scales Cit.por
   Ms Scales Mich.por
   Ms Scales.pdf
   scales test.por
   Scales.por
   Sinani.pdf
   Sinani_Umbral_Dragon.pdf.url
   spell list and inventory accounting for silver.xlsx
   Tempest rising Evil witch.json
   TenariGuide.txt
   gcs Characters/
    Antoine Blumberg.png
    Antoine.pdf
    Arlie Mcgonigle.gcs
    CoC_0.6.2e.swf
    David Schalow.gcs
    David Schalow2.pdf
    Gia Schalow - Legion War Stories.gcs
    Gia Schalow - Legion War Stories.pdf
    Gia Schalow.gcs
    icarus Drone.gcs
    kais fantasy game.gcs
    Kais new new new legion game Armadillo Medic.gcs
    kais pirate space dolphin.gcs
    Kais quick fantasy.gcs
    Kais razor bug.gcs
    Kais rebooted space pirate dolphin.gcs
    Kitcat ucsc bug.gcs
    vikars space sheet.gcs
    Yu Piselli.gcs
    ~~Antoine Blumberg.html
   pcgen characters/
    Arezoli.pcg
    dndtf game.pcg
    Dragus kobold druid companion.pcg
    Dragus kobold druid.pcg
    Drogon fast robot.pcg
    Drogon fast robot.pcg.bak
    Drogon stroing robot.pcg
    Drogon stroing robot.pcg.bak
    Endrin of Hornwood.pcg
    Faralia's familiar.pcg
    Faralia.pcg
    Faralia.pcg.bak
    Faralia.TXT
    Fiarre.pcg
    gradea pseudodragon.pcg
    Isidora.pcg
    Jenney.pcg
    Jil.pcg
    Kai dnd game.pcg
    Leiane.pcg
    Mab rat mage.pcg
    mabs friend snake cleric.pcg
    magnus.pcg
    Marcos.pcg
    Miria.pcg
    Mourgram Uthelienn 2.Id_38268.pcg
    Mourgram Uthelienn.pcg
    New_design_of_wolf__s_armour_by_Okami_Kodokuna (for Tina).jpg
    Night.pcg
    Psicrysta 2l.Id_38273.pcg
    Psicrystal.pcg
    Ras Ben.pcg
    RasBen.pcg
    RasBenFamiliar.pcg
    ravy's evil kobold
    ravy's evil kobold.pcg
    ravy's evil kobold.pcg.bak
    ravy's evil kobold.txt
    Rosuto Mokuteki.pcg
    Roulin.pcg
    ryans level 20 druid.pcg
    Ryans level 21 mouse sorc.pcg
    Ryans level 21 mouse sorc.pcg.bak
    Sarashdar.pcg
    Sarashdardoc.pcg
    Seresha.pcg
    Sickles game.pcg
    Snuffles.pcg
    Soloni.pcg
    Starscream saturday morning kobold monk.pcg
    Tina.pcg
    Tina.pcg.bak
    turtles quick game.pcg
    visceroth.pcg
 Stories/
  biomancer.txt
  Brass_Case.txt
  got_milk.txt
  Integrated.txt
  isalia_boutique_1.txt
  Isalias_busy_day.txt
  lost_souls.txt
  off_to_semminary.txt
  riding_away.txt
  Sergovy_and_then_some.txt
  small.txt
  some_interesting_customers.txt
  soul_gem.txt
  Strange_Sacrifice.txt
  the_flower.txt
 System_Documentation/
  Architecture.md
  Docker_Filesystem.md
  Indexer.md
  README.md
  Search_Server.md
  Security_Audit.md
  Troubleshooting.md
 Trash/
 World_Building/
  Remade_Origin_Framework.md
  Reshaping_Trap_Tables.md
  Aethelmark/
   Aethelmark.md
   Hanging_Threads.md
   Laws_and_Framework.md
   Master_Calendar.md
   Skill_Tree_System.dot
   Skill_Tree_System.mermaid
   Skill_Tree_Visualization.md
   World_Standards.md
   Cendrel/
    Cendrel.md
    Kennel_Hounds_Setting.md
    Timeline_Kennel_Hounds.md
    Camp_Rochevaux/
     Buyers_Facility.md
     Camp_Rochevaux.md
     Characters/
      Aubert.md
      Celine_Daubray.md
      Duval.md
      Fabron.md
      Gate_Man.md
      Gervais_Tournon.md
      Gregor.md
      Grenn.md
      Halden_Creuse.md
      Joren.md
      Lenne_Souchard.md
      Mathis_Renard.md
      Perret.md
      Rill_Sunclaw.md
      Rill_Sunclaw_Skills.md
      Tessier.md
      The_Buyer.md
    Characters/
     Edouard_Vellancourt.md
    Maruvec/
     Maruvec.md
     Characters/
      Brac.md
      Colette_Varre.md
      Dix.md
      Isandar_Quickclaw.md
      Isandar_Quickclaw_Skill_Tree.md
      Kaz_Quickclaw.md
      Kess.md
      Maret_Aldec.md
      Perrin_Aldec.md
      Renne.md
      Sable_Venn.md
      Severin_Cault.md
      Silas_Drouet.md
      Theo_Marchais.md
      Yara_Quickclaw.md
    Vauclair/
     Vauclair.md
     Vauclair_Kennel.md
     Characters/
      Corvel.md
      Elise_Marenne.md
      Renaud_Bastier.md
      Sekkel.md
      Varne.md
     Clans/
      Rixek_Clan.md
      Sezzin_Clan.md
      Veth_Clan.md
   Scenarios/
    Cendrel/
     Camp_Rochevaux_Campaign/
      Camp_Rochevaux_Summary_1.md
      Camp_Rochevaux_Summary_2.md
      Camp_Rochevaux_Summary_3.md
      Camp_Rochevaux_Summary_4.md
      Camp_Rochevaux_Summary_5.md
      Camp_Rochevaux_Summary_6.md
      Camp_Rochevaux_Summary_7.md
      Rochevaux_Campaign.md
     Maruvec_Campaign/
      Maruvec_Campaign.md
      Maruvec_Perchance_Save_State.json
      Maruvec_Summary_1.md
      Maruvec_Summary_2.md
      Maruvec_Summary_3_MISSING.md
      Maruvec_Summary_4.md
      Maruvec_Summary_5.md
      Maruvec_Summary_6.md
     Vauclair_Campaign/
      Vauclair_Campaign.md
      Vauclair_Summary_1.md
    Isalias_Manor/
     Manor_Daily_Life.md
     Nobles_Commission_Session_01.md
     Nobles_Commission_Session_02.md
     Nobles_Commission_Session_03.md
     Nobles_Commission_Session_04.md
     Nobles_Commission_Session_05.md
     Nobles_Commission_Session_06.md
     Serya_Integration.md
     Day_Briefs/
      Day_01_Serya_Integration.md
      Day_02_Serya_Integration.md
    Scenario_prompts/
     Bandit_Recipe.md
     kennel_hounds_experiment1.md
     Silberbach_Setting_Prompt.md
     Wilderness_Garrison_Scouts.md
    Viktor_Steinfeld/
     Timeline_Viktor_Steinfeld.md
     Viktor_Steinfeld_Session_01.md
   Silberbach/
    Region/
     Aldenberg_Hold_Settlement.md
     Graudorf.md
     Halselund.md
     hex map screenshot.png
     Kaelens_Ford.md
     lake closeup.png
     map screenshot.png
     Meerhold.md
     Reinheim.md
     Rennic_Hall.md
     Rothwyn_Estate.md
     Silberbach CIty-autosave.wxx
     Silberbach CIty.wxx
     silberbach valley map-autosave.wxx
     silberbach valley map.wxx
     silberbach_valley_map.annotations.backup 1.md
     silberbach_valley_map.annotations.md
     silberbach_valley_map.svg
     silberbach_valley_map_v1.svg
     Steinfeld_Estate_Village.md
     test1.uvtt
     The_March_of_Silberbach.md
     Waldheim_Lodge_Settlement.md
     Westgate.md
     Characters/
      emperor_aldric.jpg
      Emperor_Aldric.md
     Factions/
      Guilds/
       Bakers_and_Butchers_Guild/
        Bakers_and_Butchers_Guild.md
        Characters/
       Blacksmiths_and_Metalworkers_Guild/
        Blacksmiths_and_Metalworkers_Guild.md
        Characters/
       Brewers_Guild/
        Brewers_Guild.md
        Characters/
         Drest.md
         Master_Heinrek_Vohlmann.md
       Carpenters_and_Masons_Guild/
        Carpenters_and_Masons_Guild.md
        Characters/
         Master_Joren_Vesker.md
         Master_Korin_Halberd.md
       Farmers_Guild/
        Farmers_Guild.md
        Characters/
         Brandt.md
         Master_Henrick_Cael.md
       Fullers_and_Dyers_Guild/
        Fullers_and_Dyers_Guild.md
        Characters/
       Merchants_Guild/
        Merchants_Guild.md
        Characters/
       Miners_Guild/
        Miners_Guild.md
        Characters/
       River_Traders_Guild/
        River_Traders_Guild.md
        Characters/
         Master_Rolf_Vannholt.md
         Senior_Dockmaster_Bero.md
       Tanners_and_Leatherworkers_Guild/
        Tanners_and_Leatherworkers_Guild.md
        Characters/
         Master_Edda_Reinhart.md
         Master_Yorik_Halsten.md
       Weavers_Guild/
        Weavers_Guild.md
        Characters/
         Hauss.md
         Sorren.md
      Manor/
       Industrial_Shops.md
       Infirmary.md
       Isalias_Manor.md
       Kennels_and_Stables.md
       Main_Building.md
       Manor_Reference.md
       Manor_Services.md
       Staff_Wing.md
       The_Apothecary.md
       The_Garden_Wing.md
       Characters/
        Animals/
         Vorro.md
        Clients/
         Aldric_Venn.md
         Corvin.md
         Elspeth_Voss.md
         Jesmine_Farrow.md
         Marta_Sehn.md
         Tomas_K_Rennic.md
         Wendel.md
        Companions/
         Kael_the_Amber_Manticore.jpg
         Kael_the_Amber_Manticore.md
         Lira_the_Sable_Doe.jpg
         Lira_the_Sable_Doe.md
         Nyssa_the_Moonlit_Vixen.jpg
         Nyssa_the_Moonlit_Vixen.md
         Pip.md
         Ryn.md
         Silas_the_Obsidian_Stallion.jpg
         Silas_the_Obsidian_Stallion.md
         Vix.md
        Owner/
         Isalia_Kreiger.jpg
         Isalia_Kreiger.md
         Isalia_Kreiger_Expanded_Background.md
        Peripheral_Staff/
         Anthony_Valtor.jpg
         Anthony_Valtor.md
         Dena.md
         Jaskin.md
         Liora.md
         Manor_Surrogate_Staff.md
         Marek.md
         Marta_Kitchen.md
         Petra.md
         Renn.jpg
         Renn.md
         Tob.md
         Vorik_the_Iron_Boar.jpg
         Vorik_the_Iron_Boar.md
        Senior_Staff/
         Alric_Dain.jpg
         Alric_Dain.md
         Captain_Albrecht_Vogt.jpg
         Captain_Albrecht_Vogt.md
         Dr_Selene_Korr.jpg
         Dr_Selene_Korr.md
         Elias_Varn.jpg
         Elias_Varn.md
         Elowen_Vale.jpg
         Elowen_Vale.md
         Kira_Lann.jpg
         Kira_Lann.md
         Lyra_Vex.jpg
         Lyra_Vex.md
         Mira_Toren.jpg
         Mira_Toren.md
         Rennik_Tor.jpg
         Rennik_Tor.md
         Sable_the_Mare.md
        Transformed_Residents/
         Goran.md
         Valerius_Corvinus.md
         Vesna.md
      Merchant_Families/
       House_Farrow/
        House_Farrow.md
        Characters/
         Garvin_Farrow.md
       House_Vale/
        House_Vale.md
        Characters/
       House_Welser/
        House_Welser.md
        Characters/
      Noble_Houses/
       House_Aldenberg/
        House_Aldenberg.md
        Characters/
         Mira_von_Aldenberg.md
       House_Grauwald/
        House_Grauwald.md
        Characters/
       House_Kaelen/
        House_Kaelen.md
        Characters/
         Aldric_Kaelen.md
         Baron_Torvin_Kaelen.jpg
         Baron_Torvin_Kaelen.md
         Elara_Kaelen.md
         Fenrik_Kaelen.md
         Torvin_Kaelen.md
       House_Kreiger/
        House_Kreiger.md
        Characters/
         Duchess_Iaxiandra_Kreiger.jpg
         Duchess_Iaxiandra_Kreiger.md
         Duke_Romaine_Kreiger.jpg
         Duke_Romaine_Kreiger.md
       House_Meerhold/
        House_Meerhold.md
        Characters/
       House_Rennic/
        House_Rennic.md
        Characters/
         lady_seria_rennic.jpg
         Lady_Seria_Rennic.md
         Lord_Edric_Rennic.md
         Lord_Tomas_R_Rennic.md
         Sir_Gareth_Rennic.md
         Tomas_K_Rennic.md
       House_Rothwyn/
        House_Rothwyn.md
        Characters/
         Florian_Rothwyn.md
         Lord_and_Lady_Rothwyn.md
       House_Steinfeld/
        House_Steinfeld.md
        Steinfeld_Estate.md
        Characters/
         Briar.md
         Edric_Bruck.md
         Hannah_Voss.md
         Lukas_Steinfeld.md
         Mrs_Aldenmarch.md
         Oswin_Brandt.md
         Pell.md
         Timothy.md
         Tomis_Bruck.md
         Viktor_Steinfeld.md
        Tenant_Farms/
         Bruck_Farm.md
         Kern_Farm.md
         Markel_Farm.md
       House_Valtor/
        House_Valtor.md
        Characters/
         Count_Elias_Valtor.jpg
         Count_Elias_Valtor.md
         gerran_valtor.jpg
         Gerran_Valtor.md
         Lady_Marguerite_Valtor.md
       House_Waldheim/
        House_Waldheim.md
        Characters/
         Sergovy_Waldheim.md
     Unique_Enchanted_Items/
      Decanter_of_Endless_Horse_Semen.md
      Isalias_Steel_Plug.md
      Portal_Panties.md
      Tantalus_Tease.md
      Transformation_Potion.md
    Town/
     Caravaners_way.md
     Market_Square.md
     Merchants_Close.md
     Silberbach.md
     Silberbach_Arrival.md
     The_Crescent_House.md
     The_Drowned_Rat.md
     The_Harbor_District.md
     The_Old_Temple.md
     The_Silver_Eel.md
     Valtor_Keep.md
     Vanders_Currency_Exchange.md
     Weavers_Row.md
     Characters/
      Aldren.md
      Aldus_Corvel.md
      Constable_Ferris.md
      Dietrich_Haan.md
      Fenk.md
      judge_thomas_kinsky.jpg
      Judge_Thomas_Kinsky.md
      Pol.md
      Voss_and_Kraemer.md
  Gallihammer/
   Biomancer.md
   Bioservitor.md
   Communication.md
   Cyberservitor.md
   Gallihammer- complete setting book.pdf
   Gallihammer_Overview.md
   Reshaping_Programme_Framework.md
   Reshaping_Trap_Tables.md
   Selenar_Origins.md
   The_Mechanicus.md
   The_Peoples.md
   The_Warp.md
   Archaeos_Expedition/
    Archaeos_Expedition_Overview.md
    Forge_Monastery_Valdrekk.md
    Characters/
     Proving_Ground_Crew.md
     Si_ken.md
    Recovered_Technology/
    Scenarios/
     Session_01_Briefing.md
     Si_ken_Prologue_Briefing.md
     Si_ken_Prologue_Summary.md
    Ship/
     The_Proving_Ground.md
    Sites/
   Dead_Terra/
    Dead_Terra_Factions.md
    Dead_Terra_Geography.md
    Dead_Terra_Overview.md
    Europan_Reaches.md
    Flaura_and_Fauna/
     Ambush_Reptiles.md
     Carnivorous_Flora.md
     Dead_Terra_Compendium_Master_Index.md
     Formica_War_Ants.md
     Humans_Terran_Baseline.md
     Hyper_Aggressive_Stinging_Insects.md
     Megafauna_Omnivores.md
     Pack_Hunters.md
     Parasitic_Fungal_Colonies.md
     Terran_Megafauna_Worms.md
     Terran_Microbial_Life.md
     Toxic_and_Chemical_Warfare_Plants.md
     Venomous_Serpents.md
    Scenarios/
     The_Crawl.md
   Equipment/
    Imperial_Relic_Weapons_Specific.md
    Reshaping_Cascade_Weapons_Detailed.md
    Vehicle_Weapons_Ship_Armament.md
    Weapons_Armour_Equipment.md
   Rogue_Trader/
    Crew_Roles.md
    Human_Cyber_Mastiff_Programme.md
    Looting_Rules.md
    Research_and_Manufacturing.md
    Rogue_Trader_Overview.md
    Ship_Combat_Forces.md
    Ship_Culture.md
    The_Fates_Cast.md
    Characters/
     Balphereon.md
     Copy of Johns Black Crusade Lxotl Renegade.xlsx
     Damien.md
     Gemszi.md
     Ito.md
     Johns 40k Sebastians psihound.xlsx
     Johns BC Heritek mouse Damien.xlsx
     Johns BC Night Lord Reptile Kerberos.xlsx
     Johns BC only war squad.xlsx
     Johns Black Crusade Lxotl Renegade.xlsx
     Kerberos.md
     Psihound.md
     Sebastian.md
     Valeriana_Servilia.md
    Locations/
     Eternity.md
     Talax_System.md
    Scenarios/
     Gemszi_Livestock_Conversion.md
     Gemszi_Session_01.md
     Gemszi_Session_01_Checkpoint.md
     Gemszi_Session_02_Checkpoint.md
     Gemszi_Session_03_Checkpoint.md
     Gemszi_Session_04_Checkpoint.md
     Gemszi_Session_05_Checkpoint.md
  Other_Projects/
   G_lith_Race_SWN.md
   KaiSF_Tauran_Vega.md
   Tenari_Guide.md
   Character_Pool/
    _GalliChar_MM_Reference.md
    _Import_TODO.md
    Allia_Meinwitz.md
    Allina.md
    Anthony_Wilmington.md
    Antoine_Blumberg.md
    Aranaea.md
    Arlie_Mcgonigle.md
    Astraea.md
    Brian_Hitchens.md
    Catbot.md
    Charlote.md
    Cits_Dragon_MnM.md
    Daniel_Sanchez.md
    David_Schalow.md
    DNDTF_Smart_Hero.md
    Dragon_Hatchling_Rifts.md
    Eve_Schallow.md
    Faralia.md
    Galli_MnM.md
    Gallibot.md
    Gia_Schalow.md
    Gia_Schalow_400.md
    Heskan.md
    Honi.md
    Ia_skel.md
    Icarus.md
    Icarus_Drone.md
    Icasus.md
    Incognito.md
    Isidora.md
    Iskandai.md
    Jagaima.md
    Jenney.md
    Jil.md
    Kalysto.md
    Kani.md
    Kelly.md
    Lash.md
    Leiane.md
    Madila.md
    Marcos.md
    Miria.md
    Mist_in_the_Wind.md
    Mourgram_Uthelienn.md
    Ms_Scales.md
    Night.md
    Ras_Ben_Gnoll_Cleric.md
    Ras_Ben_Kobold_Wizard.md
    Recon_Captain.md
    Riktiki.md
    Rosuto_Mokuteki.md
    Roulin.md
    Royal_Frilled_Dragon_Hatchling.md
    Saphira.md
    Sarashdar.md
    Scales_Galliard.md
    Scarlett_Dilallo.md
    Seresha.md
    Shami.md
    Shpni_Schallow.md
    Sickles_Cleric.md
    Silver.md
    Sinani.md
    Skrakle.md
    Soloni.md
    Tina.md
    Tom_pLUM.md
    Visceroth.md
    Yu_Piselli.md
   Little_spark/
    little_spark_skilltree.txt
    little_spark_summary1.txt
   Neon_Fang/
    Caldera_Corps.md
    Elsin_Curated_Companions.md
    Neon_Fang_Setting.md
    Neon_fang_summary.txt
    Verity_Biomedical.md
    Cells/
     Cell_Seven.md
    Characters/
     Cassian_Elsin.md
     Maren_Ashby.md
     Rael.md
   Souls_Gem/
    Characters/
     Father_Halric.md
     The_Captain.md
     The_Envoy.md
     The_Kobold.md
     The_Necromancer.md
     The_Witch.md
    Locations/
     The_Capital.md
     The_Necromancers_Tower.md
     The_Shrine_Town.md
     The_Witchs_Hut.md
    Scenarios/
     Soul_Gem_Scenario.md
     Soul_Gem_Story_So_Far.md
    Session_Summaries/
