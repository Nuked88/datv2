from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.selector import HtmlXPathSelector
from craigslist_sample.items import CraigslistSampleItem


class MySpider(CrawlSpider):
    name = "craigs"
    allowed_domains = ["http://www.gamesvillage.it"]
    start_urls = ["http://www.gamesvillage.it/forum/forum.php"]

    rules = (
        Rule(SgmlLinkExtractor(allow=(), restrict_xpaths=('//h2[@class="forumtitle"]',)), callback="parse_items", follow= True),
    )

    def parse_items(self, response):
        hxs = HtmlXPathSelector(response)
        titles = hxs.xpath('//a[@class="title"]')
        print titles+"ddddddddd"
        items = []
        for title in titles:
            item = CraigslistSampleItem()
            item["title"] = title.select('//a[@class="title"]/text()').extract()
            #item["link"] = title.xpath("//a@href").extract()
            items.append(item)
        return(items)
