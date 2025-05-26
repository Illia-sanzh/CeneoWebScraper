import json
import requests
from bs4 import BeautifulSoup
from config import headers
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
import os
class Product:
    def __init__(self, product_id, product_name='', stats={}, opinions=[]):
        self.product_id = product_id
        self.product_name = product_name
        self.opinions = opinions
        self.stats = stats

    def __str__(self):
        return f"product id: {self.product_id}\nproduct name:{self.product_name}\nstats:" + json.dumps(self.stats, indent=4, ensure_ascii=False) + "\nopinions" + "\n\n".join(str(opinion) for opinion in self.opinions)

    def __repr__(self):
        return f"Product(product id={self.product_id}, product name={self.product_name}, opinions=["+", ".join([repr(opinion) for opinion in self.opinions]) +f"], stats={self.stats})"
    def hex_to_RGB(self, hex_str):
        """ #FFFFFF -> [255,255,255]"""
        #Pass 16 to the integer function for change of base
        return [int(hex_str[i:i+2], 16) for i in range(1,6,2)]
    def get_color_gradient(self, c1, c2, n):
        """
        Given two hex colors, returns a color gradient
        with n colors.
        """
        assert n > 1
        c1_rgb = np.array(self.hex_to_RGB(c1))/255
        c2_rgb = np.array(self.hex_to_RGB(c2))/255
        mix_pcts = [x/(n-1) for x in range(n)]
        rgb_colors = [((1-mix)*c1_rgb + (mix*c2_rgb)) for mix in mix_pcts]
        return ["#" + "".join([format(int(round(val*255)), "02x") for val in item]) for item in rgb_colors]
    def get_link(self):
        return f"https://www.ceneo.pl/{self.product_id}#tab-reviews"

    def extract_name(self):
        response = requests.get(self.get_link(), headers=headers)
        page_dom = BeautifulSoup(response.text, 'html.parser')
        self.product_name = page_dom.select_one('h1')
    def opinions_to_dict(self):
        return [opinion.to_dict() for opinion in self.opinions]
    def calculate_stats(self):
        opinions = pd.DataFrame.from_dict(self.opinions_to_dict())
        self.stats['opinions_count'] = opinions.shape[0]
        self.stats["pros_count"] = opinions.pros_pl.astype(bool).sum()
        self.stats["cons_count"] = opinions.cons_pl.astype(bool).sum()
        self.stats["pros_cons_count"] = opinions.apply(lambda o: bool(o.pros_pl) and bool(o.cons_pl), axis=1).sum()
        self.stats["average_score"] = opinions.stars.mean()
        self.stats["pros"] = opinions.pros_en.explode().value_counts()
        self.stats["cons"] = opinions.cons_en.explode().value_counts()
        self.stats['recommendation']  = opinions.recommend.value_counts(dropna=False).reindex([True, False, np.nan], fill_value=0)
        self.stats['stars'] = opinions.stars.value_counts().reindex(list(np.arange(0.5,5.5,0.5)), fill_value=0)

    def generate_charts(self):
        if not os.path.exists('.app/static/piecharts'):
            os.mkdir('.app/static/piecharts')
        if not os.path.exists('.app/static/barcharts'):
            os.mkdir('.app/static/barcharts')
        self.stats['recommendations'].plot.pie(
        autopct = lambda r: f"{r:.1f}%" if r>0 else '' ,
            label='',
            colors  = ['forestgreen', 'red', 'blue'],
            labels=['Recommend', 'Not recommend', 'No opinion']
        )
        plt.title(f"Recommendations for product id: {self.product_id}\nNumber of opinions: {self.stats['opinions_count']}")
        plt.savefig(f".app/static/piecharts/{self.product_id}.png")
        plt.close()

        color1='#FF0000'
        color2='#0000FF'
        plt.figure(figsize=(7,6))
        ax = self.stats['stars'].plot.bar(color = self.get_color_gradient(color1,color2,15))
        plt.bar_label(container=ax.containers[0])
        plt.xlabel("Number of stars")
        plt.ylabel("Number of opinions")
        plt.title(f"Number of opinions about product:{self.product_id}\n with particular")
        plt.xticks(rotation=0)
        plt.savefig(f".app/static/barcharts/{self.product_id}.png")
        plt.close()
class Opinion:
    selectors = {
        'opinion_id': (None, 'data-entry-id',),
        'author': ('span.user-post__author-name',),
        'recommend' :('span.user-post__author-recomendation > em.recommended',),
        'stars' :('span.user-post__score-count',),
        'content_pl' :('div.user-post__text',),
        'pros_pl' :('div.review-feature__item--positive', None, True),
        'cons_pl' :('div.review-feature__item--negative', None, True),
        'helpful' :('button.vote-yes', "data-total-vote"),
        'unhelpful' :('button.vote-no', "data-total-vote"),
        'published' :("span.user-post__published > time:nth-child(1)", 'datetime'),
        'purchased' :("span.user-post__published > time:nth-child(2)", 'datetime')
    }
    def __init__(self, opinion_id, author, recommend, stars, content, pros, cons, helpful, unhelpful, published, purchased):
        self.opinion_id = opinion_id
        self.author = author
        self.recommend = recommend
        self.stars = stars
        self.content = content
        self.pros = pros 
        self.cons = cons
        self.helpful = helpful
        self.unhelpful = unhelpful
        self.published = published
        self.purchased = purchased

    def __str__(self):
        return '\n'.join([f'{key}: {getattr(self,key)}'for key in self.selectors.keys()])
    def __repr__(self):
        return "Opinion("+', '.join([f'{key}={getattr(self,key)}'for key in self.selectors.keys()])+")"
    
    def to_dict(self):
        return {{key}: getattr(self,key)for key in self.selectors.keys()}
        