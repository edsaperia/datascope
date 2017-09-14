from collections import OrderedDict

from core.models.organisms import Community, Individual


class RedditScrapeCommunity(Community):

    COMMUNITY_SPIRIT = OrderedDict([
        ("subjects", {
            "process": "HttpResourceProcessor.fetch",
            "input": None,
            "contribute": "Append:ExtractProcessor.extract_from_resource",
            "output": "Collective#id",
            "config": {
                "_args": ["$.subreddit"],
                "_kwargs": {},
                "_resource": "RedditList",
                "_objective": {
                    "@": "soup.find_all(id=lambda el_id: el_id and el_id.startswith('thing_'))",
                    "id": "el.get('id').split('_')[-1]",
                    "details_link": "el.get('data-permalink')",
                    "comments_count": "el.get('data-comments-count')",
                    "score": "el.get('data-score')",
                    "author": "el.get('data-author')",

                },
                "_continuation_limit": 1000,
                "_interval_duration": 2000
            },
            "schema": {},
            "errors": {},
        }),
        ("images", {
            "process": "HttpResourceProcessor.fetch_mass",
            "input": "@subjects",
            "contribute": "Update:ExtractProcessor.extract_from_resource",
            "output": "@subjects",
            "config": {
                "_args": ["$.details_link"],
                "_kwargs": {},
                "_resource": "RedditPermalink",
                "_objective": {
                    "@": "soup.find_all(id=lambda el_id: el_id and el_id.startswith('media-preview-'))",
                    "id": "el.get('id').split('-')[-1]",
                    "media_preview": "el.find('img').get('src') if el.find('img') else None",
                },
                "_interval_duration": 2000,
                "_update_key": "id"
            },
            "schema": {},
            "errors": {},
        }),
        ("comments", {
            "process": "HttpResourceProcessor.fetch_mass",
            "input": "@subjects",
            "contribute": "Append:ExtractProcessor.extract_from_resource",
            "output": "Collective#id",
            "config": {
                "_args": ["$.details_link"],
                "_kwargs": {},
                "_resource": "RedditPermalink",
                "_objective": {
                    "@": "soup.find_all(id=lambda el_id: el_id and el_id.startswith('thing_'))[1:]",
                    "id": "el.get('id').split('_')[-1]",
                    "parent_id": "next(el.parents)['id'].split('_')[-1] if next(el.parents) else None",
                    "author": "el.get('data-author')",
                    "author_score": "el.select('.score.unvoted')[0].text if el.select('.score.unvoted') else 0",
                    "comment": "[paragraph.text for paragraph in el.select('.usertext-body p')]"
                }
            },
            "schema": {},
            "errors": {},
        }),
        ("download", {
            "process": "HttpResourceProcessor.fetch_mass",
            "input": "@images",
            "contribute": None,
            "output": None,
            "config": {
                "_args": ["$.url"],
                "_kwargs": {},
                "_resource": "ImageDownload"
            },
            "schema": {},
            "errors": None,
        })
    ])

    COMMUNITY_BODY = []

    def initial_input(self, *args):
        return Individual.objects.create(
            community=self,
            collective=None,
            properties={
                "subreddit": args[0]
            },
            schema={}
        )

    def set_kernel(self):
        self.kernel = self.current_growth.output

    class Meta:
        verbose_name = "Reddit scrape community"
        verbose_name_plural = "Reddit scrape communities"
