# coding:utf8
from models import *
import hashlib

def get_hash(data):
    hasher = hashlib.sha256()
    hasher.update(data)
    return hasher.hexdigest()

def get_pending():
    q = ZhihuTopic.query
    q.equal_to('state', 'pending')
    q.limit(10)
    result = []
    for i in q.find():
        result.append({"url": i.get("url"),})
        i.set("state","working")
        i.save()
    return result

def add_pending(task_list):
    results = []
    for task in task_list:
        sid = task["topic_id"]
        topic = ZhihuTopic()
        # topic.set("url", task["url"])
        topic.set("state", "pending")
        topic.set("topic_id",str(sid))
        # topic.set("topic_id", get_hash(str(sid)))
        topic.save()
        results.append(topic)

    return results

def complete_task(data):
    '''
        {
            topic_id:{'name':'XX',children:[child_id,...]},
            ...
        }
    '''
    q = ZhihuTopic.query
    q.equal_to("state","working")
    q.containedIn('topic_id', data.keys())
    q.limit(1000)

    for task in q.find():
        topic = data[task.get("topic_id")]

        task.set("name",topic["name"])
        task.set("state","complete")

        q1 = ZhihuTopic.query
        q1.containedIn('topic_id', topic["children"])
        q1.limit(1000)
        children = q1.find()
        result_map = map(lambda x:{x.get("topic_id"):x},children)

        rel = task.relation("children")
        pending_list = []
        for i in topic["children"]:
            if result_map.get(i,False):
                rel.add(result_map[i])
            else:
                pending_list.append({"topic_id":i})

        add_pending(pending_list)
        task.save()


    return len(data)




