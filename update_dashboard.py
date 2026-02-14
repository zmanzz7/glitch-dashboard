#!/usr/bin/env python3
"""Quick dashboard updater — call with actions like:
  python3 update_dashboard.py email sent user@example.com "Company Name" "Category"
  python3 update_dashboard.py email bounced user@example.com
  python3 update_dashboard.py email replied user@example.com
  python3 update_dashboard.py timeline "Event description" type
  python3 update_dashboard.py product "Name" platform price status url
  python3 update_dashboard.py revenue source amount
  python3 update_dashboard.py mrr current clients
  python3 update_dashboard.py push  (git commit + push)
"""
import json, sys, subprocess
from datetime import datetime

DATA = '/Users/glitch/.openclaw/workspace/dashboard/data.json'

def load():
    with open(DATA) as f:
        return json.load(f)

def save(d):
    d['lastUpdated'] = datetime.now().isoformat()
    with open(DATA, 'w') as f:
        json.dump(d, f, indent=2)

def push():
    subprocess.run(['git', 'add', '-A'], cwd='/Users/glitch/.openclaw/workspace/dashboard')
    subprocess.run(['git', 'commit', '-m', f'Dashboard update {datetime.now().strftime("%H:%M")}'], cwd='/Users/glitch/.openclaw/workspace/dashboard')
    subprocess.run(['git', 'push'], cwd='/Users/glitch/.openclaw/workspace/dashboard')

if __name__ == '__main__':
    action = sys.argv[1]
    d = load()
    
    if action == 'email':
        status = sys.argv[2]
        email = sys.argv[3]
        if status == 'sent':
            company = sys.argv[4] if len(sys.argv) > 4 else ''
            category = sys.argv[5] if len(sys.argv) > 5 else ''
            d['outreach']['emails'].append({
                'to': email, 'company': company, 'category': category,
                'sentAt': datetime.now().isoformat(), 'status': 'sent'
            })
            d['outreach']['totalSent'] += 1
            d['outreach']['delivered'] += 1
        else:
            for e in d['outreach']['emails']:
                if e['to'] == email:
                    e['status'] = status
                    break
            if status == 'bounced':
                d['outreach']['bounced'] += 1
                d['outreach']['delivered'] -= 1
            elif status == 'replied':
                d['outreach']['replied'] += 1
            elif status == 'opened':
                d['outreach']['opened'] += 1
    
    elif action == 'timeline':
        event = sys.argv[2]
        etype = sys.argv[3] if len(sys.argv) > 3 else 'milestone'
        d['timeline'].append({
            'date': datetime.now().strftime('%Y-%m-%d %H:%M'),
            'event': event, 'type': etype
        })
    
    elif action == 'revenue':
        source = sys.argv[2]
        amount = float(sys.argv[3])
        d['revenue']['total'] += amount
        d['revenue'][source.lower()] = d['revenue'].get(source.lower(), 0) + amount
        for b in d['revenue']['breakdown']:
            if b['source'].lower() == source.lower():
                b['amount'] += amount
    
    elif action == 'mrr':
        d['mrr']['current'] = float(sys.argv[2])
        d['mrr']['clients'] = int(sys.argv[3])
    
    elif action == 'push':
        save(d)
        push()
        print('Pushed')
        sys.exit(0)
    
    save(d)
    print(f'Updated: {action}')
    
    if '--push' in sys.argv:
        push()
        print('Pushed')
