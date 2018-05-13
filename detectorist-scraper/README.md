# vBulletin Detectorist Scraper
This is an example of how to scrape every post of a vBulletin forum (specifically, http://metaldetectingforum.com, but as long as the XPath targets are the same it should work).

Pagination is handled for pages of different threads, and for pages of individual posts.

Post, thread, and username information is collected in items and saved in a MongoDB database via a pipeline.

It should take about 90 hours to scrape the 2.4M posts using AutoThrottle, or less if you're more aggressive (though you might get banned, depending on the forum).

Requires scrapy, pymongo, and a MongoDB server. Python 3 probably not supported; tested on Python 2.7.

***

## TODO:
* Investigate the handful of `ERROR: Spider error processing ...` pages

## vBulletin Forum Taxonomy
vBulletin forums are arranged like so:

* Index (aka Board): `example.com`, `example.com/index.php`
  * Forum: `example.com/forumdisplay.php?f=111`
    * Thread: `example.com/showthread.php?t=222222`  
      * Post: most sanely viewed on the thread page...

You can also view posts individually by their post id, eg `example.com/showpost.php?p=1000000` -- but the next post id `?p=1000001` might not be from the same thread!

Every post also has a number, which is its order in the thread. This is what I call `post_no`.

***

### Get a list of forums on the index page with

    './/td[contains(@id,"f")]/div/a'

You *could* exclude `<a>`'s with smallfont ancestors b/c they're subforms:

    './/td[contains(@id,"f")]/div/a[not(ancestor::div[@class="smallfont"])]'

But you might as well crawl all the forms from the main page.

### Get a list of threads on a forum with

    './/a[contains(@id,"thread_title")]'

(then //text() or /@href + urljoin the results)
