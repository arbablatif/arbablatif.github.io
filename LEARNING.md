# Learning notes

Plain-language notes on how this site works and why it was built this way.

## What SEO means here

Search engine optimisation is making pages easy for a search engine to find, understand and show. It has three parts:

1. **Being found.** The sitemap lists every page, and `robots.txt` tells crawlers they are welcome and where the sitemap is.
2. **Being understood.** Each page has a clear title, a description and one main heading, and its text uses the words people actually search for, such as "predictive maintenance" or "text-to-SQL".
3. **Being trusted.** This comes mostly from outside the site: other pages linking to it, and how long it has existed. Good markup can't replace this, which is why no one can honestly promise a ranking.

## Why a website as well as GitHub

GitHub controls the title and metadata of its own pages. On your own site you control them for every page, so each project can target its own topic. The site and repos also link to each other, which helps search engines connect them.

## Key terms

- **Title tag:** the blue link text in search results. Kept to 60 characters so it isn't cut off.
- **Meta description:** the snippet below that link. Kept to 160 characters. Search engines may replace it with their own.
- **Canonical URL:** tells search engines the one official address for a page, so copies don't compete.
- **Open Graph tags:** control the title, text and image shown when a link is shared on LinkedIn and similar sites.
- **JSON-LD structured data:** a hidden, machine-readable summary, for example "this page is software written by this person, and the code is here". It helps search engines connect your name to your work.
- **Alt text:** a written description of an image for screen readers and search engines.

## Design decisions

- **Generated static pages.** There is no server or database, so hosting is free and very little can break. Python generates the pages once, before publishing.
- **No JavaScript or web fonts.** Pages load quickly, and crawlers see all the content without running code.
- **Content kept apart from layout.** `content.py` holds the words and `build.py` holds the structure. To change wording, you only touch one file.
- **Limitations on every page.** They are there for the same reason they are in the READMEs: a client who sees what a system cannot do will trust the results more.
- **Figures checked against READMEs.** A portfolio number that disagrees with its own repo damages credibility, so a test catches a headline value that doesn't appear there.

## What to do after publishing

1. Add the site to [Google Search Console](https://search.google.com/search-console) and submit `sitemap.xml`. This is the fastest way to get indexed.
2. Put the site address on your LinkedIn profile. A link from a trusted site helps it get found.
3. Update the site when you finish a project. Recent, specific content does better than a page that never changes.
