import sys

from neomodel import config, StructuredNode, StringProperty, RelationshipFrom, \
    RelationshipTo, BooleanProperty

config.DATABASE_URL = 'bolt://neo4j:123456@localhost:7687'


class Topic(StructuredNode):

    name = StringProperty(unique_index=True, required=True)
    topic_id = StringProperty(unique_index=True, required=True)
    done = BooleanProperty(index=True, required=True)

    parent_topics = RelationshipFrom('Topic', 'ParentTopic')
    child_topics  = RelationshipTo('Topic', 'ParentTopic')


def save(parent_topic, child_topics):
    print(parent_topic.name)
    for ct in child_topics:
        sys.stdout.write(ct.name + ' ')
    sys.stdout.write('\n')
    sys.stdout.flush()

    pT = Topic.nodes.get_or_none(topic_id=parent_topic.topic_id)
    if pT:
        parent_topic = pT

    parent_topic.done = True
    parent_topic.save()

    for child_topic in child_topics:
        pT = Topic.nodes.get_or_none(topic_id=child_topic.topic_id)
        if not pT:
            child_topic.save()
        else:
            child_topic = pT

        if not parent_topic.child_topics.is_connected(child_topic):
            parent_topic.child_topics.connect(child_topic)


def is_done(topic_id=None, name=None, done=None):
    if Topic.nodes.get_or_none(topic_id=topic_id,name=name,done=done):
        return True
    else:
        return False


def save_new_topic(topic):
    pT = Topic.nodes.get_or_none(topic_id=topic.topic_id)
    if not pT:
        topic.save()
