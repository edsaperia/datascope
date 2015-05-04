import io, re
import requests, warc

# Some compiled regexes to detect certain Hyves pages
INDEX_PATTERN = re.compile("https?:\/\/([^.]+)\.hyves\.nl/$")
PROFILE_PATTERN = re.compile("https?:\/\/([^.]+)\.hyves\.nl/profiel/$")

# A list of dictionaries that indicates which archives to get
# This list should become a complete list of Hyves archives
# We could either scrape the archive site or fill them in by hand
TARGETS = [
    {
        "archive": "https://archive.org/download/archiveteam_hyves_20131124104613/hyves_20131124104613.megawarc.warc.gz",
        "index": "hyves_20131124104613.megawarc.warc.os.cdx",
    }
]

# Some vars this program works with
target = TARGETS[0]
cache = {}
limit = 10


# A function to save results in a dictionary
def store_in_cache(match, data, typ):

    stored = cache.get(match)
    if stored is None:
        cache[match] = {
            typ: data
        }
    else:
        cache[match][typ] = data


with io.open(target["index"], 'r') as fb:

    # Read the index file
    for line in fb:

        data = line.split(' ')  # splits columns in index file
        uri = data[2]  # looks at third column

        index_match = INDEX_PATTERN.match(uri)
        if index_match is not None:
            store_in_cache(index_match.group(1), data, "index")
        profile_match = PROFILE_PATTERN.match(uri)
        if profile_match is not None:
            store_in_cache(profile_match.group(1), data, "profile")

    for i, stored in enumerate(cache.values()):

        if i >= limit:
            break

        if "index" in stored and "profile" in stored:

            print "Getting:", stored["profile"]

            # Prepare partial request for data from archive
            cached_data = stored["profile"]
            compressed_offset = cached_data[-2]
            compressed_file_size = cached_data[-3]
            headers = {
                "Range": "bytes={}-{}".format(compressed_offset, int(compressed_offset) + int(compressed_file_size) + 1)
            }

            # Get data and write to disk
            response = requests.get(target['archive'], headers=headers, verify=False)
            with open("tmp.warc.gz", "w+b") as tmp_gz:
                tmp_gz.write(response.content)

            # Read as WARC record
            wf = warc.open("tmp.warc.gz")
            record = wf.read_record()

            html = []
            body = False
            for line in record.payload.read().split('\n'):
                if body:
                    html.append(line)
                if not line.strip():
                    body = True

            html_file = open(
                "".join(x if x.isalnum() else '-' for x in cached_data[0]) + ".html",
                "w+"
            )
            html_file.writelines(html)
