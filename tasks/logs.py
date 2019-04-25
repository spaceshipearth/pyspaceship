
from invoke import task, run

import json
import pendulum

@task(
  help={
    'freshness': 'Interval over which to look at logs (default: "1h")',
    'agent': 'Print the user agent',
  },
)
def lb(ctx, freshness='1h', agent=False):
  """Logs from the load balancer (ingress)"""
  output = json.loads(
    run("gcloud logging read 'resource.type=http_load_balancer'"
      " --format json"
      f" --freshness {freshness}",
        hide=True).stdout)

  for line in output[::-1]:
    try:
      time = pendulum.parse(line['timestamp'])
      req = line['httpRequest']
      status = str(req['status']) if 'status' in req else '???'

      parts = [
        time.to_datetime_string(),
        req['remoteIp'],
        req['requestMethod'],
        status,
        req['responseSize'] if 'responseSize' in req else '0',
        req['requestUrl'],
      ]

      if agent:
        parts.append(req['userAgent'])

      print(" ".join(parts))
    except Exception as e:
      print(f"Invalid log line {line}: {e}")

@task(
  default=True,
  help={
    'freshness': 'Interval over which to look at logs (default: "1h")',
  }
)
def container(ctx, freshness='1h'):
  """Logs from our containers"""
  log_filter = ' AND '.join([
    'resource.type=container',
    'resource.labels.namespace_id=default',
    'resource.labels.container_name=pyspaceship',
  ])

  cmd = f'gcloud logging read "{log_filter}" --format json --freshness {freshness}'

  output = json.loads(run(cmd, hide=True).stdout)
  for line in output[::-1]:
    """
    {'insertId': 'ibe8vife9ti4i', 'labels': , 'logName': 'projects/spaceshipearthprod/logs/pyspaceship', 'receiveTimestamp': '2019-04-25T18:00:03.509676329Z', 'resource': , 'severity': 'INFO', 'textPayload': '10.128.2.1 - - [25/Apr/2019:17:59:58 +0000] "GET / HTTP/1.1" 200 4627 "-" "GoogleHC/1.0"\n', 'timestamp': '2019-04-25T17:59:58.560663349Z'}
"""
    try:
      # skip health checks
      if 'textPayload' in line:
        msg = line['textPayload']
      elif 'jsonPayload' in line:
        msg = line['jsonPayload']['message']
      else:
        msg = "<no message>"

      if 'GoogleHC' in msg or 'kube-probe' in msg:
        continue

      time = pendulum.parse(line['timestamp'])

      parts = [
        time.to_datetime_string(),
        line['severity'],
        msg,
      ]

      print(" ".join(parts))
    except Exception as e:
      print(f"Invalid log line {line}: {e}")
