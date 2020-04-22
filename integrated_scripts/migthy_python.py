import json
import time
import os

l1 = os.getenv("EXECUTOR_CONFIG_L1")
l2 = os.getenv("EXECUTOR_CONFIG_L2","incognito")
l3 = os.getenv("EXECUTOR_CONFIG_L3","cobol")
print(json.dumps(dict(msg="Soy Java :)", by=l1)))
time.sleep(1)
print(json.dumps(dict(msg="Soy Java, en serio", by=l2)))
time.sleep(2)
print(json.dumps(dict(msg="Ok, lo admito, soy COBOL", by=l3)))
