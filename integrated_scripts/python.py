import os
import json
print(json.dumps(dict(msg="Soy python", color="goldenrod")))

fail = os.getenv("FAIL", None)
if fail:
    exit(1)