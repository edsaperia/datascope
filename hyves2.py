import io, re
import requests, warc
import subprocess  # gzip -cd -


index_pattern = re.compile("https?:\/\/([^.]+)\.hyves\.nl/$")
profile_pattern = re.compile("https?:\/\/([^.]+)\.hyves\.nl/profiel/$")
cache = {}
url = "https://archive.org/download/archiveteam_hyves_20131124104613/"
targets = [
    {
        "index": "hyves_20131124104613.megawarc.warc.os.cdx",
        "archive": "hyves_20131124104613.megawarc.warc.gz"
    }
]
targetz = []
for target in targets:
    response = requests.head(url + target['archive'])
    target["url"] = response.headers.get('location')
    targetz.append(target)

target = targetz[0]


def store_in_cache(match, data, typ):

    stored = cache.get(match)
    if stored is None:
        cache[match] = {
            typ: data
        }
    else:
        cache[match][typ] = data


limit = 1


with io.open(target["index"], 'r') as fb:

    for line in fb:

        data = line.split(' ')
        uri = data[2]

        index_match = index_pattern.match(uri)
        if index_match is not None:
            store_in_cache(index_match.group(1), data, "index")
        profile_match = profile_pattern.match(uri)
        if profile_match is not None:
            store_in_cache(profile_match.group(1), data, "profile")

    for i, stored in enumerate(cache.values()):

        if i >= limit:
            break

        if "index" in stored and "profile" in stored:
            cached_data = stored["index"]
            compressed_offset = cached_data[-2]
            compressed_file_size = cached_data[-3]
            headers = {
                "Range": "bytes={}-{}".format(compressed_offset, int(compressed_offset) + int(compressed_file_size) + 1)
            }

            response = requests.get(target['url'], headers=headers, verify=False)
            import ipdb; ipdb.set_trace()
            fp = warc.WARCFile(fileobj=response.raw)

            record = fp.read_record()
            print record
