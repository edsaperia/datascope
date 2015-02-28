import warc


class BlackListException(Exception):
    pass


warc_data = warc.open("archiveteam_hyves_20131125032333.cdx.gz")
blacklist = [] # ['cache.hyves', 'hyves-static','metadata://']

counter = 0

for i, record in enumerate(warc_data):

    uri = record.header.get("warc-target-uri", "")

    try:
        for term in blacklist:
            if term in uri:
                raise BlackListException
    except BlackListException as e:
        continue

    if uri:
        counter += 1
        print uri

print counter