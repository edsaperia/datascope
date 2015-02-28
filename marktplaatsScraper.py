"""
@Author: A.J. de Mooij
@Email: A.J.deMooij@students.uu.nl
"""

import requests, unicodecsv, json, urllib
from bs4 import BeautifulSoup


# What is entered in the field if value couldn't be found
empty_message = "<empty>"

# THe csv writer (instantiated with openWriter() function)
writer = None

# Headers for the csv file (with ordering)
csv_headers = [
    'name',
    'slogan',
    'link',
    'telefoon',
    'provincie',
    'stad',
    'address',
    'location',
    'kvkNumber',
    'registrationType',
    'bedrijfsvorm',
    'mederwerkers',
    'op_marktplaats',
    'ervaring',
    'creationDate',
    'advert_type'
]


def getProfile(url, advert_type='advertentie'):
    """
    Try to read a url marktplaats profile.
    If a value cannot be found, write the empty message.
    @param 		url 	The url to the zzp'ers profile
    @param 		advert_type THe type of profile (advert or vakman-profile)
    @return 	Dictionary with the profile information
                of the zzp'er
    """
    r = requests.get(url)
    #Making it a beautiful soup object
    soup = BeautifulSoup(r.text)

    profile = {}

    # Try to get the slogan. If it doesn't exists, add as empty
    try:
        profile['slogan'] = soup.find('h2', id='slogan').text
    except:
        profile['slogan'] = empty_message

    # Try to get the link to ZZP'ers page
    try:
        profile['link'] = soup.find('a', id='vip-seller-url-link').text
    except:
        profile['link'] = empty_message

    # Get city and province
    try:
        locatie = soup.find('li', id='vip-seller-location').findChildren()[0].text
        try:
            profile['stad'], profile['provincie'] = locatie.split(', ')
        except:
            profile['stad'] = locatie
            profile['provincie'] = empty_message
    except:
        profile['stad'] = empty_message
        profile['provincie'] = empty_message

    # Append the JSON of the kvk to the profile dictionary
    headers = ['ervaring', 'op_marktplaats', 'mederwerkers', 'bedrijfsvorm']
    try:
        kvkNummer = (soup.find('div', id='kvk-data-block').find('div', {'class' : 'data-holder'}).text).replace('\n', '')
        response = urllib.urlopen('http://diensten-vakmensen.marktplaats.nl/kvk/info.json?kvk=%s' % kvkNummer)
        data = json.loads(response.read())
        profile.update(data['kvkInfo'])

        # Get the additional block information
        additionals = soup.find('div', id='vip-additional-data').findChildren('div', {'class' : 'additional-data-block'})[1:]

        # Get all the information from the blocks
        for h in range(len(headers)):
            profile[headers[h]] = additionals[h].findChildren()[0].text
    except:
        for n in headers + ['name', 'location', 'address', 'kvkNumber', 'creationDate', 'registrationType']:
            profile[n] = empty_message

    # Extract javascript hidden phone number (suckers)
    try:
        profile['telefoon'] = soup.find('li', id='vip-seller-phone').findChildren()[0].text
    except:
        profile['telefoon'] = empty_message

    profile['advert_type'] = advert_type

    return profile

def openWriter(name='marktplaatsscraper.csv'):
    '''
    Open the csv file where the marktplaats data will be written to
    @param 		Name 	The name of the csv file (including extension)
    '''
    #setting up our CSV file, making sure we have headers
    global writer
    writer = unicodecsv.writer(open(name, 'wb'), encoding='utf-8',delimiter=';', dialect='excel',quotechar='"')
    writer.writerow(csv_headers)

def writeRow(row):
    '''
    Writes the row to the openend file
    @param 	row 	The row to be written
    '''
    result = []
    for h in csv_headers:
        result.append(row[h])
    writer.writerow(result)

def extractVakmensen(page=1):
    '''
    Reads the search page of diensten-vakmensen.marktplaats.nl and scans for profiles of vakmensen.
    The link to that profile will than be passed to getProfile() and the result is written to the csv file
    Two types of profiles exist: vakmensen, with elaborate data and a normal marktplaats advertentie with
    less abundant information. To catch this, the type of profile is guessed from the link
    @arg 	page 	The page in the search to scan for profiles
    @return 		True iff the page still contains profiles. Otherwise, you have probably reached the last
                    page
    '''
    # THe search page lists them nicely. We can use the page number to search marktplaats iteratively
    url = "http://diensten-vakmensen.marktplaats.nl/zoeken.html?query=&categoryId=1098&distance=0&postcode=&searchOnTitleAndDescription=true&wrt=4s&sortOrder=decreasing&sortBy=relevance&currentPage=%d" % page
    r = requests.get(url)

    #Making it a beautiful soup object
    soup = BeautifulSoup(r.text)

    # Anchor element is the profile-title-description class
    profiles = soup.findAll('div', {'class' : 'profile-title-description'})

    print "%d items on page %d" %(len(profiles), page)

    if len(profiles == 0):
        return False

    # Extract the links for each of those profiles
    for p in profiles:
        a = p.find('h2').find('a')
        name = a.find('span').text
        link = a.get('href')
        advert_type = 'vakman'
        if not link.startswith('http://'):
            link = 'http://www.marktplaats.nl/' + link
            advert_type = 'advertentie'
        print name

        # Reads the profile and writes to csv
        writeRow(getProfile(link, advert_type))

    return True


if __name__ == '__main__':
    # open a new csv writer
    openWriter()

    # Scan 30 pages and write all the 30 * 35 profiles
    # to the csv file
    # print status after every page
    for n in range(30):
        print "\n\nStarted reading page %d \n" %n
        extractVakmensen(n+1)

    # Use this if you don't mind not using your computer
    # for a few days. COuld take a while
#	i = 1
#	while(true):
#		print "\n\nStarted reading page %d \n" %n
#		if not extractVakmensen(n):
#			"Page %d seems to be the last page" %i-1
#			break

    print "Done"