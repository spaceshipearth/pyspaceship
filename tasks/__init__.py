from invoke import Collection

from tasks import run, image, k8s, logs

ns = Collection()
ns.add_collection(run)
ns.add_collection(image)
ns.add_collection(k8s)
ns.add_collection(logs)
