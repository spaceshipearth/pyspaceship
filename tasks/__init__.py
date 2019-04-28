from invoke import Collection

from . import run, image, k8s, logs, rq

ns = Collection()
ns.add_collection(run)
ns.add_collection(image)
ns.add_collection(k8s)
ns.add_collection(logs)
ns.add_collection(rq)
