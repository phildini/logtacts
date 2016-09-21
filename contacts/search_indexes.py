from haystack import indexes
from contacts.models import Contact


class ContactIndex(indexes.SearchIndex, indexes.Indexable):

    text = indexes.NgramField(document=True, use_template=True)
    name = indexes.NgramField(model_attr='name', boost=1.2)
    book = indexes.IntegerField(model_attr="book_id")
    tags = indexes.MultiValueField()
    tags_ids = indexes.MultiValueField()

    def get_model(self):
        return Contact

    def index_queryset(self, using=None):
        return self.get_model().objects.all()

    def get_updated_field(self):
        return 'changed'

    def prepare_tags(self, obj):
        return [tag.tag for tag in obj.tags.all()]

    def prepare_tags_ids(self, obj):
        return [tag.id for tag in obj.tags.all()]
