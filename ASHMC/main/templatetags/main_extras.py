from django import template

import feedparser

import random
import re
import datetime

register = template.Library()


@register.filter
def is_today(value):
    assert isinstance(value, datetime.date)
    now = datetime.datetime.now()
    return (
        value.day == now.day and
        value.month == now.month and
        value.year == now.year
        )


class RssParserNode(template.Node):
    def __init__(self, var_name, url=None, url_var_name=None):
        self.url = url
        self.url_var_name = url_var_name
        self.var_name = var_name

    def render(self, context):
        if self.url:
            context[self.var_name] = feedparser.parse(self.url)
        else:
            try:
                context[self.var_name] = feedparser.parse(context[self.url_var_name])
            except KeyError:
                raise template.TemplateSyntaxError, "the variable \"%s\" can't be found in the context" % self.url_var_name
        return ''


@register.tag(name="get_rss")
def get_rss(parser, token):
    # This version uses a regular expression to parse tag contents.
    try:
        # Splitting by None == splitting by spaces.
        tag_name, arg = token.contents.split(None, 1)
    except ValueError:
        raise template.TemplateSyntaxError, "%r tag requires arguments" % token.contents.split()[0]

    m = re.search(r'(.*?) as (\w+)', arg)
    if not m:
        raise template.TemplateSyntaxError, "%r tag had invalid arguments" % tag_name
    url, var_name = m.groups()

    if url[0] == url[-1] and url[0] in ('"', "'"):
        return RssParserNode(var_name, url=url[1:-1])
    else:
        return RssParserNode(var_name, url_var_name=url)

"""
example usage:

{% load cache %}
{% load rss %}

{% cache 500 rss_display %}
    {% get_rss "http://www.freesound.org/blog/?feed=rss2" as rss %}
    {% for entry in rss.entries %}
        <h1>{{entry.title}}</h1>
        <p>
            {{entry.summary|safe}}
        </p>
        <p>
            <a href="{{entry.link}}">read more...</a>
        </p>
    {% endfor %}
{% endcache %}
"""


class RandomGreetingNode(template.Node):
    GREETING_CHOICES = (
        "Welcome, ",
        "Hi there, ",
        "Hello, ",
        "Greetings, ",
        "Salutations, ",
        "Salve, ",
    )

    def render(self, context):
        return random.choice(self.GREETING_CHOICES)


@register.tag(name='greeting')
def greeting(parser, token):
    tag_name = token.contents.split(None, 1)
    if isinstance(tag_name, tuple):
        raise template.TemplateSyntaxError, "%r tag takes no arguments" % token.contents.split()[0]

    return RandomGreetingNode()
