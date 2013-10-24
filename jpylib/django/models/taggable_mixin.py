"""
Contains the tagged model mixin
"""
from taggit.managers import TaggableManager


class TaggableMixin(object):
    """
    Mixin that adds tagging functionality to another model
    """

    tags = TaggableManager(blank=True)

    def print_tags(self):
        """
        Get a comma-delimited string of the tags on this object

        :returns: comma-delimited string of the tags, or an empty strign
        """
        tags = [tag.name for tag in self.tags.all().order_by('name')]
        return ", ".join(tags) if tags else ""

