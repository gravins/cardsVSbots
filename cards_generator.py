import pandas as pd
import gender_guesser.detector as gender
import holidays
import random
import re
from thesaurus import Word
from multiprocessing import Process
import json
import pickle
import swapi
import time
import sys
sys.path.insert(0, 'en/')
from verb import verb_conjugate, verb_infinitive


def print_tracery(tracery, name="project_Alessio_Gravina", last=["origin"]):
    pickle.dump(tracery, open(name + ".p", "wb"))

    with open(name + ".txt", "w") as j:
        j.write("{\n")
        for k in tracery.keys():
            if k not in last:
                j.write("\t \""+k+"\": [")
                for i in range(len(tracery[k])):
                    if i < len(tracery[k])-1:
                        j.write("\""+tracery[k][i]+"\""+",")
                    else:
                        j.write("\""+tracery[k][i]+"\"" + "],\n")
        for k in last[:-1]:
            j.write("\t \"" + k + "\": [")
            for i in range(len(tracery[k])):
                if i < len(tracery[k]) - 1:
                    j.write("\""+tracery[k][i]+"\"" + ",")
                else:
                    j.write("\""+tracery[k][i]+"\"" + "],\n")
        k = "origin"
        j.write("\t \"" + k + "\": [")
        for i in range(len(tracery[k])):
            if i < len(tracery[k]) - 1:
                j.write("\""+tracery[k][i]+"\"" + ",")
            else:
                j.write("\""+tracery[k][i]+"\"" + "]\n}")


def black_main():
    start_b = time.time()
    wildcard = "______"
    tracery = {
        "origin": ["#_sentence#"],
        "_p": ["[char-H:his][char-h:himself][name:#_male_char#]", "[char-H:her][char-h:herself][name:#_female_char#]"],
        "_sentence": []
    }

    funniest = pd.read_csv("funniest-actors.csv")
    veale_char = pd.read_excel("NOCList.xlsx")
    veale_char = veale_char.fillna('')
    tracery["_noc_people"] = [c.replace('"', '\\"') for c in veale_char["Character"].values]

    # Adding new type of sentece
    tracery["_sentence"].append("[#_p#]To prepare for #char-H# upcoming role, #name# immersed #char-h# in the world of " + wildcard + ".")
    tracery["_male_char"] = []
    tracery["_female_char"] = []
    detector = gender.Detector()
    for f in funniest["Name"]:
        index = veale_char.index[veale_char["Character"].str.contains(f)]
        if len(index) > 0:
            char = veale_char.at[index[0], "Gender"]
            if char == "male":
                tracery["_male_char"].append(f)
            elif char == "female":
                tracery["_female_char"].append(f)
            else:
                print("Gender of " + f + " in Character, not recognized")
        else:
            index = veale_char.index[veale_char["Canonical Name"].str.contains(f)]
            if len(index) > 0:
                canonical = veale_char.at[index[0], "Gender"]
                if canonical == "male":
                    tracery["_male_char"].append(f)
                elif canonical == "female":
                    tracery["_female_char"].append(f)
                else:
                    print("Gender of " + f + " in Canonical Name, not recognized")
            else:
                index = veale_char.index[veale_char["AKA"].str.contains(f)]
                if len(index) > 0:
                    aka = veale_char.at[index[0], "Gender"]
                    if aka == "male":
                        tracery["_male_char"].append(f)
                    elif aka == "female":
                        tracery["_female_char"].append(f)
                    else:
                        print("Gender of " + f + " in AKA, not recognized")
                else:
                    gen = detector.get_gender(f.split(" ")[0])
                    if gen == "male":
                        tracery["_male_char"].append(f)
                    elif gen == "female":
                        tracery["_female_char"].append(f)
                    else:
                        print("Gender of " + f + " not recognized from gender detector")
    del funniest

    # Adding new type of sentece
    tracery["_sentence"].append("[#_f#]Life of #_name# was forever changed when #_opponent# introduce #_char-H# to " + wildcard + ".")
    tracery["_f"] = []
    for row in veale_char.iterrows():
        if row[1]["Opponent"] != "":
            opponents = row[1]["Opponent"].replace('"', '\\"').split(", ")
            pron = "him" if row[1]["Gender"] == "male" else "her"
            if len(opponents) > 1:
                tracery[row[1]["Character"].replace('"', "").replace(" ", "-")+"-opponent"] = opponents
                tracery["_f"].append("[_char-H:"+pron+"][_name:"+row[1]["Character"].replace('"', '\\"')+"][_opponent:#"+row[1]["Character"].replace('"', "").replace(" ", "-")+"-opponent#]")
            else:
                tracery["_f"].append("[_char-H:" + pron + "][_name:" + row[1]["Character"].replace('"', '\\"') + "][_opponent:" + opponents[0] + "]")

    # Adding new type of sentece
    tracery["_sentence"].append("#_male_char#, here for " + wildcard + ".")
    tracery["_sentence"].append("#_female_char#, here for " + wildcard + ".")

    # Adding new type of sentece
    tracery["_sentence"].append("Every #_holiday# my #_family_member# gets drunk and tells the story about " + wildcard + ".")
    family = pd.read_csv("family.csv")
    tracery["_family_member"] = family["Name"].values.tolist()
    tracery["_holiday"] = list(holidays.US(years=2019).values())
    del family

    # Adding new type of sentece
    prep = pd.read_csv("preposition.csv")
    tracery["_preposition"] = prep.head(4)["Word"].tolist()
    del prep
    tracery["_dd"] = ["day", "night", "month", "week", "year"]
    tracery["_oo"] = ["drinking", "video games", "#_video_games#", "drugs", "#_drugs#", "sex", "#_sex_noun#"]
    tracery["_event"] = ["#_holiday#", "long #_dd#", "big #_dd#", "night of #_oo#"]
    tracery["_action"] = [wildcard + " relaxes me", wildcard + " makes me mad", wildcard + " freaks me out"]
    tracery["_sentence"].append("#_preposition.capitalize# #_event.a#, #_action#.")

    sex_act = pd.read_csv("sex-activities.csv")
    tracery["_sex_noun"] = sex_act[sex_act["grammar"] == "noun"]["word"].tolist()
    del sex_act
    with open("sexual_acts.txt", "r") as f:
        for line in f.readlines():
            tracery["_sex_noun"].append(line.replace(" \n", "").replace("\n", "").lower())
        f.close()

    drugs = pd.read_excel("drugs.xlsx")
    tracery["_drugs"] = drugs["Name"].values
    del drugs

    games = pd.read_csv("best_games.csv")
    tracery["_video_games"] = games["Game"].values
    del games

    nat_db = pd.read_csv("nationalities.csv")
    tracery["_nationality"] = nat_db["Nationality(Adjective)"].values
    del nat_db

    f = open("quotes.json", "r")
    quotes = json.load(f)
    f.close()

    tracery["_quotes"] = []
    for _ in range(5):
        tracery["_sentence"].append("#_quotes#")

    end = "."
    romance_syn = Word("romance").synonyms()
    for i, q in enumerate(quotes):
        # Remove [...]
        q["Quote"] = re.sub("\[.*\]", "", q["Quote"])
        q["Quote"] = re.sub("  ", " ", q["Quote"])

        # Pattern 1 -> incipit: ____ and ____
        if re.search(".*: .* and .*", q["Quote"]) and not re.search(".*:.*\..* and .*", q["Quote"]) and not re.search(".*:.* and see .*", q["Quote"]):
            incipit = q["Quote"].split(":")[0]
            if len(incipit) > 0:
                if "." in incipit:
                    incipit = incipit.split(".")[-1]
                    incipit = re.sub("^\s", "", incipit)

            if (not re.search("(f[ae]ll|fallen) in love|[Ff]our |[Ss]even |[Ff]ive |[Ss]ix |[Nn]ine |[Ee]ight ", incipit)) and (len(incipit) in range(1, 75) or "internet" in incipit):
                if " ask" in incipit:
                    end = "?"

                # if the incipit contains a NOC character than replace it with #noc_people#
                candidates = re.findall("[A-Z][a-z]*", incipit)
                found = False
                for cand in candidates:
                    index = veale_char.index[veale_char["Canonical Name"].str.contains(cand)]
                    if len(index) > 0:
                        for c in re.findall(cand+" [A-Za-z]+", incipit):
                            if c in veale_char.loc[index, "Character"].values:
                                incipit = incipit.replace(c, "#noc_people#")
                                found = True
                                break
                    if found:
                        break

                # if the incipit contains a Nationality than replace it with #natiolity#
                candidates = re.findall("[A-Z][a-z]*", incipit)
                for cand in candidates:
                    if cand in tracery["_nationality"]:
                        incipit = re.sub("an* " + cand, "#_nationaly.a#", incipit)
                        incipit = re.sub("An* " + cand, "#_nationaly.a.capitalize#", incipit)
                        break

                if len(re.findall('"', incipit)) == 1:
                    incipit = incipit.replace('"', "")
                if "Coaching 101" in incipit:
                    incipit = "#_creations#"

                for w in romance_syn:
                    # if contains a romance synonym than add a sex noun instead of one wildcard
                    if w in incipit:
                        if re.search("[Tt]hree ", incipit):
                            tracery["_quotes"].append(incipit + ": #_sex_noun#, " + wildcard + " and " + wildcard + end)
                        elif not re.search("[Oo]ne ", incipit):
                            tracery["_quotes"].append(incipit+": #_sex_noun# and "+wildcard + end)
                        break
                if re.search("[Tt]hree ", incipit):
                    tracery["_quotes"].append(incipit + ": " + wildcard + ", " + wildcard + " and " + wildcard + end)
                elif re.search("[Oo]ne ", incipit):
                    tracery["_quotes"].append(incipit + ": " + wildcard + end)
                else:
                    tracery["_quotes"].append(incipit + ": " + wildcard + " and " + wildcard + end)
                end = "."

        # Pattern 2 -> incipit like a ____
        spl = q["Quote"].split(".")
        spl = spl[0] if len(spl) > 2 else spl[-1]
        if re.search("^ ", spl):
            spl = spl[1:]

        if re.search(".* like a[n]? ", spl):
            spl = spl.replace("\"", "")
            end = spl[-1] if re.search("[\.\?]", spl[-1]) and not re.search("([Dd]o (you|we|they|I)\s*\?)$", spl) else "."
            spl = re.split(" like a[n]? ", spl)
            tracery["_quotes"].append(spl[0] + " like " + wildcard + end)
    del quotes

    creation = pd.read_csv("VealeCreations.csv")
    creation = creation.fillna('')
    search = ["Espionage", "Computers", "Research Field", "Framework"]
    tracery["_creations"] = []
    for s in search:
        tracery["_creations"] += creation.loc[creation['Creation Type'].str.contains(s) |
                                              creation['Creation Type.1'].str.contains(s) |
                                              creation['Creation Type.2'].str.contains(s) |
                                              creation['Creation Type.3'].str.contains(s), "Creation"].values.tolist()
    del creation

    place = pd.read_excel("LocationListing.xlsx")
    tracery["_place"] = place.loc[place['Type'].str.contains("Building") |
                                 place['Type'].str.contains("Room") |
                                 place['Type'].str.contains("Event"), "Location"].values.tolist()
    del place

    books = pd.read_excel("BookQualities.xlsx")
    tracery["_sentence"].append('\\"#_title#\\", is the book of the #_dd#!')
    tracery["_sentence"].append('\\"#_title#\\", soon in the best #_place#.')

    tracery["_title"] = [wildcard + "for " + wildcard + ': a story of hope']
    for title in books["Book"]:
        spl = re.split(" [aA]nd ", title)
        if len(spl) == 2 and "" not in spl:
            tracery["_title"].append(wildcard + " and " + spl[1])
            tracery["_title"].append(spl[0] + " and " + wildcard)

        spl = re.split(" [oO]f ", title)
        if len(spl) == 2 and "" not in spl:
            tracery["_title"].append(spl[0] + " of " + wildcard)

        spl = re.split(" [oO]f the ", title)
        if "" not in spl:
            if len(spl) == 2:
                tracery["_title"].append(spl[0] + " of " + wildcard)
            elif len(spl) > 2:
                sent = ""
                for chunk in spl[:-1]:
                    sent += chunk
                tracery["_title"].append(sent + wildcard)

        spl = re.split(" ", title)
        if (len(spl) == 2 or len(spl) == 3) and "" not in spl:
            sent = ""
            for chunk in spl[:-1]:
                sent += chunk + " "
            tracery["_title"].append(sent + wildcard)
    del books

    # Add sentence
    http_codes = pd.read_csv("http-code.csv")
    tracery["_http_codes"] = [str(r["Code"]) + " - " + wildcard + " " + r["Meaning"] for _, r in http_codes.iterrows()]
    del http_codes
    tracery["_sentence"].append("#_http_codes#")

    print("Saving BlackCard Tracery, ", time.time() - start_b)

    print_tracery(tracery, "black_card_tracery", ["_sentence", "origin"])


def white_main():
    start_w = time.time()
    tracery = {
        "origin": ["#_white_card_n# -*- #_white_card_n# -*- #_white_card_g# -*- #_white_card_g#"],
        "_hashtag": ["\#rockybalboa"],
        "_noun": ["#_hc#"],
        "_hc": ["The planet invasion", "A micropenis", "A micro vagina"],
        "_gerund_phrase": [],
        "_white_card_n": ["#_hashtag#", "#_noun#"],
        "_white_card_g": ["#_gerund_phrase#"],
        "_someone": ["#_noc_people#", "#_BeautifulActors#", "#_BeautifulActresses#", "#_pet.a#", "#_whose# #_pet#", "#_whose# #_family#", "#_star_wars#"],
        "_whose": ["your", "your bff\'s", "#_noc_people#\'s", "#_BeautifulActors#\'s", "#_BeautifulActresses#\'s"]

    }

    # Add creations to _noun
    creation = pd.read_csv("VealeCreations.csv")
    creation = creation.fillna('')
    search = ["Espionage", "Computers", "Research Field", "Framework"]
    tracery["_creations"] = []
    for s in search:
        tracery["_creations"] += creation.loc[creation['Creation Type'].str.contains(s) |
                                             creation['Creation Type.1'].str.contains(s) |
                                             creation['Creation Type.2'].str.contains(s) |
                                             creation['Creation Type.3'].str.contains(s), "Creation"].values.tolist()
    del creation
    tracery["_noun"].append("#_creations#")

    # Load NocList dataset
    veale_char = pd.read_excel("NOCList.xlsx")
    veale_char = veale_char.fillna('')

    # Add "marrying noc_people" to _gerund_phrase
    tracery["_noc_people"] = [c.replace('"', '\\"') for c in veale_char["Character"].values]
    tracery["_noun"].append("#_noc_people#")
    tracery["_gerund_phrase"].append("marrying #_someone#")

    # Add Star Wars characters to tracery
    tracery["_star_wars"] = []
    sw = pd.read_csv("StarWarsActors.csv")
    for d in sw["Description"]:
        d = re.sub(" \(.*\)", "", d)
        d = re.split("/", d)
        tracery["_star_wars"] += d
    tracery["_noun"].append("#_star_wars#")

    # Fill the _gerund_phrase with typical activity into NOCList
    for actions in veale_char[veale_char["Typical Activity"] != ""]["Typical Activity"]:
        # Parse the activity
        actions = actions.replace("  ", " ").replace('\"', '\\"')
        if actions[0] == " ":
            actions = actions[1:]
        acts = actions.split(", ")

        # Store the actions
        for act in acts:
            verb = act.split(" ")[0]
            if verb != "":
                if "_" + verb not in tracery.keys():
                    tracery["_gerund_phrase"].append(verb + " #_" + verb + "#")
                    tracery["_" + verb] = []
                a = act.replace(verb + " ", "", 1)
                if a not in tracery["_"+verb] or (a in tracery["_"+verb] and random.random() >= 0.85):
                    tracery["_" + verb].append(a)

    # Fill the _gerund_phrase with the actions related to the vehicles e.g. driving an AudiR8
    tracery["_gerund_phrase"] += ["piloting the " + x.name for x in swapi.get_all("starships").iter() if len(x.name.split(" ")) == 2]
    veale_vehicles = pd.read_excel("vehicleFleet.xlsx")
    for vehicles in veale_char[veale_char["Vehicle of Choice"] != ""]["Vehicle of Choice"]:
        # Parse the vehicles
        vehicles = vehicles.replace("  ", " ").replace('\"', '\\"')
        if vehicles[0] == " ":
            vehicles = vehicles[1:]
        vehs = vehicles.split(", ")

        # Store the phrase
        for v in vehs:
            affordances = veale_vehicles.loc[veale_vehicles["Vehicle"].str.contains(v)]["Affordances"].values
            if len(affordances) > 0:
                aff = affordances[0].split(", ")
                for a in aff:
                    if "_" + a not in tracery.keys():
                        tracery["_" + a] = []
                        tracery["_gerund_phrase"].append(a + " #_" + a + "#")

                    tracery["_" + a].append(v)
    del veale_vehicles
    del veale_char

    # Add name of most beautiful actresses to the tracery
    beautiful = pd.read_csv("MostBeautifulActresses-imdb.csv")
    tracery["_BeautifulActresses"] = beautiful["Name"].values
    del beautiful

    # Add name of most beautiful actors to the tracery
    beautiful = pd.read_csv("SexiestMaleActors.csv")
    tracery["_BeautifulActors"] = beautiful["Name"].values
    del beautiful

    tracery["_noun"].append("#_BeautifulActors#")
    tracery["_noun"].append("#_BeautifulActresses#")
    tracery["_gerund_phrase"].append("sexting with #_someone#")

    # Add Location to the tracery
    location = pd.read_excel("LocationListing.xlsx")
    in_loc = location.loc[location["Preposition"].str.contains("in")]
    tracery["_in_place"] = []
    for det, prep in zip(in_loc["Determiner"].values, in_loc["Location"].values):
        tracery["_in_place"].append(det+" "+prep)

    on_loc = location.loc[location["Preposition"].str.contains("on")]
    tracery["_on_place"] = []
    for det, prep in zip(on_loc["Determiner"].values, on_loc["Location"].values):
        tracery["_on_place"].append(det + " " + prep)
    del location

    # Add family members to the tracery
    family = pd.read_csv("family.csv")
    tracery["_family"] = family["Name"].values.tolist()
    del family

    # Add pets to the tracery
    petsdf = pd.read_excel("DomesticAnimals.xlsx")
    tracery["_pet"] = []
    for x in petsdf["Species and subspecies"].values:
        spl = re.split(" \(", x)[0]
        if " and " not in spl:
            tracery["_pet"].append(spl)
        else:
            tracery["_pet"] += re.split(" and ", spl)
    del petsdf

    # Add phrases related to sex into _noun using locations, pets, family and people previously added
    with open("sex_noun_phrase.txt", "r") as f:
        for row in f.readlines():
            row = re.sub("\([0-9a-zA-Z]*\)", "", re.sub("[0-9][0-9]*\. ", "", row)).split(" - ")[0]
            row = re.sub("[\.!]", "", row)
            if len(row) < 50:
                if re.search("in a[n]? ", row):
                    spl = re.split("in a[n]? ", row)
                    if spl[0] in tracery["_noun"]:
                        if random.random() >= 0.85:
                            tracery["_noun"].append(spl[0] + " in #_in_place#")
                        if spl[1] not in tracery["_in_place"]:
                            tracery["_in_place"].append(spl[1])

                    spl = re.split("on a[n]? |on the ", row)
                    if spl[0] in tracery["_noun"]:
                        if random.random() >= 0.85:
                            tracery["_noun"].append(spl[0] + " on #_on_place#")
                        if spl[1] not in tracery["_on_place"]:
                            tracery["_on_place"].append(spl[1])

                    spl = re.split("on your ", row)
                    if spl[0] in tracery["_noun"]:
                        if random.random() >= 0.85:
                            tracery["_noun"].append(spl[0] + " on #_someone#")
                        if spl[1] not in tracery["_someone"]:
                            tracery["_someone"].append(spl[1])
        f.close()

    # Add sexual activities to _noun
    sex_act = pd.read_csv("sex-activities.csv")
    tracery["_noun"] = sex_act[sex_act["grammar"] == "noun"]["word"].tolist()
    with open("sexual_acts.txt", "r") as f:
        for line in f.readlines():
            tracery["_noun"].append(line.replace(" \n", "").replace("\n", ""))
        f.close()

    # Add sexual disorder to _noun
    with open("sexualDisorder.txt", "r") as sd:
        tracery["_noun"] += [re.sub("\n", "", x) for x in sd.readlines()]
        sd.close()

    # Add drugs to _gerund_phrase
    tracery["_gerund_phrase"].append("#_drugs#")
    tracery["_drugs"] = []
    drugs = pd.read_excel("drugs.xlsx")
    for _, row in drugs.iterrows():
        for how in row["How Administered"].split(","):
            conj = verb_conjugate(verb_infinitive(how.replace(" ", "")), tense="present participle")
            tracery["_drugs"].append(conj + row["Name"])
    del drugs

    # Add games to _gerund_phrase
    games = pd.read_csv("best_games.csv")
    tracery["_gerund_phrase"].append("playing #_games#")
    tracery["_games"] = games["Game"].values
    del games

    print("Saving WhiteCard tracery, ", time.time() - start_w)

    print_tracery(tracery, "white_card_tracery", ["_white_card_n", "_white_card_g", "origin"])


if __name__ == "__main__":
    black = Process(target=black_main())
    white = Process(target=white_main())

    black.start()
    white.start()
    black.join()
    white.join()

