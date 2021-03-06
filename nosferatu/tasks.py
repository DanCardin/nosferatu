import logging

from apscheduler.jobstores.base import JobLookupError
from . import cache, db
from .models import Node, Rule
from .node_utils import (
    find_nodes, change_node_status, get_node_status,
    BadIpException, CommunicationException, BadStatusException,
)
from .task_lock import task_lock

log = logging.getLogger()

def change_state(affected_node, field, thing):
    # If field is `None` the action is "unchanged"
    if field is not None:
        # Otherwise it means on or off
        action = 'OFF'
        if field:
            action = 'ON'

        ip = str(affected_node.ip_addr)
        mac = str(affected_node.mac_addr)

        if thing == 'RELAY':
            if affected_node.relay_status != field:
                with task_lock(key=mac, timeout=10):
                    status = change_node_status(ip, thing, action)
                db_update_relay(affected_node.id, status)

        elif thing == 'MOTION':
            if affected_node.motion_status != field:
                with task_lock(key=mac, timeout=10):
                    status = change_node_status(ip, thing, action)
                db_update_motion(affected_node.id, status)



def rules_poll():
    rules = Rule.query.filter_by(type='Event')

    # Get all the nodes we could reference below
    ids = set()
    for rule in rules:
        ids.add(rule.node)
        ids.add(rule.event_node)

    # Map node id to node object
    node_info = {}
    nodes = Node.query.filter(Node.id.in_(ids)) if ids else []
    for node in nodes:
        node_info[node.id] = node

    # For each rule
    for rule in rules:
        affected_node = node_info[rule.node]
        node_to_check = node_info[rule.event_node]
        if affected_node and node_to_check:
            # If `node_to_check` has the state of `event_node_state` then `affected_node`
            # should change ITS state to the value of `turn_on`
            if node_to_check.relay_status == rule.event_node_state:
                change_state(affected_node, rule.turn_on, 'RELAY')
            if node_to_check.motion_status == rule.event_node_state:
                change_state(affected_node, rule.turn_motion_on, 'MOTION')

#######################################
# Direct Node Communication
#######################################
def get_node_status_task(node_id):
    node = Node.query.filter_by(id=node_id).first()
    ip_str = str(node.ip_addr)
    mac = str(node.mac_addr)

    with task_lock(key=mac, timeout=10):
        try:
            status = get_node_status(ip_str)
        except (BadIpException, CommunicationException, BadStatusException) as e:
            print(e)
            status = ('Erroar', 'Erroar', 'Erroar')

    try:
        led_status, motion_status, relay_status, motion_timeout = status
        db_update_relay(node_id, relay_status)
    except:
        led_status, motion_status, relay_status, motion_timeout = 'Erroar', 'Erroar', 'Erroar', 'Erroar'

    try:
        motion_timeout = int(motion_timeout) / 1000
    except:
        motion_timeout = 5

    return {
        'led': led_status,
        'relay': relay_status,
        'motion': motion_status,
        'motionTimeout': motion_timeout,
    }


def test_node_task(args):
    if args['action'] == 'start':
        test = 'START'
    else:
        test = 'STOP'

    with task_lock(key=args['mac'], timeout=15):
        change_node_status(args['ip'], "TEST", test)


def find_nodes_task():
    return find_nodes()


def toggle_node_task(node_id):
    node = Node.query.filter_by(id=node_id).first()

    ip_str = str(node.ip_addr)
    mac = str(node.mac_addr)

    with task_lock(key=mac, timeout=15):
        status = change_node_status(ip_str, "RELAY", "TOGGLE")

    db_update_relay(node_id, status)


def change_motion_task(node_id, input):
    node = Node.query.filter_by(id=node_id).first()

    ip_str = str(node.ip_addr)
    mac = str(node.mac_addr)

    status = input['motion'].upper()

    with task_lock(key=mac, timeout=15):
        status_reply = change_node_status(ip_str, "MOTION", status)

    db_update_motion(node_id, status_reply)

    motion_timeout = input.get('motion_timeout')
    if motion_timeout:
        print(motion_timeout, str(motion_timeout))
        status_reply = change_node_status(ip_str, "TIMEOUT", motion_timeout)



#######################################
# Database calls
#######################################
from . import schedule


def add_node_task(node, user_id):
    try:
        if not node['name']:
            raise Exception("Invalid Name")

        node = Node(
            name=node['name'],
            ip_addr=node['ip'],
            mac_addr=node['mac'],
            user_id=user_id,
        )
        db.session.add(node)
        db.session.commit()
        return {'id': node.id}
    except Exception as e:
        log.exception(e)


def get_nodes_task():
    nodes = Node.query.all()
    result = {}
    for i, node in enumerate(nodes):
        result['id{}'.format(i)] = node.id
    return result


def get_node_task(node_id):
    node = Node.query.get(node_id)
    return node.to_json()


def add_rule_task(node_id, rule):
    log.debug(rule)

    try:
        # Validate the zipcode
        if rule.get('sched_type') == 'auto':
            zip_code = rule.get('zip_code')
            if zip_code is not None:
                for digit in zip_code:
                    try:
                        zip_code = int(digit)
                    except ValueError:
                        zip_code = None
                if not zip_code:
                    raise Exception("Error no Zipcode")
        else:
            zip_code = None

        def change_map(value):
            return {
                'on': True,
                'off': False,
                'unchanged': None,
            }[value]

        rule = Rule(
            name=rule['name'],
            type=rule['type'],
            turn_on=change_map(rule['turn_on']),
            turn_motion_on=change_map(rule['turn_motion_on']),
            days='.'.join(rule['days']),

            sched_type=rule.get('sched_type'),
            sched_hour=rule.get('hour'),
            sched_minute=rule.get('minute'),
            sched_zip_code=zip_code,
            sched_time_of_day=rule.get('time_of_day'),

            event_node=rule.get('event_node'),
            event_node_state=rule.get('event_node_status'),

            node=node_id,
        )
        db.session.add(rule)
        db.session.commit()

        if rule.type == 'Schedule':
            from .scheduler import add_sched_rule
            add_sched_rule(rule, schedule)

        print(rule.id)

        return {'id': rule.id}
    except Exception as e:
        log.exception(e)


def delete_node_task(node_id):
    try:
        node = Node.query.get(node_id)
        if node.rules:
            for rule in node.rules:
                db.session.delete(rule)

        rules = Rule.query.filter_by(event_node=node_id).delete()

        db.session.delete(node)
        db.session.commit()
        return {'result': node.id}
    except:
        raise
    return {'result': False}


def get_all_rules_task(node_id):
    rules = Rule.query.filter_by(node=node_id).all()

    if rules:
        result = {}
        for i, rule in enumerate(rules):
            result['id{}'.format(i)] = rule.id
        return result
    return {}


def get_rule_task(node_id, rule_id):
    rule = Rule.query.filter_by(node=node_id, id=rule_id).first()
    if rule:
        if rule.type == 'Schedule':
            if rule.sched_type == 'manual':
                print(rule.sched_hour)
                info = 'at {}:{:02} {AMPM}'.format(
                    ((rule.sched_hour + 11) % 12) + 1,
                    rule.sched_minute,
                    AMPM='AM' if rule.sched_hour < 12 else 'PM'
                )
            else:
                info = rule.sched_time_of_day

        elif rule.type == 'Event':
            info = 'when `{node}` is {status}'.format(
                node=Node.query.get(rule.event_node).name,
                status='on' if rule.event_node_state else 'off'
            )
        else:
            info = rule.sched_type

        turn_on = []
        if rule.turn_on is not None:
            turn_on.append('Turn light {}'.format('on' if rule.turn_on else 'off'))
        else:
            turn_on.append('Light unchanged')
        if rule.turn_motion_on is not None:
            turn_on.append('Turn motion {}'.format('on' if rule.turn_motion_on else 'off'))
        else:
            turn_on.append('Motion unchanged')

        return {
            'id': rule.id,
            'name': rule.name,
            'turn_on': turn_on,
            'days': [day.title() for day in rule.days.split('.')],
            'type': rule.type,
            'info': info,
        }


def delete_rule_task(node_id, rule_id):
    try:
        rule = Rule.query.filter_by(node=node_id, id=rule_id).first()
        if rule:
            db.session.delete(rule)
            db.session.commit()

            try:
                schedule.remove_job(str(rule.id))
                schedule.print_jobs()
            except JobLookupError:
                pass
            return {'result': rule.id}
    except:
        raise
    return {'result': False}


def db_update_status(node_id, status, status_type=None):
    if status_type is None:
        raise Exception("Status type can't be None")
    if status not in ['On', 'Off']:
        return

    status_map = {
        'On': True,
        'Off': False,
    }
    current_status = status_map[status]

    node = Node.query.get(node_id)
    setattr(node, status_type, current_status)
    db.session.commit()


def db_update_relay(node_id, status):
    db_update_status(node_id, status, status_type='relay_status')


def db_update_motion(node_id, status):
    db_update_status(node_id, status, status_type='motion_status')
