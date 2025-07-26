import struct
import json
from enum import Enum, auto

region_list = [
{"map": "Limgrave", "name": "Church of Dragon Communion", "playRegion": 6100090, "bonfireFlags": {76110}, "isOpenWorld": True},
{"map": "Limgrave", "name": "The First Step, Church of Elleh", "playRegion": 6100000, "bonfireFlags": {76100, 76101}, "isOpenWorld": True},
{"map": "Limgrave", "name": "Seaside Ruins", "playRegion": 6100001, "bonfireFlags": {76113, 76106}, "isOpenWorld": True},
{"map": "Limgrave", "name": "Mistwood Outskirts, Fort Haight West", "playRegion": 6100004, "bonfireFlags": {76114, 76103, 76104, 76105}, "isOpenWorld": True},
{"map": "Limgrave", "name": "Agheel Lake North, Murkwater Coast, Gatefront Ruins", "playRegion": 6100002, "bonfireFlags": {76116, 76111, 76108}, "isOpenWorld": True},
{"map": "Limgrave", "name": "Summonwater Village Outskirts", "playRegion": 6100003, "bonfireFlags": {76119}, "isOpenWorld": True},
{"map": "Limgrave", "name": "Waypoint Ruins Cellar", "playRegion": 6100010, "bonfireFlags": {76120}, "isOpenWorld": True},
{"map": "Limgrave", "name": "Stormfoot Catacombs", "playRegion": 3002001, "bonfireFlags": {73002}, "isDungeon": True},
{"map": "Limgrave", "name": "Murkwater Catacombs", "playRegion": 3004001, "bonfireFlags": {73004}, "isDungeon": True},
{"map": "Limgrave", "name": "Groveside Cave", "playRegion": 3103001, "bonfireFlags": {73103}, "isDungeon": True},
{"map": "Limgrave", "name": "Coastal Cave", "playRegion": 3115001, "bonfireFlags": {73115}, "isDungeon": True},
{"map": "Limgrave", "name": "Murkwater Cave", "playRegion": 3100001, "bonfireFlags": {73100}, "isDungeon": True},
{"map": "Limgrave", "name": "Highroad Cave", "playRegion": 3117001, "bonfireFlags": {73117}, "isDungeon": True},
{"map": "Limgrave", "name": "Limgrave Tunnels", "playRegion": 3201001, "bonfireFlags": {73201}, "isDungeon": True},
{"map": "Stranded Graveyard", "name": "Cave of Knowledge", "playRegion": 1800090, "bonfireFlags": {71800}, "isDungeon": True},
{"map": "Stranded Graveyard", "name": "Stranded Graveyard", "playRegion": 1800001, "bonfireFlags": {71801}, "isDungeon": True},
{"map": "Stormhill", "name": "Stormhill", "playRegion": 6101000, "bonfireFlags": {76102, 71002, 76117, 76118}, "isOpenWorld": True},
{"map": "Stormhill", "name": "Margit, the Fell Omen", "playRegion": 6101010, "bonfireFlags": {71001}, "isBoss": True},
{"map": "Stormhill", "name": "Deathtouched Catacombs", "playRegion": 3011001, "bonfireFlags": {73011}, "isDungeon": True},
{"map": "Stormhill", "name": "Divine Tower of Limgrave", "playRegion": 3410090, "bonfireFlags": {73412, 73410}},
{"map": "Weeping Peninsula", "name": "Castle Morne", "playRegion": 6102001, "bonfireFlags": {76158, 76159, 76160}, "isBoss": True},
{"map": "Weeping Peninsula", "name": "Morne Moangrave", "playRegion": 6102020, "bonfireFlags": {76161}, "isBoss": True},
{"map": "Weeping Peninsula", "name": "Weeping Peninsula East", "playRegion": 6102000, "bonfireFlags": {76151, 76153, 76154, 76155, 76157}, "isOpenWorld": True},
{"map": "Weeping Peninsula", "name": "Weeping Peninsula West", "playRegion": 6102002, "bonfireFlags": {76150, 76152, 76156, 76162}, "isOpenWorld": True},
{"map": "Weeping Peninsula", "name": "Impaler's Catacombs", "playRegion": 3001001, "bonfireFlags": {73001}, "isDungeon": True},
{"map": "Weeping Peninsula", "name": "Tombsward Catacombs", "playRegion": 3000001, "bonfireFlags": {73000}, "isDungeon": True},
{"map": "Weeping Peninsula", "name": "Earthbore Cave", "playRegion": 3101001, "bonfireFlags": {73101}, "isDungeon": True},
{"map": "Weeping Peninsula", "name": "Tombsward Cave", "playRegion": 3102001, "bonfireFlags": {73102}, "isDungeon": True},
{"map": "Weeping Peninsula", "name": "Morne Tunnel", "playRegion": 3200001, "bonfireFlags": {73200}, "isDungeon": True},
{"map": "Stormveil Castle", "name": "Stormveil Main Gate, Stormveil Cliffside", "playRegion": 1000001, "bonfireFlags": {71008, 71004}},
{"map": "Stormveil Castle", "name": "Gateside Chamber", "playRegion": 1000006, "bonfireFlags": {71003}},
{"map": "Stormveil Castle", "name": "Rampart Tower", "playRegion": 1000003, "bonfireFlags": {71005}},
{"map": "Stormveil Castle", "name": "Liftside Chamber, Secluded Cell", "playRegion": 1000005, "bonfireFlags": {71006, 71007}, "isBoss": True},
{"map": "Stormveil Castle", "name": "Godrick the Grafted", "playRegion": 1000000, "bonfireFlags": {71000}, "isBoss": True},
{"map": "Liurnia of the Lakes", "name": "Liurnia South-East", "playRegion": 6200001, "bonfireFlags": {76217, 76200, 76201, 76202, 76203, 76244, 76221, 76222}, "isOpenWorld": True},
{"map": "Liurnia of the Lakes", "name": "Liurnia East", "playRegion": 6200004, "bonfireFlags": {76223, 76234, 76224, 76225, 76226}, "isOpenWorld": True},
{"map": "Liurnia of the Lakes", "name": "Behind Caria Manor", "playRegion": 6200008, "bonfireFlags": {76247, 76228, 76238}},
{"map": "Liurnia of the Lakes", "name": "Slumbering Wolf's Shack", "playRegion": 3105090, "bonfireFlags": {76215}},
{"map": "Liurnia of the Lakes", "name": "Liurnia South", "playRegion": 6200000, "bonfireFlags": {76205, 76204, 76216, 76236, 76241, 76243, 76242, 76233}, "isOpenWorld": True},
{"map": "Liurnia of the Lakes", "name": "Liurnia South-West", "playRegion": 6200002, "bonfireFlags": {76219, 76220, 76237}, "isOpenWorld": True},
{"map": "Liurnia of the Lakes", "name": "Liurnia West", "playRegion": 6200005, "bonfireFlags": {76218, 76210, 76227, 76213}, "isOpenWorld": True},
{"map": "Liurnia of the Lakes", "name": "Kingsrealm Ruins", "playRegion": 6200003, "bonfireFlags": {76212}, "isOpenWorld": True},
{"map": "Liurnia of the Lakes", "name": "Main Caria Manor Gate", "playRegion": 6200007, "bonfireFlags": {76214}, "isOpenWorld": True},
{"map": "Liurnia of the Lakes", "name": "Caria Manor", "playRegion": 6200007, "bonfireFlags": {76230}},
{"map": "Liurnia of the Lakes", "name": "Manor Lower Level", "playRegion": 6200007, "bonfireFlags": {76231}},
{"map": "Liurnia of the Lakes", "name": "Royal Moongazing Grounds", "playRegion": 6200010, "bonfireFlags": {76232}},
{"map": "Liurnia of the Lakes", "name": "The Ravine", "playRegion": 6200006, "bonfireFlags": {76235, 76229, 76211}, "isOpenWorld": True},
{"map": "Liurnia of the Lakes", "name": "Cliffbottom Catacombs", "playRegion": 3006001, "bonfireFlags": {73006}, "isDungeon": True},
{"map": "Liurnia of the Lakes", "name": "Road's End Catacombs", "playRegion": 3003001, "bonfireFlags": {73003}, "isDungeon": True},
{"map": "Liurnia of the Lakes", "name": "Black Knife Catacombs", "playRegion": 3005001, "bonfireFlags": {73005}, "isDungeon": True},
{"map": "Liurnia of the Lakes", "name": "Stillwater Cave", "playRegion": 3104001, "bonfireFlags": {73104}, "isDungeon": True},
{"map": "Liurnia of the Lakes", "name": "Lakeside Crystal Cave", "playRegion": 3105001, "bonfireFlags": {73105}, "isDungeon": True},
{"map": "Liurnia of the Lakes", "name": "Academy Crystal Cave", "playRegion": 3106001, "bonfireFlags": {73106}, "isDungeon": True},
{"map": "Liurnia of the Lakes", "name": "Main Academy Gate", "playRegion": 1400011, "bonfireFlags": {76206}},
{"map": "Liurnia of the Lakes", "name": "Raya Lucaria Crystal Tunnel", "playRegion": 3202001, "bonfireFlags": {73202}, "isDungeon": True},
{"map": "Liurnia of the Lakes", "name": "Divine Tower of Liurnia", "playRegion": 3411090, "bonfireFlags": {73422, 73421, 73420}},
{"map": "Bellum Highway", "name": "Bellum Highway", "playRegion": 6201000, "bonfireFlags": {76207, 76208, 76239, 76240}, "isOpenWorld": True},
{"map": "Bellum Highway", "name": "Grand Lift of Dectus, Jarburg", "playRegion": 6200090, "bonfireFlags": {76209, 76245}, "isOpenWorld": True},
{"map": "Ruin-Strewn Precipice", "name": "Ruin-Strewn Precipice", "playRegion": 3920002, "bonfireFlags": {73901}},
{"map": "Ruin-Strewn Precipice", "name": "Ruin-Strewn Precipice Overlook", "playRegion": 3920003, "bonfireFlags": {73902}, "isBoss": True},
{"map": "Ruin-Strewn Precipice", "name": "Magma Wyrm Makar", "playRegion": 3920000, "bonfireFlags": {73900}, "isBoss": True},
{"map": "Moonlight Altar", "name": "Moonlight Altar", "playRegion": 6202000, "bonfireFlags": {76250, 76251, 76252}},
{"map": "Academy of Raya Lucaria", "name": "Church of the Cuckoo", "playRegion": 1400013, "bonfireFlags": {71402}},
{"map": "Academy of Raya Lucaria", "name": "Schoolhouse Classroom", "playRegion": 1400015, "bonfireFlags": {71403}},
{"map": "Academy of Raya Lucaria", "name": "Debate Parlor", "playRegion": 1400010, "bonfireFlags": {71401}},
{"map": "Academy of Raya Lucaria", "name": "Raya Lucaria Grand Library", "playRegion": 1400000, "bonfireFlags": {71400}, "isBoss": True},
{"map": "Altus Plateau", "name": "Rampartside Path", "playRegion": 6300005, "bonfireFlags": {76305}, "isOpenWorld": True},
{"map": "Altus Plateau", "name": "Stormcaller Church, Lux Ruins", "playRegion": 6300000, "bonfireFlags": {76300, 76302}, "isOpenWorld": True},
{"map": "Altus Plateau", "name": "The Shaded Castle", "playRegion": 6300001, "bonfireFlags": {76320, 76321}},
{"map": "Altus Plateau", "name": "Altus Highway Junction", "playRegion": 6300002, "bonfireFlags": {76301, 76303}, "isOpenWorld": True},
{"map": "Altus Plateau", "name": "Castellan's Hall", "playRegion": 6300030, "bonfireFlags": {76322}},
{"map": "Altus Plateau", "name": "Forest-Spanning Greatbridge", "playRegion": 6300003, "bonfireFlags": {76304, 76306}, "isOpenWorld": True},
{"map": "Altus Plateau", "name": "Unsightly Catacombs", "playRegion": 3012001, "bonfireFlags": {73012}, "isDungeon": True},
{"map": "Altus Plateau", "name": "Sainted Hero's Grave", "playRegion": 3008001, "bonfireFlags": {73008}, "isDungeon": True},
{"map": "Altus Plateau", "name": "Sage's Cave", "playRegion": 3119001, "bonfireFlags": {73119}, "isDungeon": True},
{"map": "Altus Plateau", "name": "Perfumer's Grotto", "playRegion": 3118001, "bonfireFlags": {73118}, "isDungeon": True},
{"map": "Altus Plateau", "name": "Dominula, Windmill Village, Road of Iniquity Side Path", "playRegion": 6300004, "bonfireFlags": {76307, 76308, 76313}, "isOpenWorld": True},
{"map": "Altus Plateau", "name": "Old Altus Tunnel", "playRegion": 3204001, "bonfireFlags": {73204}, "isDungeon": True},
{"map": "Altus Plateau", "name": "Altus Tunnel", "playRegion": 3205001, "bonfireFlags": {73205}, "isDungeon": True},
{"map": "Mt. Gelmir", "name": "Ninth Mt. Gelmir Campsite", "playRegion": 6302000, "bonfireFlags": {76352, 76351, 76350}, "isOpenWorld": True},
{"map": "Mt. Gelmir", "name": "Road of Iniquity", "playRegion": 6302001, "bonfireFlags": {76353}, "isOpenWorld": True},
{"map": "Mt. Gelmir", "name": "Seethewater Terminus, Primeval Sorcerer Azur", "playRegion": 6302002, "bonfireFlags": {76354, 76355, 76356, 76357}, "isOpenWorld": True},
{"map": "Mt. Gelmir", "name": "Wyndham Catacombs", "playRegion": 3007001, "bonfireFlags": {73007}, "isDungeon": True},
{"map": "Mt. Gelmir", "name": "Gelmir Hero's Grave", "playRegion": 3009001, "bonfireFlags": {73009}, "isDungeon": True},
{"map": "Mt. Gelmir", "name": "Seethewater Cave", "playRegion": 3107001, "bonfireFlags": {73107}, "isDungeon": True},
{"map": "Mt. Gelmir", "name": "Volcano Cave", "playRegion": 3109001, "bonfireFlags": {73109}, "isDungeon": True},
{"map": "Capital Outskirts", "name": "Capital Outskirts", "playRegion": 6301000, "bonfireFlags": {76309, 76310, 76311, 76312}, "isOpenWorld": True},
{"map": "Capital Outskirts", "name": "Capital Rampart", "playRegion": 6301090, "bonfireFlags": {76314}, "isOpenWorld": True},
{"map": "Capital Outskirts", "name": "Auriza Side Tomb", "playRegion": 3013091, "bonfireFlags": {73013}, "isDungeon": True},
{"map": "Capital Outskirts", "name": "Auriza Hero's Grave", "playRegion": 3010001, "bonfireFlags": {73010}, "isDungeon": True},
{"map": "Capital Outskirts", "name": "Sealed Tunnel", "playRegion": 3412011, "bonfireFlags": {73431}, "isDungeon": True},
{"map": "Capital Outskirts", "name": "Divine Tower of West Altus", "playRegion": 3412090, "bonfireFlags": {73430, 73432}},
{"map": "Volcano Manor", "name": "Volcano Manor", "playRegion": 1600012, "bonfireFlags": {71602}},
{"map": "Volcano Manor", "name": "Prison Town Church", "playRegion": 1600014, "bonfireFlags": {71603}},
{"map": "Volcano Manor", "name": "Temple of Eiglay", "playRegion": 1600010, "bonfireFlags": {71601}},
{"map": "Volcano Manor", "name": "Guest Hall", "playRegion": 1600016, "bonfireFlags": {71604}},
{"map": "Volcano Manor", "name": "Audience Pathway", "playRegion": 1600006, "bonfireFlags": {71605}, "isBoss": True},
{"map": "Volcano Manor", "name": "Abductor Virgin", "playRegion": 1600020, "bonfireFlags": {71606}, "isDungeon": True},
{"map": "Volcano Manor", "name": "Subterranean Inquisition Chamber", "playRegion": 1600022, "bonfireFlags": {71607}},
{"map": "Volcano Manor", "name": "Rykard, Lord of Blasphemy", "playRegion": 1600000, "bonfireFlags": {71600}, "isBoss": True},
{"map": "Leyndell, Royal Capital", "name": "Erdtree Sanctuary", "playRegion": 1100010, "bonfireFlags": {71101}},
{"map": "Leyndell, Royal Capital", "name": "East Capital Rampart", "playRegion": 1100012, "bonfireFlags": {71102}},
{"map": "Leyndell, Royal Capital", "name": "Lower Capital Church", "playRegion": 1100015, "bonfireFlags": {71103}},
{"map": "Leyndell, Royal Capital", "name": "Avenue Balcony", "playRegion": 1100013, "bonfireFlags": {71104}},
{"map": "Leyndell, Royal Capital", "name": "Queen's Bedchamber", "playRegion": 1100001, "bonfireFlags": {71107}, "isBoss": True},
{"map": "Leyndell, Royal Capital", "name": "West Capital Rampart, Fortified Manor, First Floor", "playRegion": 1100016, "bonfireFlags": {71105, 71108}},
{"map": "Leyndell, Royal Capital", "name": "Divine Bridge", "playRegion": 1100017, "bonfireFlags": {71109}},
{"map": "Leyndell, Royal Capital", "name": "Elden Throne", "playRegion": 1100000, "bonfireFlags": {71100}, "isBoss": True},
{"map": "Subterranean Shunning-Grounds", "name": "Underground Roadside", "playRegion": 3500002, "bonfireFlags": {73501}},
{"map": "Subterranean Shunning-Grounds", "name": "Forsaken Depths", "playRegion": 3500008, "bonfireFlags": {73502}, "isBoss": True},
{"map": "Subterranean Shunning-Grounds", "name": "Leyndell Catacombs", "playRegion": 3500010, "bonfireFlags": {73503}},
{"map": "Subterranean Shunning-Grounds", "name": "Leyndell Catacombs Part II", "playRegion": 3500011, "bonfireFlags": {73503}},
{"map": "Subterranean Shunning-Grounds", "name": "Frenzied Flame Proscription", "playRegion": 3500092, "bonfireFlags": {73504}},
{"map": "Subterranean Shunning-Grounds", "name": "Cathedral of the Forsaken", "playRegion": 3500000, "bonfireFlags": {73500}},
{"map": "Leyndell, Ashen Capital", "name": "Leyndell, Capital of Ash", "playRegion": 1105011, "bonfireFlags": {71122, 71123}, "isBoss": True},
{"map": "Leyndell, Ashen Capital", "name": "Queen's Bedchamber ", "playRegion": 1105001, "bonfireFlags": {71124}, "isBoss": True},
{"map": "Leyndell, Ashen Capital", "name": "Divine Bridge ", "playRegion": 1105092, "bonfireFlags": {71125}},
{"map": "Leyndell, Ashen Capital", "name": "Elden Throne ", "playRegion": 1105000, "bonfireFlags": {71120}, "isBoss": True},
{"map": "Stone Platform", "name": "Fractured Marika", "playRegion": 1900000, "bonfireFlags": {71900}, "isBoss": True},
{"map": "Stone Platform", "name": "Elden Beast", "playRegion": 1900001, "bonfireFlags": {71900}, "isBoss": True},
{"map": "Caelid", "name": "Central Caelid", "playRegion": 6400001, "bonfireFlags": {76406, 76407, 76416, 76414, 76411, 76404, 76405, 76417, 76418}, "isOpenWorld": True},
{"map": "Caelid", "name": "Caelid North", "playRegion": 6400000, "bonfireFlags": {76400, 76401, 76403, 76410, 76402, 76409}, "isOpenWorld": True},
{"map": "Caelid", "name": "Chamber Outside the Plaza", "playRegion": 6400002, "bonfireFlags": {76420}, "isBoss": True},
{"map": "Caelid", "name": "Redmane Castle Plaza", "playRegion": 6400010, "bonfireFlags": {76419}},
{"map": "Caelid", "name": "Starscourge Radahn", "playRegion": 6400040, "bonfireFlags": {76422}, "isBoss": True},
{"map": "Caelid", "name": "Minor Erdtree Catacombs", "playRegion": 3014001, "bonfireFlags": {73014}, "isDungeon": True},
{"map": "Caelid", "name": "Caelid Catacombs", "playRegion": 3015001, "bonfireFlags": {73015}, "isDungeon": True},
{"map": "Caelid", "name": "War-Dead Catacombs", "playRegion": 3016001, "bonfireFlags": {73016}, "isDungeon": True},
{"map": "Caelid", "name": "Abandoned Cave", "playRegion": 3120001, "bonfireFlags": {73120}, "isDungeon": True},
{"map": "Caelid", "name": "Gaol Cave", "playRegion": 3121001, "bonfireFlags": {73121}, "isDungeon": True},
{"map": "Caelid", "name": "Gael Tunnel", "playRegion": 3207001, "bonfireFlags": {73207}, "isDungeon": True},
{"map": "Caelid", "name": "Gael Tunnel Part II", "playRegion": 3207002, "bonfireFlags": {73207}, "isDungeon": True},
{"map": "Caelid", "name": "Rear Gael Tunnel Entrance", "playRegion": 3207090, "bonfireFlags": {73257}, "isDungeon": True},
{"map": "Caelid", "name": "Sellia Crystal Tunnel", "playRegion": 3208001, "bonfireFlags": {73208}, "isDungeon": True},
{"map": "Caelid", "name": "Chair-Crypt of Sellia", "playRegion": 6400020, "bonfireFlags": {76415}, "isBoss": True, "isOpenWorld": True},
{"map": "Swamp of Aeonia", "name": "Swamp of Aeonia", "playRegion": 6401000, "bonfireFlags": {76412, 76413}, "isOpenWorld": True},
{"map": "Greyoll's Dragonbarrow", "name": "Dragonbarrow", "playRegion": 6402000, "bonfireFlags": {76450, 76451, 76453, 76452, 76455}, "isOpenWorld": True},
{"map": "Greyoll's Dragonbarrow", "name": "Sellia Hideaway", "playRegion": 3111001, "bonfireFlags": {73111}, "isDungeon": True, "isOpenWorld": True},
{"map": "Greyoll's Dragonbarrow", "name": "Dragonbarrow Cave", "playRegion": 3110001, "bonfireFlags": {73110}, "isDungeon": True, "isOpenWorld": True},
{"map": "Greyoll's Dragonbarrow", "name": "Bestial Sanctum", "playRegion": 6402001, "bonfireFlags": {76454, 76456}, "isOpenWorld": True},
{"map": "Greyoll's Dragonbarrow", "name": "Divine Tower of Caelid: Center", "playRegion": 3413003, "bonfireFlags": {73441}},
{"map": "Greyoll's Dragonbarrow", "name": "Divine Tower of Caelid: Basement", "playRegion": 3413013, "bonfireFlags": {73440}, "isBoss": True},
{"map": "Greyoll's Dragonbarrow", "name": "Isolated Divine Tower", "playRegion": 3415090, "bonfireFlags": {73460}},
{"map": "Forbidden Lands", "name": "Forbidden Lands", "playRegion": 6500000, "bonfireFlags": {76500}, "isOpenWorld": True},
{"map": "Forbidden Lands", "name": "Grand Lift of Rold", "playRegion": 6500090, "bonfireFlags": {76502}, "isOpenWorld": True},
{"map": "Forbidden Lands", "name": "Hidden Path to the Haligtree", "playRegion": 3020001, "bonfireFlags": {73020}, "isDungeon": True},
{"map": "Forbidden Lands", "name": "Hidden Path to the Haligtree Part II", "playRegion": 3020002, "bonfireFlags": {73020}, "isDungeon": True},
{"map": "Forbidden Lands", "name": "Divine Tower of East Altus", "playRegion": 3414011, "bonfireFlags": {73450, 73451}},
{"map": "Mountaintops of the Giants", "name": "Zamor Ruins", "playRegion": 6501000, "bonfireFlags": {76501, 76503}, "isOpenWorld": True},
{"map": "Mountaintops of the Giants", "name": "Central Mountaintops", "playRegion": 6501001, "bonfireFlags": {76505, 76504, 76520}, "isOpenWorld": True},
{"map": "Mountaintops of the Giants", "name": "Castle Sol", "playRegion": 6501002, "bonfireFlags": {76521}, "isOpenWorld": True},
{"map": "Mountaintops of the Giants", "name": "Spiritcaller's Cave", "playRegion": 3122001, "bonfireFlags": {73122}, "isDungeon": True},
{"map": "Mountaintops of the Giants", "name": "Castle Sol Main Gate, Church of the Eclipse", "playRegion": 6501003, "bonfireFlags": {76522, 76523}, "isOpenWorld": True},
{"map": "Mountaintops of the Giants", "name": "Castle Sol Rooftop", "playRegion": 6501010, "bonfireFlags": {76524}, "isBoss": True, "isOpenWorld": True},
{"map": "Flame Peak", "name": "Giants' Gravepost, Foot of the Forge", "playRegion": 6502000, "bonfireFlags": {76506, 76507, 76508}, "isOpenWorld": True, "isBoss": True},
{"map": "Flame Peak", "name": "Fire Giant", "playRegion": 6502010, "bonfireFlags": {76509, 76510}, "isBoss": True},
{"map": "Flame Peak", "name": "Giants' Mountaintop Catacombs", "playRegion": 3018001, "bonfireFlags": {73018}, "isDungeon": True},
{"map": "Flame Peak", "name": "Giant-Conquering Hero's Grave", "playRegion": 3017002, "bonfireFlags": {73017}, "isDungeon": True},
{"map": "Consecrated Snowfield", "name": "Consecrated Snowfield", "playRegion": 6503000, "bonfireFlags": {76550, 76551, 76652, 76653}, "isOpenWorld": True},
{"map": "Consecrated Snowfield", "name": "Consecrated Snowfield Catacombs", "playRegion": 3019001, "bonfireFlags": {73019}, "isDungeon": True},
{"map": "Consecrated Snowfield", "name": "Cave of the Forlorn", "playRegion": 3112001, "bonfireFlags": {73112}, "isDungeon": True},
{"map": "Consecrated Snowfield", "name": "Yelough Anix Tunnel", "playRegion": 3211001, "bonfireFlags": {73211}, "isDungeon": True},
{"map": "Miquella's Haligtree", "name": "Haligtree Canopy", "playRegion": 1500011, "bonfireFlags": {71506}},
{"map": "Miquella's Haligtree", "name": "Haligtree Town Plaza", "playRegion": 1500012, "bonfireFlags": {71507, 71508}, "isBoss": True},
{"map": "Miquella's Haligtree", "name": "Haligtree Promenade", "playRegion": 1500010, "bonfireFlags": {71505}, "isBoss": True},
{"map": "Elphael, Brace of the Haligtree", "name": "Prayer Room", "playRegion": 1500001, "bonfireFlags": {71501}},
{"map": "Elphael, Brace of the Haligtree", "name": "Elphael Inner Wall, Drainage Channel", "playRegion": 1500002, "bonfireFlags": {71503, 71502}},
{"map": "Elphael, Brace of the Haligtree", "name": "Haligtree Roots", "playRegion": 1500003, "bonfireFlags": {71504}, "isBoss": True},
{"map": "Elphael, Brace of the Haligtree", "name": "Malenia, Goddess of Rot", "playRegion": 1500000, "bonfireFlags": {71500}, "isBoss": True},
{"map": "Ainsel River", "name": "Ainsel River Well Depths", "playRegion": 1201001, "bonfireFlags": {71211, 71212}},
{"map": "Ainsel River", "name": "Ainsel River Downstream", "playRegion": 1201002, "bonfireFlags": {71213}},
{"map": "Ainsel River", "name": "Ainsel River Downstream Part II", "playRegion": 1201003, "bonfireFlags": {71213}},
{"map": "Ainsel River", "name": "Astel, Naturalborn of the Void", "playRegion": 1204000, "bonfireFlags": {71240}, "isBoss": True},
{"map": "Ainsel River", "name": "Dragonkin Soldier of Nokstella", "playRegion": 1201000, "bonfireFlags": {71210}},
{"map": "Ainsel River Main", "name": "Ainsel River Main", "playRegion": 1201011, "bonfireFlags": {71214}},
{"map": "Ainsel River Main", "name": "Nokstella, Eternal City", "playRegion": 1201013, "bonfireFlags": {71215}},
{"map": "Ainsel River Main", "name": "Nokstella Waterfall Basin", "playRegion": 1201014, "bonfireFlags": {71219}},
{"map": "Lake of Rot", "name": "Lake of Rot Shoreside", "playRegion": 1201015, "bonfireFlags": {71216}},
{"map": "Lake of Rot", "name": "Grand Cloister", "playRegion": 1201016, "bonfireFlags": {71218}},
{"map": "Lake of Rot", "name": "Grand Cloister Part II", "playRegion": 1201017, "bonfireFlags": {71218}},
{"map": "Nokron, Eternal City", "name": "Nokron, Eternal City", "playRegion": 1207026, "bonfireFlags": {71271}},
{"map": "Nokron, Eternal City", "name": "Mimic Tear", "playRegion": 1202020, "bonfireFlags": {71221}},
{"map": "Nokron, Eternal City", "name": "Ancestral Woods", "playRegion": 1202002, "bonfireFlags": {71224}},
{"map": "Nokron, Eternal City", "name": "Night's Sacred Ground", "playRegion": 1202007, "bonfireFlags": {71226}},
{"map": "Nokron, Eternal City", "name": "Aqueduct-Facing Cliffs", "playRegion": 1202003, "bonfireFlags": {71225}},
{"map": "Nokron, Eternal City", "name": "Aqueduct-Facing Cliffs Part II", "playRegion": 1202004, "bonfireFlags": {71225}, "isBoss": True},
{"map": "Nokron, Eternal City", "name": "Great Waterfall Basin", "playRegion": 1202000, "bonfireFlags": {71220}, "isBoss": True},
{"map": "Mohgwyn Palace", "name": "Palace Approach Ledge-Road", "playRegion": 1205001, "bonfireFlags": {71251}},
{"map": "Mohgwyn Palace", "name": "Dynasty Mausoleum Entrance", "playRegion": 1205004, "bonfireFlags": {71252}},
{"map": "Mohgwyn Palace", "name": "Dynasty Mausoleum Midpoint", "playRegion": 1205006, "bonfireFlags": {71253}, "isBoss": True},
{"map": "Mohgwyn Palace", "name": "Cocoon of the Empyrean", "playRegion": 1205000, "bonfireFlags": {71250}, "isBoss": True},
{"map": "Siofra River", "name": "Siofra River Well Depths", "playRegion": 1207031, "bonfireFlags": {71270}},
{"map": "Siofra River", "name": "Siofra River Bank", "playRegion": 1202033, "bonfireFlags": {71222}},
{"map": "Siofra River", "name": "Worshippers' Woods", "playRegion": 1202034, "bonfireFlags": {71223, 71227}},
{"map": "Deeproot Depths", "name": "Root-Facing Cliffs", "playRegion": 1203001, "bonfireFlags": {71231}},
{"map": "Deeproot Depths", "name": "Great Waterfall Crest Part II", "playRegion": 1203002, "bonfireFlags": {71232}},
{"map": "Deeproot Depths", "name": "Deeproot Depths", "playRegion": 1203003, "bonfireFlags": {71232, 71233}},
{"map": "Deeproot Depths", "name": "The Nameless Eternal City", "playRegion": 1203004, "bonfireFlags": {71234}},
{"map": "Deeproot Depths", "name": "Across the Roots", "playRegion": 1203005, "bonfireFlags": {71235}, "isBoss": True},
{"map": "Deeproot Depths", "name": "Prince of Death's Throne", "playRegion": 1203000, "bonfireFlags": {71230}, "isBoss": True},
{"map": "Crumbling Farum Azula", "name": "Crumbling Beast Grave", "playRegion": 1300012, "bonfireFlags": {71303}},
{"map": "Crumbling Farum Azula", "name": "Crumbling Beast Grave Depths, Tempest-Facing Balcony", "playRegion": 1300013, "bonfireFlags": {71304, 71305}},
{"map": "Crumbling Farum Azula", "name": "Dragon Temple", "playRegion": 1300017, "bonfireFlags": {71306}, "isBoss": True},
{"map": "Crumbling Farum Azula", "name": "Dragon Temple Transept", "playRegion": 1300018, "bonfireFlags": {71307}, "isBoss": True},
{"map": "Crumbling Farum Azula", "name": "Dragon Temple Altar", "playRegion": 1300010, "bonfireFlags": {71302}, "isBoss": True},
{"map": "Crumbling Farum Azula", "name": "Dragon Temple Lift", "playRegion": 1300019, "bonfireFlags": {71308}},
{"map": "Crumbling Farum Azula", "name": "Dragon Temple Rooftop", "playRegion": 1300003, "bonfireFlags": {71309}},
{"map": "Crumbling Farum Azula", "name": "Dragonlord Placidusax", "playRegion": 1300020, "bonfireFlags": {71301}, "isBoss": True},
{"map": "Crumbling Farum Azula", "name": "Beside the Great Bridge", "playRegion": 1300006, "bonfireFlags": {71310}, "isBoss": True},
{"map": "Crumbling Farum Azula", "name": "Maliketh, the Black Blade", "playRegion": 1300000, "bonfireFlags": {71300}, "isBoss": True}
]

affinity_enum = {
    0: "None",
    1: "Heavy",
    2: "Keen",
    3: "Quality",
    4: "Fire",
    5: "Flame",
    6: "Lightning",
    7: "Sacred",
    8: "Magic",
    9: "Cold",
    10: "Poison",
    11: "Blood",
    12: "Occult"
}

ITERATION_COUNT = 0x1400


def check_bosses(data, base_pointer, boss_list):
    slain_bosses = []
    for boss_dict in boss_list:
        byte = int(boss_dict["byte_offset"], 16)
        bit = boss_dict["bit"]
        bit_mask = 1 << bit

        byte_to_check = base_pointer + byte
        data_byte = struct.unpack_from('<B', data, byte_to_check)[0]


        if bit_mask & data_byte != 0:
            name = boss_dict["name"]
            slain_bosses.append({
                "name": name,
                "main": boss_dict["remembrance"],
                "dlc": boss_dict["is_dlc"]
            })
    
    return slain_bosses

def check_graces(data, base_pointer, graces):
    visited_graces = []
    for grace_dict in graces:
        byte = int(grace_dict["byte_offset"], 16)
        bit = grace_dict["bit_index"]
        bit_mask = 1 << bit

        byte_to_check = base_pointer + byte
        data_byte = struct.unpack_from('<B', data, byte_to_check)[0]


        if bit_mask & data_byte != 0:
            visited_graces.append(grace_dict)
    
    return visited_graces

            



def analyse(relative, path, table, character_id, boss_list, graces):
    region_map = {entry["playRegion"]: entry["name"] for entry in region_list}
    print(f"\n--- Parsing file '{path}' ---")
    with open(relative+path, 'rb') as f:
        data = f.read()
    iVar10 = 0x330 + (character_id * 0x280010)
    i = 1
    for _ in range(ITERATION_COUNT):
        address = iVar10
        ga_item_handle, item_id = struct.unpack_from('<II', data, address)
        category = item_id & 0xF0000000
        if category == 0:
            if item_id != 0x0001ADB0:
                pure_item_id = item_id - (item_id % 10000)
                item_str = f"0x{pure_item_id:08X}"
                item_name = table.get(item_str, "unknown")
                item_enchant = (item_id // 100) % 100
                item_upgrade = item_id % 100
                print(f"{i}. Weapon - {hex(ga_item_handle)} - {item_str} - {item_name}{f" (Real id - {hex(item_id)}). Enchant - {affinity_enum.get(item_enchant)}. Upgrade - {item_upgrade}" if pure_item_id != item_id else ""}")
                i += 1
            iVar10 += 0x15
        elif category == 0x10000000:
            iVar10 += 0x10
        else:
            iVar10 += 0x8

    print(f"\n- The offset after the ga_items structure is {hex(iVar10)}")
    uVar11 = iVar10 + 0x94cc
    print(f"- Adding 0x94cc, offset is now {hex(uVar11)}")
    items_1 = struct.unpack_from('<I', data, uVar11)[0]
    print(f"- Number of items to skip - {items_1}")
    active = False
    if active:
        tester_offset = uVar11 + 0x4
        for i in range(items_1):
            item_id, flag = struct.unpack_from('<II', data, tester_offset)
            item_hex = f"0x{item_id:08X}"
            item_name = table.get(item_hex, "Unknown")
            if i < 10:
                print(f"  - {item_hex} : {flag} - {item_name}" )
            tester_offset += 0x8
    uVar11 += items_1 * 8 + 0x62EB
    print(f"- Skipping {items_1} items, adding 0x62EB. Address is now {hex(uVar11)}")
    items_2 = struct.unpack_from('<I', data, uVar11)[0]
    print(f"- Number of items to skip - {items_2}")
    active = False
    if active:
        tester_offset = uVar11 + 0x4
        for i in range(items_2):
            item_id = struct.unpack_from('<I', data, tester_offset)[0]
            item_hex = f"0x{item_id:08X}"
            if i < 10:

                #print(f"  - {i+1}. {item_id}")
                if item_id in region_map.keys():
                    print(f"Id {item_id}: {region_map[item_id]}")
                else:
                    print(f"Id not found: {item_id}")
            tester_offset += 0x4
    uVar11 += (items_2 * 4) + 0x1c641
    print(f"- Skipping {items_2} items, adding 0x1C641. Address is now {hex(uVar11)}")
    event_flags_region_offset = struct.unpack_from('<I', data, uVar11)[0]
    print(f"- Reading final relative offset from {hex(uVar11)}: {hex(event_flags_region_offset)}")
    event_flags_base_addr = uVar11 + event_flags_region_offset + 0x21
    print(f"- Final Event Flag Base Address is {hex(event_flags_base_addr)}")

    slain_bosses = check_bosses(data, event_flags_base_addr, boss_list)
    if not slain_bosses:
        print("\n- No slain bosses found")
        return
    print(f"\n- Found {len(slain_bosses)} slain bosses!\n")
    for entry in sorted(slain_bosses, key=lambda e: e["name"]):
        print(f"  - {entry['name']}{' (MAIN BOSS)' if entry['main'] else ''}{' (DLC)' if entry['dlc'] else ""}")

    visited_graces = check_graces(data, event_flags_base_addr, graces)
    if not visited_graces:
        print("\n- No visited graces found")
        return
    print(f"\n- Found {len(visited_graces)} visited graces!\n")
    for entry in sorted(visited_graces, key=lambda e: e["name"]):
        print(f"  - {entry['id']}: {entry['name']}")
        
        



PATH_LIST = "after.sl2", "borjom.sl2", "alexander.sl2"
relative = 'extraction&testing/'
with open(f'{relative}util/item_dict.json', 'r', encoding='utf8') as f:
    data = json.load(f)
with open(f'{relative}util/boss_data.json', 'r', encoding='utf-8') as f:
    boss_list = json.load(f)
with open(f'{relative}util/graces_map.json', 'r', encoding='utf-8') as f:
    graces = json.load(f)
for entry in PATH_LIST:
    analyse(relative, entry, data, 0, boss_list, graces)
