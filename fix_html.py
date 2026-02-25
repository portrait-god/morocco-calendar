import sys

with open("templates/index.html", "r") as f:
    lines = f.readlines()

out = []
for line in lines:
    if "        </div>" in line and "    </div>" in lines[lines.index(line)+1] and "timeline-labels" in "".join(lines[lines.index(line):lines.index(line)+5]):
        continue
    out.append(line)

with open("templates/index.html", "w") as f:
    f.writelines(out)
