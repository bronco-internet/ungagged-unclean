# -*- coding: utf-8 -*-
from flask import Flask
from flask import render_template
from flask import request
from flask import flash

from link_check import url_split
from link_check import blocked_by_robots_txt
from link_check import get_dates_for
from link_check import check_head_nofollow
from link_check import check_head_noindex
from link_check import check_page_header
from link_check import check_google_index
from link_check import is_nofollow_on_link
from link_check import is_noindex_on_link
from link_check import check_canonical_matches
from link_check import canonicall

from bs4 import BeautifulSoup
import requests
import re
from reppy.cache import RobotsCache
import traceback
import urllib
import tldextract
from urlparse import urlparse
from collections import namedtuple

app = Flask(__name__)
app.secret_key = '<your-app-secret>'

@app.route('/', methods = ['GET', 'POST'])
def home():
    
    if request.method == 'GET':
        return render_template('index.html')

    if request.method == 'POST':

        # get form submissions
        link_to_check = request.form.get('page_url', None)
        domain_to_check = request.form.get('link_domain', None)

        try:
            # fetch url and build soup
            r  = requests.get(link_to_check.strip(), timeout=10)
            data = r.text
            soup = BeautifulSoup(data, 'html5lib')

            # check canonical tag
            canonical_tag = check_canonical_matches(soup, link_to_check)

            canonical = canonicall(soup, link_to_check)

            # check xrobots header
            xrobot = check_page_header(r)

            # check head noindex
            head_noindex = check_head_noindex(soup)

            # check head nofollow
            head_nofollow = check_head_nofollow(soup)

            # check google index
            google_index = check_google_index(link_to_check)

            # check robots.txt file
            robots_txt_block = blocked_by_robots_txt(link_to_check)

            # grab all links and check for domain 
            linking_status = False
            noindex_on_link = False
            nofollow_on_link = False
            linking_url = ''
            anchor_text = ''
            for link in soup.find_all('a', href=True):
                if domain_to_check in link['href']:
                    # update the linking status
                    linking_status = True

                    # grab the link anchor text
                    anchor_text = link.contents[0]

                    # grab the linking link
                    linking_url = link['href']

                    # check if noindex is on link
                    noindex_on_link = is_noindex_on_link(link)

                    # check if nofollow is on link
                    nofollow_on_link = is_nofollow_on_link(link)

                else:
                    pass

            # check google cache
            google = requests.get('https://webcache.googleusercontent.com/search?q=cache:{}'.format(link_to_check.strip()), timeout=5)
            if google.status_code == 200:
                is_in_google_cache = True
            else:
                is_in_google_cache = False
            google_data = google.text
            google_soup = BeautifulSoup(google_data, 'html5lib')

            # check canonical tag
            google_canonical_tag = check_canonical_matches(soup, link_to_check)

            google_canonical = canonicall(soup, link_to_check)

            # check head noindex
            google_head_noindex = check_head_noindex(soup)

            # check head nofollow
            google_head_nofollow = check_head_nofollow(soup)

            # grab all links and check for domain 
            google_linking_status = False
            google_noindex_on_link = False
            google_nofollow_on_link = False
            google_linking_url = ''
            google_anchor_text = ''
            for link in google_soup.find_all('a', href=True):
                if domain_to_check in link['href']:
                    # update the linking status
                    google_linking_status = True

                    # grab the link anchor text
                    google_anchor_text = link.contents[0]

                    # grab the linking link
                    google_linking_url = link['href']

                    # check if noindex is on link
                    google_noindex_on_link = is_noindex_on_link(link)

                    # check if nofollow is on link
                    google_nofollow_on_link = is_nofollow_on_link(link)

                else:
                    pass
            return render_template('return.html', 
                canonical_tag=canonical_tag, 
                xrobot=xrobot,
                head_nofollow=head_nofollow,
                head_noindex=head_noindex,
                google_index=google_index,
                robots_txt_block=robots_txt_block,
                linking_status=linking_status,
                nofollow_on_link=nofollow_on_link,
                noindex_on_link=noindex_on_link,
                link_to_check=link_to_check,
                canonical=canonical,
                anchor_text=anchor_text,
                linking_url=linking_url,
                google_head_noindex=google_head_noindex,
                google_head_nofollow=google_head_nofollow,
                google_canonical=google_canonical,
                google_canonical_tag=google_canonical_tag,
                google_nofollow_on_link=google_nofollow_on_link,
                google_noindex_on_link=google_noindex_on_link,
                google_linking_url=google_linking_url,
                google_anchor_text=google_anchor_text,
                google_linking_status=google_linking_status,
                is_in_google_cache=is_in_google_cache
                )

        except Exception as e:
            flash(e)
            flash("Sorry, there was an error. That's all we know.")
            return render_template('index.html')




if __name__ == '__main__':
    app.run(debug=True)