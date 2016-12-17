import six
# noinspection PyUnresolvedReferences
from six.moves.urllib.parse import urlencode

import re
import requests

from django.shortcuts import render_to_response, redirect
from django.template.loader import render_to_string
from django.core.urlresolvers import reverse
from django.conf import settings

from rest_framework import status

from core.views import CommunityView
from wiki_feed.models import WikiFeedCommunity


TARGET_WIKI = "https://en.wikipedia.org/"


def edit_wiki(page, content):
    wiki_session = requests.Session()
    api_endpoint = TARGET_WIKI + "w/api.php"
    initial_login_payload = {
        'action': 'query',
        'format': 'json',
        'utf8': '',
        'meta': 'tokens',
        'type': 'login'
    }
    response = wiki_session.post(api_endpoint, data=initial_login_payload)
    login_token = response.json()['query']['tokens']['logintoken']
    confirm_login_payload = {
        'action': 'login',
        'format': 'json',
        'utf8': '',
        'lgname': settings.WIKI_USER,
        'lgpassword': settings.WIKI_PASSWORD,
        'lgtoken': login_token
    }
    wiki_session.post(api_endpoint, data=confirm_login_payload)
    edit_token_params = {
        'action': 'query',
        'format': 'json',
        'meta': 'tokens',
    }
    response = wiki_session.get(api_endpoint, params=edit_token_params)
    edit_token = response.json()['query']['tokens']['csrftoken']
    edit_payload = {
        'action': 'edit',
        'assert': 'user',
        'format': 'json',
        'utf8': '',
        'text': content,
        'title': page,
        'nocreate': 1,
        'token': edit_token
    }
    return wiki_session.post(api_endpoint, edit_payload)


def get_existing_sections(page):
    page_url = "{}wiki/{}".format(TARGET_WIKI, page)

    page_response = requests.get(page_url, params={"action": "raw"})
    anchor_regex = re.compile("\{\{\s*anchor\s*\|([^}]+)")
    current_anchor = None
    sections = {
        "header": []
    }
    for line in page_response.text.splitlines():
        match = anchor_regex.search(line)
        if match:
            pre_anchor = line[:match.start()]
            if pre_anchor and current_anchor:
                sections[current_anchor].append(pre_anchor)
            current_anchor = match.groups()[0].strip()
            sections[current_anchor] = [line[match.start():]]
        elif match is None and current_anchor:
            sections[current_anchor].append(line)
        else:
            continue
    return sections


def wiki_page_update(request, page):
    response = CommunityView().get_response(WikiFeedCommunity, "latest-news", request.GET.dict())
    if response.status_code == status.HTTP_202_ACCEPTED:
        wait_url = reverse("v1:wiki_page_wait", kwargs={"page": page})
        wait_query = request.META.get("QUERY_STRING")
        return redirect("{}?{}".format(wait_url, wait_query))
    existing_sections = get_existing_sections(page)
    content = render_to_string("wiki_feed/header.wml", {"absolute_uri": request.build_absolute_uri()})
    for page_details in response.data["results"]:
        page_key = str(page_details["pageid"])
        if page_key in existing_sections:
            content += "\n".join(existing_sections[page_key])
        else:
            rank_info = page_details["ds_rank"]
            modules = (info for info in six.iteritems(rank_info) if info[0] != 'rank')
            sorted_modules = sorted(modules, key=lambda item: float(item[1]['rank']), reverse=True)
            content += render_to_string("wiki_feed/section.wml", {
                "page": page_details,
                "modules": sorted_modules
            })
    edit_wiki(page, content)
    return redirect("{}wiki/{}".format(TARGET_WIKI, page))


def wiki_page_wait(request, page):
    return render_to_response("wiki_feed/wait.html", {
        "segments_to_service": settings.SEGMENTS_TO_SERVICE,
        "service_query": "latest-news",
        "continue_path": reverse("v1:wiki_page_update", args=(page,)),
        "page_title": page
    })