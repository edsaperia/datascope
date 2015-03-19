import requests
from dateutil.parser import parse as time_parse
import json


RESULTS = []


def log_error(message, celeb_qualifier):
    try:
        print u"Error for: ".format(message)
    except UnicodeEncodeError:
        print u"UTF8 Error for: {}".format(celeb_qualifier)


def doit(entities):

    for i, celeb_entity in enumerate(entities):

        # Occasional logging to start off at offset when script fails
        if not i % 100:
            print i

        # Get Wikidata details based on qualifier
        celeb_qualifier = "Q{}".format(celeb_entity)
        rsp = requests.get("https://www.wikidata.org/wiki/Special:EntityData/{}.json".format(celeb_qualifier))
        celeb_data = rsp.json()

        # Extract name and birth date
        try:
            name = celeb_data["entities"][celeb_qualifier]["labels"]["nl"]["value"]
        except KeyError:
            log_error(celeb_qualifier, celeb_qualifier)
            continue
        try:
            birth_day_time = celeb_data["entities"][celeb_qualifier]["claims"]["P569"][0]["mainsnak"]["datavalue"]["value"]["time"]
        except (ValueError, KeyError):
            log_error(name, celeb_qualifier)
            continue
        try:
            birth_day = time_parse(birth_day_time[1:]).strftime("%d-%m-%Y")
        except:
            print "Date",
            log_error(name, celeb_qualifier)
            continue

        # Save in global list
        RESULTS.append({
            "name": name,
            "birth_date": birth_day
        })


# Call Wiki Data Query to get qualifiers which are:
# 1) Dutch citizens
# 2) have a known birth date
# 3) no known decease date
#response = requests.get("http://wdq.wmflabs.org/api?q=CLAIM[27:55] AND CLAIM[569] AND NOCLAIM[570]")
#dutch_celebs_with_birth_date = response.json()["items"]
# Save for later :)
fp = open('celeb_qualifiers.json', 'rw')
dutch_celebs_with_birth_date = json.load(fp)
#json.dump(dutch_celebs_with_birth_date, fp)

fp.close()


offset = 700


try:
    doit(dutch_celebs_with_birth_date[offset:])
except Exception as e:
    print str(e)
print json.dumps(RESULTS)