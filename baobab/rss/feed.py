from django.contrib.syndication.views import Feed
from django.utils.feedgenerator import Atom1Feed
from baobab.backoffice.models import Event, EventLog
from django.utils.timezone import now
import markdown


class RssStatusFeed(Feed):
    title = 'Gandi.net Status RSS Feed'
    link = '/rss/'
    description = 'Get information about Gandi platform status'

    def items(self):
        return Event.objects.order_by('-last_update')[:50]

    def item_title(self, item):
        title = item.title
        nb_logs = item.eventlogs.count()
        state = None
        if item.category == item.MAINTENANCE and item.date_start < now():
            if not item.date_end or item.date_end > now():
                state = 'STARTED'
        if nb_logs > 0:
            state = 'UPDATE %d' % nb_logs
        if item.date_end and item.date_end <= now():
            state = 'FINISHED'
        if state:
            title = '[%s] %s' % (state, title)
        return title

    def item_description(self, item):
        if item.services.exists():
            services = []
            for service in item.services.all():
                services.append(service.get_name_display())
            services = ', '.join(service for service in services)
        else:
            services = 'No service impacted'
        description = '**Type : %s**<br>' % item.get_category_display()
        description += '**Services : %s**<br>' % services
        description += '**Last update : %s**<br>' % str(
            item.last_update.strftime("%Y-%m-%d %X %z"))
        description += '**Date start : %s**<br>' % (item.date_start)
        if item.date_end:
            description += '**Date end : %s**<br>' % (item.date_end)
        elif item.estimate_date_end:
            description += '**Estimated date end : %s**<br>' % (
                item.estimate_date_end)
        if item.eventlogs.exists():
            for eventlog in item.eventlogs.all():
                description += '<p><em>Update on %s :</em><br>' % str(
                    eventlog.date)
                description += markdown.markdown(eventlog.comment)
                description += '<hr/></p>'
            description += markdown.markdown('#### Initial message')
        description += markdown.markdown(
            item.eventdatas.get(lang__iso='en').summary)
        return markdown.markdown(description)

    def item_pubdate(self, item):
        return item.last_update

    def item_link(self, item):
        event_id = item.id
        nb_logs = item.eventlogs.count()
        if nb_logs > 0:
            # Add a GET params unused on frontend side due to RSS client cache
            last_item = item.eventlogs.all()[0]
            # Ugly hack to update the link if the date_end only is updated
            if item.date_end:
                if last_item.date < item.date_end:
                    last_item.id += 1
            event_id = "%d?evnt_id=%d" % (event_id, last_item.id)
        elif item.date_end:
            event_id = "%d?evnt_id=1" % event_id
        return '/timeline/events/%s' % event_id


class AtomStatusFeed(RssStatusFeed):
    feed_type = Atom1Feed
    title = 'Gandi.net Status Atom Feed'
    link = '/atom/'
    subtitle = RssStatusFeed.description
