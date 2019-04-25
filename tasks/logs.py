
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

@task
def logs(ctx):
  """Read the latest logs"""
  output = json.loads(
    run('gcloud logging read logName=projects/spaceshipearthprod/logs/pyspaceship --format json --freshness 1h --order asc', hide=True).stdout)
  for line in output:
    print(line['textPayload'].strip())

