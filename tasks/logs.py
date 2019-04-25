
from invoke import task, run

import json
import pendulum

@task(
  help={
    'freshness': 'Interval over which to look at logs (default: "1h")',
  },
)
def lb(ctx, freshness='1h'):
  """Logs from the load balancer (ingress)"""
  output = json.loads(
    run("gcloud logging read 'resource.type=http_load_balancer'"
      " --format json"
      f" --freshness {freshness}",
        hide=True).stdout)

  for line in output[::-1]:
    time = pendulum.parse(line['timestamp'])
    req = line['httpRequest']
    print(" ".join([
      time.to_datetime_string(),
      req['requestMethod'],
      str(req['status']),
      req['responseSize'],
      req['requestUrl'],
      req['userAgent'],
      req['remoteIp'],
    ]))

@task
def logs(ctx):
  """Read the latest logs"""
  output = json.loads(
    run('gcloud logging read logName=projects/spaceshipearthprod/logs/pyspaceship --format json --freshness 1h --order asc', hide=True).stdout)
  for line in output:
    print(line['textPayload'].strip())

