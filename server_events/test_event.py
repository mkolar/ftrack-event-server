# import ftrack_api as local session
import ftrack_api
from utils import print_entity_head
#
session = ftrack_api.Session()

# ----------------------------------


def test_event(event):
    '''just a testing event'''

    # start of event procedure ----------------------------------
    for entity in event['data'].get('entities', []):
        if entity['entityType'] == 'task' and entity['action'] == 'update':

            print "\n\nevent script: {}".format(__file__)
            print_entity_head.print_entity_head(entity, session)

            # for k in task.keys():
            #     print k, task[k]
            # print '\n'
            # print task['assignments']

            for e in entity.keys():
                print '{0}: {1}'.format(e, entity[e])

    # end of event procedure ----------------------------------
